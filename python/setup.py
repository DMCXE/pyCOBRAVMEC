#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys
import shlex

if sys.platform == "darwin":
    from distutils import sysconfig

    vars = sysconfig.get_config_vars()
    vars["LDSHARED"] = vars["LDSHARED"].replace("-bundle", "-dynamiclib")

from skbuild import setup


def _fix_duplicate_rpaths(so_file):
    """Remove duplicate LC_RPATH entries from a Mach-O binary on macOS."""
    if sys.platform != "darwin" or not os.path.exists(so_file):
        return
    try:
        # Get current rpaths using otool
        result = subprocess.run(
            ["otool", "-l", so_file],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.split("\n")
        rpaths = []
        for i, line in enumerate(lines):
            if "cmd LC_RPATH" in line:
                # The path is 2 lines after the cmd line
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "path " in lines[j]:
                        path = lines[j].split("path ")[1].split(" (offset")[0].strip()
                        rpaths.append(path)
                        break

        # Find duplicates
        seen = set()
        duplicates = []
        for rpath in rpaths:
            if rpath in seen:
                duplicates.append(rpath)
            else:
                seen.add(rpath)

        # Remove duplicate rpaths (keep first occurrence)
        for dup in duplicates:
            subprocess.run(
                ["install_name_tool", "-delete_rpath", dup, so_file],
                capture_output=True,
                check=False,  # May fail if already removed
            )
            print(f"Removed duplicate RPATH: {dup}")
    except Exception as e:
        print(f"Warning: Failed to fix rpaths in {so_file}: {e}")

fldr_path = pathlib.Path(__file__).parent.absolute()
root_path = fldr_path.parent
config_path = root_path / "cmake_config_file.json"

cmake_args = []
if config_path.exists():
    with open(config_path) as fp:
        data = json.load(fp)
        cmake_args = data.get("cmake_args", [])

rpath_args = [
    "-DCMAKE_SKIP_RPATH=ON",
    "-DCMAKE_INSTALL_RPATH=",
    "-DCMAKE_BUILD_RPATH=",
    "-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=FALSE",
    "-DCMAKE_MACOSX_RPATH=OFF",
]
for arg in rpath_args:
    if arg not in cmake_args:
        cmake_args.append(arg)


class EmptyListWithLength(list):
    def __len__(self):
        return 1


def _strip_rpath_flags(flags):
    if not flags:
        return flags
    parts = shlex.split(flags)
    cleaned = []
    skip_next = False
    for part in parts:
        if skip_next:
            skip_next = False
            continue
        if part == "-Wl,-rpath":
            skip_next = True
            continue
        if part.startswith("-Wl,-rpath,"):
            continue
        cleaned.append(part)
    return " ".join(cleaned)


# Clean rpath flags from all relevant environment variables
for env_var in ["LDFLAGS", "LDSHARED", "CFLAGS", "FFLAGS", "FCFLAGS"]:
    flags = os.environ.get(env_var, "")
    cleaned = _strip_rpath_flags(flags)
    if cleaned != flags:
        os.environ[env_var] = cleaned

# Also add cmake flags to forcibly disable rpath at cmake level
if "-DCMAKE_SKIP_INSTALL_RPATH=ON" not in cmake_args:
    cmake_args.append("-DCMAKE_SKIP_INSTALL_RPATH=ON")
if "-DCMAKE_SKIP_BUILD_RPATH=ON" not in cmake_args:
    cmake_args.append("-DCMAKE_SKIP_BUILD_RPATH=ON")

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
