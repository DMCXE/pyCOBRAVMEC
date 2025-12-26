#!/usr/bin/env python3
import json
import os
import pathlib
import sys

if sys.platform == "darwin":
    from distutils import sysconfig

    vars = sysconfig.get_config_vars()
    vars["LDSHARED"] = vars["LDSHARED"].replace("-bundle", "-dynamiclib")

from skbuild import setup

fldr_path = pathlib.Path(__file__).parent.absolute()
root_path = fldr_path.parent
config_path = root_path / "cmake_config_file.json"

cmake_args = []
if config_path.exists():
    with open(config_path) as fp:
        data = json.load(fp)
        cmake_args = data.get("cmake_args", [])


class EmptyListWithLength(list):
    def __len__(self):
        return 1


os.chdir(root_path)

setup(
    name="cobravmec",
    version="0.1.0",
    packages=["cobravmec"],
    package_dir={"": "python"},
    install_requires=["f90wrap", "numpy>=1.21"],
    python_requires=">=3.9",
    ext_modules=EmptyListWithLength(),
    description="Python wrapper for COBRAVMEC",
    cmake_args=cmake_args,
    cmake_source_dir=".",
)
