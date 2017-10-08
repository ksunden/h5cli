import h5py
import os
import re

class NewH5Explorer(object):
    def __init__(self, h5_obj):
        self.__filename = h5_obj.file.filename
        self.__file = h5_obj
        self.__working_dir = h5_obj.name

        self.__dir_queue = list()

    @staticmethod
    def from_file(filename, mode="r"):
        h5_file = h5py.File(filename, mode)
        return NewH5Explorer(h5_file)

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

    @property
    def raw(self):
        return self.__file

    @property
    def datasets(self):
        target_dir = self.__check_group(None)

        return [k for k, v in self.__file[target_dir].items()
                if isinstance(v, h5py.Dataset)]
    @property
    def groups(self):
        target_dir = self.__check_group(None)

        return [k for k, v in self.__file[target_dir].items()
                if isinstance(v, h5py.Group)]

    def __getitem__(self, path):
        result = self.__file[self.__get_absolute_path(path)]
        if isinstance(result, h5py.Dataset):
            return result
        return NewH5Explorer(result)

    def __delitem__(self, path):
        del self.__file[self.__get_absolute_path(path)]

    def dataset(self, path):
        return self.__file[self.__check_dataset(path)]

    def group(self, path):
        return self.__file[self.__check_group(path)]
