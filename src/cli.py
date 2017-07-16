from cmd2 import Cmd, options, make_option
import h5_wrapper
import sys
import os

class CmdApp(Cmd):

    def precmd(self, line):
        if not line.startswith('load') and (line.endswith('.h5') or line.endswith('.hdf5')):
            line = 'load ' + line
        return line

    def do_ls(self, args, opts=None):
        if len(args.strip()) > 0: 
            for g in self.explorer.list_groups(args):
                print(g+"/")
            
            for ds in self.explorer.list_datasets(args):
                print(ds)
        else:
            for g in self.explorer.list_groups():
                print(g+"/")
            
            for ds in self.explorer.list_datasets():
                print(ds)

    def do_cd(self, args, opts=None):
        if len(args) == 0:
            args = '/'
        self.explorer.change_dir(args)

    def do_pwd(self, args, opts=None):
        print(self.explorer.working_dir)

    def do_pushd(self, args, opts=None):
        self.explorer.push_dir(args)

    def do_popd(self, args, opts=None):
        self.explorer.pop_dir()
        self.do_pwd(None)

    def do_mkdir(self, args, opts=None:
        raise NotImplementedError

    def do_rmdir(self, args, opts=None:
        raise NotImplementedError

    def do_rm(self, args, opts=None:
        raise NotImplementedError

    def do_cat(self, args, opts=None:
        raise NotImplementedError

    def do_head(self, args, opts=None:
        raise NotImplementedError

    def do_tail(self, args, opts=None:
        raise NotImplementedError

    def do_cp(self, args, opts=None:
        raise NotImplementedError

    def do_mv(self, args, opts=None:
        raise NotImplementedError

    def do_clear(self, args):
        os.system('clear')
        
    def do_exit(self, args):
        return True


if __name__ == '__main__':
    c = CmdApp()
    c.cmdloop()
