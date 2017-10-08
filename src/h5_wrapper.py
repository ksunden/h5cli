import h5py
import os
import re

class H5Explorer(object):
    def __init__(self, filename, mode="r"):
        self.__filename = filename
        self.__file = h5py.File(filename, mode)
        self.__working_dir = "/"

        self.__dir_queue = list()

    def __get_absolute_path(self, path):
        if path is None:
            path = self.__working_dir
        elif not path.startswith("/"):
            path = "/".join(self.__working_dir.split("/") + path.split("/"))

        return re.sub("/+", "/", os.path.normpath(path))

    def __check_group(self, path):
        path = self.__get_absolute_path(path)
        if path not in self.__file:
            raise ValueError("Directory {} does not exist.".format(path))
        elif not isinstance(self.__file[path], h5py.Group):
            raise ValueError("{} exists, but is not a directory".format(path))
        else:
            return path

    def __check_dataset(self, path):
        path = self.__get_absolute_path(path)
        if path not in self.__file:
            raise ValueError("Dataset {} does not exist.".format(path))
        elif not isinstance(self.__file[path], h5py.Dataset):
            raise ValueError("{} exists, but is not a dataset".format(path))
        return path

    @property
    def working_dir(self):
        return self.__working_dir

    @property
    def filename(self):
        return self.__filename

    def change_dir(self, new_dir="/"):
        new_dir = self.__check_group(new_dir)
        self.__working_dir = new_dir

    def push_dir(self, new_dir):
        new_dir = self.__get_absolute_path(new_dir)

        self.__dir_queue.append(self.__working_dir)
        self.change_dir(new_dir)

    def pop_dir(self):
        if len(self.__dir_queue) == 0:
            raise IndexError("Cannot pop a directory before pushing one.")
        self.__working_dir = self.__dir_queue.pop()


    def __call__(self, path=None):
        if path is None:
            return self.__file[self.__working_dir]
        else:
            return self.__file[self.__get_absolute_path(path)]

    def dataset(self, path):
        return self.__file[self.__check_dataset(path)]

    def group(self, path):
        return self.__file[self.__check_group(path)]


    def list_groups(self, target_dir=None):
        target_dir = self.__check_group(target_dir)

        return [k for k, v in self.__file[target_dir].items()
                if isinstance(v, h5py.Group)]

    def list_datasets(self, target_dir=None):
        target_dir = self.__check_group(target_dir)

        return [k for k, v in self.__file[target_dir].items()
                if isinstance(v, h5py.Dataset)]

    def create_group(self, group_dir):
        group_dir = self.__get_absolute_path(group_dir)
        self.__file.create_group(group_dir)

    def delete_dataset(self, target_path):
        target_path = self.__check_dataset(target_path)
        del self.__file[target_path]

    def delete_group(self, group_dir):
        group_dir = self.__check_group(group_dir)
        del self.__file[group_dir]
