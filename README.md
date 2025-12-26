# Now it is very experimental and incomplete, but it works for basic use cases.

# pyCOBRAVMEC

Python bindings for COBRAVMEC using a compiled Fortran extension built via
CMake + scikit-build (f90wrap + f2py). 

The `COBRAVMEC` and `LIBSTELL_mini` borrowed from https://github.com/PrincetonUniversity/STELLOPT .The `cmake` build system used here is borrowed from https://github.com/hiddenSymmetries/VMEC2000. 

## Requirements

- A Fortran compiler (gfortran or ifort).
- NetCDF C + Fortran libraries.
- CMake, Ninja, f90wrap, NumPy.
- Optional: netCDF4 (Python) for in-memory `wout` loading.
- Optional: matplotlib for plotting helpers.

## Build and Install

Install the Python package (this builds `libstell_mini`, `cobravmec`, and
the `_cobravmec` extension):

```
/path/to/python -m pip install ./python --no-build-isolation
```

The build uses `cmake_config_file.json` for CMake
configuration. Example:

```json
{
  "cmake_args": [
    "-DCMAKE_Fortran_COMPILER=gfortran",
    "-DNETCDF_INC_PATH=/path/to/netcdf/include",
    "-DNETCDF_LIB_PATH=/path/to/netcdf/lib"
  ]
}
```

## Usage

### Class-based workflow (recommended)

```python
from cobravmec import CobraRunner, CobraPlotter

runner = CobraRunner(
    k_w=3,
    kth=1,
    l_geom_input=True,
    l_tokamak_input=False,
    init_zeta=[0.0, 10.0, 20.0],
    init_theta=[0.0, 15.0, 30.0],
    surfaces=[5, 10, 15],
)

results = runner.run(extension="example")
runner.write_output()  # writes cobra_grate.<extension>

plotter = CobraPlotter(results=results)
plotter.plot_max_growth()
plotter.plot_growth_map(surface=10)
```

### Functional API

```python
from cobravmec import run_ballooning

grate, radios, ierr = run_ballooning(
    extension="example",
    k_w=3,
    kth=1,
    l_geom_input=True,
    l_tokamak_input=False,
    init_zeta=[0.0],
    init_theta=[0.0],
    surfaces=[5, 10, 15],
)
```

COBRAVMEC expects `wout.<extension>.nc` or `wout_<extension>.nc` in the current
working directory. The wrapper avoids COBRA's text input/output files, and
returns growth rates directly as NumPy arrays.


# COBRAVMEC Standalone Build

This directory is a standalone build of COBRAVMEC and a reduced
`LIBSTELL_mini`, copied from `STELLOPT`/`VMEC2000` and kept separate so the
original tree remains unchanged.

## Makefile Build (Fortran-only)

From this directory:

```
make release
```

or for debug builds:

```
make debug
```

The binaries and libraries are placed under `bin/`, `LIBSTELL/Release`,
and `COBRAVMEC/Release` (or `Debug`).

## CMake Build (Fortran + Python)

COBRAVMEC includes a CMake build that uses `LIBSTELL_mini` and supports
the Python wrapper. Example:

```
cmake -S . -B build -DNETCDF_INC_PATH=/path/to/include -DNETCDF_LIB_PATH=/path/to/lib
cmake --build build
```

For the Python package, install from `./python`:

```
/path/to/python -m pip install ./python --no-build-isolation
```

This will build `libstell_mini`, `cobravmec`, and the `_cobravmec` extension.
See `cobravmec-standalone/python/README.md` for Python API usage.

## Local Compiler Settings

If your host name does not match a bundled `make_*.inc`, the build falls back
to `SHARE/make_local.inc`. You can override settings with:

```
make MACHINE=ubuntu release
```

or by editing `SHARE/make_local.inc` in this standalone copy.
