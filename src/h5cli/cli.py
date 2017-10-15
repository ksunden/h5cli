from cmd2 import Cmd, options, make_option
from . import explorer
import os
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
        make_option('-n', '--number',action='store_true', help='print number of elements, rather than full shape'),
        make_option('-m', '--maxshape',action='store_true', help='print maximum shape, rather than current shape')
    ])
    def do_shape(self, args, opts=None):
        """Print the shape of a dataset."""
        if opts.number:
            print(self.explorer[args[0]].size)
            return False

        if opts.maxshape:
            print(self.explorer[args[0]].maxshape)
            return False

        print(self.explorer[args[0]].shape)
        return False

    def do_exit(self, args):
        return True


def main():
    c = CmdApp()
    if len(sys.argv) > 1:
        c.onecmd('load ' + sys.argv[1])
        c.postcmd(False, "")
        sys.argv[1] = ""
    c.cmdloop()
