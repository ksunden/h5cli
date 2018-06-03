#! /usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "VERSION")) as f:
    version = f.read().strip()

extra_files = []
extra_files.append(os.path.join(here, "CONTRIBUTORS"))
extra_files.append(os.path.join(here, "LICENSE"))
extra_files.append(os.path.join(here, "README.md"))
extra_files.append(os.path.join(here, "VERSION"))

setup(
    name="h5cli",
    packages=find_packages(),
    package_data={"": extra_files},
    install_requires=["h5py>=2.7.0", "cmd2>=0.7.5", "tree_format"],
    extras_require={"dev": ["black", "pre-commit"]},
    version=version,
    description="bash-like iterface for HDF5 files",
    url="https://github.com/ksunden/h5cli",
    author="Kyle Sunden",
    license="MIT",
    entry_points={"console_scripts": ["h5cli=src.h5cli.cli:main"]},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
)
