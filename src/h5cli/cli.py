from cmd2 import Cmd, options
from optparse import make_option
from . import explorer
import h5py
import os
import tree_format
import sys


class CmdApp(Cmd):

    def __init__(self):
        Cmd.shortcuts.update({'!': 'bang', '$': 'shell'})
        Cmd.__init__(self)
        self.abbrev = True
        self.prompt = '[] > '
        self.explorer = None
        self.dir_stack = list()

    def postcmd(self, stop, line):
        self.prompt = '[] > '
        if self.explorer:
            self.prompt = '[{}: {}/] {} '.format(
                os.path.basename(self.explorer.filename),
                os.path.basename(self.explorer.working_dir),
                '>' if self.explorer.raw.mode == 'r' else '+>')
        return stop

    def do_source(self, args):
        Cmd.do_load(self, args)

    @options([
        make_option('-m', '--mode', type=str, default='r', help='File mode ([r]ead, [w]rite, [a]ppend)')
    ])
    def do_load(self, args, opts=None):
        """Load an hdf5 file.

        Usage: load [-m mode] file [path]
        """
        path = '/'
        if len(args) > 1:
            path = args[1]
        if len(args) == 0:
            args = [self.explorer.filename]
            path = self.explorer.working_dir
            self.explorer.close()

        self.explorer = explorer.H5Explorer.from_file(args[0], mode=opts.mode)
        self.explorer.change_dir(path)

    def do_ls(self, args, opts=None):
        if len(args.strip()) > 0:
            dest = self.explorer[args]
        else:
            dest = self.explorer

        for g in dest.groups:
            print(g + "/")

        for ds in dest.datasets:
            print(ds)

    def do_cd(self, args, opts=None):
        if len(args) == 0:
            args = '/'
        self.explorer.change_dir(args)

    def do_pwd(self, args, opts=None):
        print(self.explorer.working_dir)

    def do_pushd(self, args, opts=None):
        self.dir_stack.append(self.explorer.working_dir)
        self.explorer.change_dir(args)

    def do_popd(self, args, opts=None):
        dest = self.dir_stack.pop()
        self.explorer.change_dir(dest)
        self.do_pwd(None)

    def do_mkdir(self, args, opts=None):
        h5_grp = self.explorer[args + "/.."].raw
        h5_grp.create_group(args)

    def do_rmdir(self, args, opts=None):
        raise NotImplementedError

    def do_rm(self, args, opts=None):
        raise NotImplementedError

    def do_cat(self, args, opts=None):
        raise NotImplementedError

    def do_head(self, args, opts=None):
        raise NotImplementedError

    def do_tail(self, args, opts=None):
        raise NotImplementedError

    @options([
        make_option('-f', '--force', action='store_const', const='f', dest='interaction', help='if  an existing destination file cannot be opened, remove it and try again (overrides a previous -i or -n option)'),
        make_option('-i', '--interactive', action='store_const', const='i', dest='interaction', help='prompt before overwrite (overrides a previous -f or -n option)'),
        make_option('-n', '--no-clobber', action='store_const', const='n', dest='interaction', default='i', help='do not overwrite an existing file (overrides a previous -f or -i option)'),
        make_option('-R', '-r', '--recursive', action='store_true', help='copy groups recursively'),
        make_option('-t', '--target-group', type=str, dest='target', help='copy all SOURCE arguments into GROUP'),
        ])
    def do_cp(self, args, opts=None):
        if opts.target:
            dest = self.explorer.group(opts.target)
            source = args
        else:
            dest = args[-1]
            source = args[:-1]
            try:
                dest = self.explorer.group(dest)
            except ValueError:
                dest = self.explorer.get_absolute_path(dest)
                # Destination is not an existing group, keep string

        for src in source:
            try:
                self.explorer.dataset(src)
                src = self.explorer.get_absolute_path(src)
            except ValueError as e:
                if 'not exist' in e.args[0]:
                    print("cp: omitting '{}': No such dataset or group".format(src))
                    continue
                elif not opts.recursive:
                    print("cp: -r not specified; omitting group '{}'".format(src))
                    continue
                else:
                    src = self.explorer.group(src)
            try:
                self.explorer.raw.copy(src, dest)
            except ValueError:
                force = opts.interaction == 'f'
                d = dest
                if isinstance(dest, h5py.Group):
                    s = src
                    if not isinstance(src, (str, bytes, os.PathLike)):
                        s = src.name
                    d = '/'.join((dest.name, os.path.basename(s)))
                if opts.interaction == 'i':
                    inp = input("cp: overwrite '{}'? ".format(d))
                    force = inp.lower() in ['y', 'yes']
                if force:
                    del self.explorer[d]
                    self.explorer.raw.copy(src, dest)


    def do_mv(self, args, opts=None):
        raise NotImplementedError

    def do_su(self, args, opts=None):
        self.do_load('-ma')

    def do_sudo(self, args, opts=None):
        # guaranteed to be 'r' or 'r+' not 'w' which would be dangerous
        mode = self.explorer.raw.mode
        self.do_load('-ma')
        self.onecmd(str(args))
        self.do_load('-m'+mode)

    def do_bang(self, args, opts=None):
        if args.strip() == '!':
            print(self.history[-2])
            self.onecmd(self.history[-2])
        elif args.strip().isnumeric():
            print(self.history[-1 * int(args) - 1])
            self.onecmd(self.history[-1 * int(args) - 1])
        else:
            history = self.history.copy()
            history.reverse()
            for cmd in history:
                if cmd.startswith(args):
                    print(cmd)
                    self.onecmd(cmd)
                    return False
            raise ValueError("{}: event not found".format(args))

    def do_clear(self, args):
        os.system('clear')

    @options([
        make_option('-n', '--number',action='store_const', const='number', dest='kind', help='print number of elements, rather than full shape'),
        make_option('-m', '--maxshape',action='store_const', const='maxshape', dest='kind', help='print maximum shape, rather than current shape'),
        make_option('-c', '--chunks',action='store_const', const='chunks', dest='kind', help='print shape of chunks, rather than full shape'),
    ])
    def do_shape(self, args, opts=None):
        """Print the shape of a dataset."""
        if opts.kind == 'number':
            print(self.explorer[args[0]].size)

        elif opts.kind == 'maxshape':
            print(self.explorer[args[0]].maxshape)

        elif opts.kind == 'chunks':
            print(self.explorer[args[0]].chunks)

        else:
            print(self.explorer[args[0]].shape)

        return False

    @options([
        make_option('-a', '--axis', type=int, help='change length of a single axis, rather than the full shape'),
    ])
    def do_resize(self, args, opts=None):
        """Resize a dataset to a given shape.

        Usage:  resize [-a axis] path int ...
        """
        dataset = args[0]
        shape = tuple(int(x) for x in args[1:])
        if opts.axis is not None:
            if len(shape) != 1:
                raise ValueError('Expected exactly one integer when changing axis size')
            self.explorer[dataset].resize(shape[0], axis=opts.axis)
        else:
            self.explorer[dataset].resize(shape)


    @options([])
    def do_len(self, args, opts=None):
        print(self.explorer[args[0]].len())

    def do_exit(self, args):
        return True

    @options([
        make_option('-s', '--shape', action='store_true', help='print the shape of datasets')
    ])
    def do_tree(self, args, opts=None):
        """list contents of groups in a tree-like format."""
        global __groupcount
        global __datasetcount
        __groupcount = 0
        __datasetcount = 0

        def children(item):
            if isinstance(item, h5py.Dataset):
                return []
            else:
                return [i[1] for i in item.items()]

        def format(item):
            name = os.path.basename(item.name)
            if name == '':
                name = '/'
            if isinstance(item, h5py.Dataset):
                if opts.shape:
                    name = name + '  ' + str(item.shape)
                global __datasetcount
                __datasetcount += 1
            elif isinstance(item, h5py.Group):
                global __groupcount
                __groupcount += 1
            return name

        if len(args) == 0:
            args.append('')
        group = self.explorer.group(args[0])
        tree_format.print_tree(group, format, children)
        print('{} groups, {} datasets'.format(__groupcount - 1, __datasetcount))

    @options([])
    def do_dtype(self, args, opts=None):
        """Print the data type of a dataset."""
        print(self.explorer[args[0]].dtype)

    @options([
        make_option('-o', '--opts', action='store_true', help='print compression options.')
        ])
    def do_comp(self, args, opts=None):
        """Print the compression filter of a dataset."""
        print(self.explorer[args[0]].compression)
        if opts.opts:
            print(self.explorer[args[0]].compression_opts)


def main():
    c = CmdApp()
    if len(sys.argv) > 1:
        c.onecmd('load ' + sys.argv[1])
        c.postcmd(False, "")
        sys.argv[1] = ""
    c.cmdloop()
    c.explorer.close()
