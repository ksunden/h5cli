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
        if self.explorer:
            self.prompt = '[{}: {}/] > '.format(
                os.path.basename(self.explorer.filename),
                os.path.basename(self.explorer.working_dir))
        return stop

    def do_source(self, args):
        Cmd.do_load(self, args)

    @options([
        make_option('-m', '--mode', type=str, default='r', help='File mode ([r]ead, [w]rite, [a]ppend)')
    ])
    def do_load(self, args, opts=None):
        self.explorer = explorer.H5Explorer.from_file(args[0], mode=opts.mode)

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

    def do_cp(self, args, opts=None):
        raise NotImplementedError

    def do_mv(self, args, opts=None):
        raise NotImplementedError

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
