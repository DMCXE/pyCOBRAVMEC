# cobravmec (Python)

Python bindings for COBRAVMEC using a compiled Fortran extension built via
CMake + scikit-build (f90wrap + f2py).

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
/path/to/python -m pip install cobravmec-standalone/python --no-build-isolation
```

The build uses `cobravmec-standalone/cmake_config_file.json` for CMake
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

COBRAVMEC expects `wout.<extension>` or `wout_<extension>` in the current
working directory. The wrapper avoids COBRA's text input/output files, and
returns growth rates directly as NumPy arrays.

## WOUT Loading (Python-side only)

`load_wout` loads VMEC wout NetCDF data for downstream tooling. This requires
the optional `netCDF4` Python package.

```python
from cobravmec import load_wout

wout = load_wout(path="wout.example.nc")
```

You can also load from an in-memory NetCDF buffer:

```python
buffer = open("wout.example.nc", "rb").read()
wout = load_wout(data=buffer)
```

Note: COBRAVMEC still reads wout data from disk via the Fortran
`read_wout_mod` module. The in-memory loader is for Python-side tooling and
does not bypass the Fortran NetCDF file read.
