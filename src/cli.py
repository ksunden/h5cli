from cmd2 import Cmd, options, make_option
import h5_wrapper
import sys

class CmdApp(Cmd):

    def do_ls(self, args, opts=None):
        for g in self.explorer.list_groups():
            print(g+"/")
        
        for ds in self.explorer.list_datasets():
            print(ds)

    def do_cd(self, args, opts=None):
        if len(args) == 0:
            args = '/'
        self.explorer.change_dir(args)

    def do_load(self, args, opts=None):
        print("Loading "+ args)
        self.explorer = h5_wrapper.H5Explorer(args)

    def do_pwd(self, args, opts=None):
        print(self.explorer.working_dir)

    def precmd(self, line):
        if not line.startswith('load') and (line.endswith('.h5') or line.endswith('.hdf5')):
            line = 'load ' + line
        return line

    def do_exit(self, args):
        return True

if __name__ == '__main__':
    c = CmdApp()
    c.cmdloop()
