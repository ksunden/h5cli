import h5py


class H5Explorer(object):
    def __init__(self, filename, mode="r"):
        self.__file = h5py.File(filename, mode)
        self.__working_dir = "/"

        self.__dir_queue = list()

    def __get_absolute_path(self, path):
        if not path.startswith("/"):
            return "/".join(self.__working_dir.split("/") + path.split("/"))
        else:
            return path

    @property
    def working_dir(self):
        return self.__working_dir

    def change_dir(self, new_dir="/"):
        new_dir = self.__get_absolute_path(new_dir)

        if new_dir in self.__file:
            self.__working_dir = new_dir
        else:
            raise ValueError("Directory {} does not exist.".format(new_dir))

    def push_dir(self, new_dir):
        self.__dir_queue.append(self.__working_dir)
        self.change_dir(new_dir)

    def pop_dir(self):
        if len(self.__dir_queue) == 0:
            raise IndexError("Cannot pop a directory before pushing one.")
        self.__working_dir = self.__dir_queue.pop()

    def list_groups(self):
        return [ k for k, v in self.__file[self.__working_dir].items()
                 if isinstance(v, h5py.Group) ]

    def list_datasets(self):
        return [ k for k, v in self.__file[self.__working_dir].items()
                 if isinstance(v, h5py.Dataset) ]

    def create_group(self, group_dir):
        group_dir = self.__get_absolute_path(group_dir)
        self.__file.create_group(group_dir)
