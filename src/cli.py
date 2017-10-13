#!/usr/bin/env python3
from cmd2 import Cmd, options, make_option
from . import explorer
import os


class CmdApp(Cmd):

    def __init__(self):
        Cmd.shortcuts.update({'!': 'bang', '$': 'shell'})
        Cmd.__init__(self)
        self.abbrev = True
        self.prompt = '[] > '
        self.explorer = None
        self.dir_stack = list()

    def precmd(self, line):
        if not line.startswith('load') and \
           (line.endswith('.h5') or line.endswith('.hdf5')):
            line = 'load ' + line
        return line

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
            self.onecmd(self.history[-2])
        elif args.strip().isnumeric():
            print(self.history[-1 * int(args) - 1])
            self.onecmd(self.history[-1 * int(args) - 1])
        else:
            history = self.history.copy()
            history.reverse()
            for cmd in history:
                if cmd.startswith(args):
                    self.onecmd(cmd)
                    return False
            raise ValueError("{}: event not found".format(args))

    def do_clear(self, args):
        os.system('clear')

    def do_exit(self, args):
        return True


def main():
    c = CmdApp()
    c.cmdloop()


if __name__ == '__main__':
    main()
