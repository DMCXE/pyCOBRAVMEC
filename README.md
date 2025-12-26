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

For the Python package, install from `cobravmec-standalone/python`:

```
/path/to/python -m pip install cobravmec-standalone/python --no-build-isolation
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
