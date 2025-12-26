from dataclasses import dataclass
import os
import inspect
from pathlib import Path

import numpy as np

try:
    import netCDF4
except ImportError:  # pragma: no cover - optional dependency
    netCDF4 = None

import importlib
import sys


def _normalize_core(core):
    cobra_api = getattr(core, "cobra_api", None)
    if cobra_api is not None:
        core = cobra_api
    if not hasattr(core, "cobra_run") and hasattr(core, "f90wrap_cobra_api__cobra_run"):
        core.cobra_run = core.f90wrap_cobra_api__cobra_run
    if not hasattr(core, "cobra_run") and hasattr(core, "f90wrap_cobra_api__cobra_run_alloc"):
        core.cobra_run = core.f90wrap_cobra_api__cobra_run_alloc
    if not hasattr(core, "cobra_run") and hasattr(core, "cobra_run_alloc"):
        core.cobra_run = core.cobra_run_alloc
    if not hasattr(core, "cobra_cleanup") and hasattr(core, "f90wrap_cobra_api__cobra_cleanup"):
        core.cobra_cleanup = core.f90wrap_cobra_api__cobra_cleanup
    if not hasattr(core, "cobra_deallocate") and hasattr(core, "f90wrap_cobra_api__cobra_deallocate"):
        core.cobra_deallocate = core.f90wrap_cobra_api__cobra_deallocate
    return core


def _get_core():
    pkg = __package__ or "cobravmec"
    candidates = (f"{pkg}.cobravmec", f"{pkg}._cobravmec")
    errors = []
    for name in candidates:
        core = sys.modules.get(name)
        if core is not None:
            return _normalize_core(core)
    for name in candidates:
        try:
            core = importlib.import_module(name)
            return _normalize_core(core)
        except ImportError as exc:
            errors.append((name, exc))
            continue
    base_dir = Path(__file__).resolve().parent
    search_roots = [
        base_dir.parent / "_skbuild",
        base_dir / "_skbuild",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        matches = list(root.glob("**/_cobravmec*.so")) + list(root.glob("**/_cobravmec*.dylib"))
        if not matches:
            continue
        for match in matches:
            sys.path.insert(0, str(match.parent))
            try:
                core = importlib.import_module(f"{pkg}._cobravmec")
                return _normalize_core(core)
            except ImportError as exc:
                errors.append((str(match), exc))
                continue
    detail = "; ".join(f"{name}: {exc}" for name, exc in errors)
    raise ImportError(
        "Failed to import COBRAVMEC extension module. "
        "Tried: " + ", ".join(candidates) + ". "
        "Errors: " + (detail if detail else "none")
    )


@dataclass
class WoutData:
    variables: dict
    attrs: dict
    source: str


@dataclass
class CobraResults:
    extension: str
    k_w: int
    kth: int
    l_geom_input: bool
    l_tokamak_input: bool
    init_zeta: np.ndarray
    init_theta: np.ndarray
    surfaces: np.ndarray
    grate: np.ndarray
    radios: np.ndarray
    ierr: int

    def max_growth_per_surface(self):
        """Return max growth rate per surface."""
        return self.grate.max(axis=(1, 2))


def run_ballooning(
    extension,
    k_w,
    kth,
    l_geom_input,
    l_tokamak_input,
    init_zeta,
    init_theta,
    surfaces,
    lscreen=False,
):
    """
    Run COBRAVMEC ballooning analysis without the text input/output files.

    Parameters
    ----------
    extension : str
        WOUT file extension (expects wout.<extension> or wout_<extension>).
    k_w : int
        Number of helical wells.
    kth : int
        Mode number (1 = most unstable).
    l_geom_input : bool
        Interpret inputs as geometric (zeta, theta) if True.
    l_tokamak_input : bool
        Interpret inputs as tokamak-style (alpha, thetak) if True.
    init_zeta : array_like
        Initial toroidal angles or alpha labels (degrees).
    init_theta : array_like
        Initial poloidal angles or labels (degrees).
    surfaces : array_like
        Surface indices on the full grid (1-based).
    lscreen : bool, optional
        Emit screen output from COBRA routines.

    Returns
    -------
    grate : ndarray
        Growth rates shaped (nsurface, ntheta, nzeta).
    radios : ndarray
        Radial coordinates for each surface (length nsurface).
    ierr : int
        Non-zero if COBRA failed to read the equilibrium.
    """
    init_zeta = np.asarray(init_zeta, dtype=np.float64)
    init_theta = np.asarray(init_theta, dtype=np.float64)
    surfaces = np.asarray(surfaces, dtype=np.int32)

    _core = _get_core()
    cobra_run = _core.cobra_run
    try:
        sig = inspect.signature(cobra_run)
        if "grate_out" in sig.parameters and "radios_out" in sig.parameters:
            raise TypeError("cobra_run requires explicit output arrays")
    except (TypeError, ValueError):
        sig = None

    try:
        grate, radios, ierr = cobra_run(
            extension,
            int(k_w),
            int(kth),
            bool(l_geom_input),
            bool(l_tokamak_input),
            init_zeta,
            init_theta,
            surfaces,
            lscreen,
        )
        return grate, radios, int(ierr)
    except TypeError as exc:
        if sig is None and "grate_out" not in str(exc) and "radios_out" not in str(exc):
            raise

    nsurf = surfaces.size
    ntheta = init_theta.size
    nzeta = init_zeta.size
    grate = np.zeros((nsurf, ntheta, nzeta), dtype=np.float64, order="F")
    radios = np.zeros(nsurf, dtype=np.float64, order="F")
    ierr = cobra_run(
        extension,
        int(k_w),
        int(kth),
        bool(l_geom_input),
        bool(l_tokamak_input),
        init_zeta,
        init_theta,
        surfaces,
        grate,
        radios,
        lscreen,
    )
    return grate, radios, int(ierr)


class CobraRunner:
    """
    COBRAVMEC execution wrapper with fixed resolution/control parameters.

    Parameters
    ----------
    k_w, kth, init_zeta, init_theta : resolution/control parameters
        Stored on the instance and reused for each run.
    surfaces : array_like
        Surface indices on the full grid (1-based).
    l_geom_input, l_tokamak_input : bool
        Input interpretation flags.
    lscreen : bool
        Emit screen output from COBRA routines.
    """

    def __init__(
        self,
        k_w,
        kth,
        init_zeta,
        init_theta,
        surfaces,
        l_geom_input,
        l_tokamak_input,
        lscreen=False,
    ):
        self.k_w = int(k_w)
        self.kth = int(kth)
        self.l_geom_input = bool(l_geom_input)
        self.l_tokamak_input = bool(l_tokamak_input)
        self.lscreen = bool(lscreen)
        self.init_zeta = np.asarray(init_zeta, dtype=np.float64)
        self.init_theta = np.asarray(init_theta, dtype=np.float64)
        self.surfaces = np.asarray(surfaces, dtype=np.int32)
        self.results = None

    def run(self, extension, surfaces=None, lscreen=None):
        """
        Run COBRAVMEC for a given VMEC wout extension.

        The stored resolution parameters are reused unless overridden.
        """
        surf = self.surfaces if surfaces is None else np.asarray(surfaces, dtype=np.int32)
        screen = self.lscreen if lscreen is None else bool(lscreen)
        grate, radios, ierr = run_ballooning(
            extension=extension,
            k_w=self.k_w,
            kth=self.kth,
            l_geom_input=self.l_geom_input,
            l_tokamak_input=self.l_tokamak_input,
            init_zeta=self.init_zeta,
            init_theta=self.init_theta,
            surfaces=surf,
            lscreen=screen,
        )
        self.results = CobraResults(
            extension=str(extension),
            k_w=self.k_w,
            kth=self.kth,
            l_geom_input=self.l_geom_input,
            l_tokamak_input=self.l_tokamak_input,
            init_zeta=self.init_zeta,
            init_theta=self.init_theta,
            surfaces=surf,
            grate=grate,
            radios=radios,
            ierr=int(ierr),
        )
        return self.results

    def write_output(self, path=None, directory=None, extension=None):
        """
        Write COBRA-style growth-rate output for the latest run.

        If path is not provided, it is derived from the extension.
        """
        if self.results is None:
            raise RuntimeError("No results available. Run CobraRunner.run first.")
        ext = extension if extension is not None else self.results.extension
        out_path = Path(path) if path is not None else cobra_grate_path(ext, directory=directory)
        write_cobra_grate(
            out_path,
            self.results.init_zeta,
            self.results.init_theta,
            self.results.surfaces,
            self.results.grate,
            self.results.radios,
            l_geom_input=self.results.l_geom_input,
            l_tokamak_input=self.results.l_tokamak_input,
        )
        return out_path


class CobraPlotter:
    """
    Plotting helper for COBRAVMEC results.

    Accepts either a CobraRunner instance or a CobraResults object.
    """

    def __init__(self, results=None, runner=None):
        if results is None and runner is not None:
            results = runner.results
        self.results = results

    def _require_results(self):
        if self.results is None:
            raise RuntimeError("No results provided to CobraPlotter.")
        return self.results

    def _require_matplotlib(self):
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError(
                "matplotlib is required for plotting; install with `pip install matplotlib`."
            ) from exc
        return plt

    def plot_max_growth(self, ax=None, normalize=True, use_radios=True, show=True):
        """
        Plot max growth rate per surface.

        x-axis: normalized flux surface coordinate (radios if available).
        """
        res = self._require_results()
        plt = self._require_matplotlib()

        y = res.max_growth_per_surface()
        if use_radios and res.radios.size == res.surfaces.size:
            x = np.asarray(res.radios, dtype=np.float64)
        else:
            x = np.asarray(res.surfaces, dtype=np.float64)
        if normalize and x.size > 0:
            denom = np.nanmax(np.abs(x))
            if denom != 0:
                x = x / denom

        if ax is None:
            _, ax = plt.subplots()
        ax.plot(x, y, marker="o")
        ax.set_xlabel("Normalized flux surface")
        ax.set_ylabel("Max growth rate")
        ax.grid(True, alpha=0.3)
        if show:
            plt.show()
        return ax

    def plot_growth_map(self, surface=None, surface_index=None, ax=None, show=True, cmap="viridis"):
        """
        Plot a 2D growth-rate map for a selected surface.
        """
        res = self._require_results()
        plt = self._require_matplotlib()

        if surface_index is None:
            if surface is None:
                surface_index = 0
            else:
                matches = np.where(res.surfaces == surface)[0]
                if matches.size == 0:
                    raise ValueError(f"Surface {surface} not found in results.")
                surface_index = int(matches[0])

        grate = res.grate[surface_index]
        zeta = np.asarray(res.init_zeta, dtype=np.float64)
        theta = np.asarray(res.init_theta, dtype=np.float64)
        zz, tt = np.meshgrid(zeta, theta)

        if ax is None:
            _, ax = plt.subplots()
        mesh = ax.pcolormesh(zz, tt, grate, shading="auto", cmap=cmap)
        surf_label = res.surfaces[surface_index] if res.surfaces.size > surface_index else surface_index
        ax.set_title(f"Surface {surf_label}")
        ax.set_xlabel("zeta_init")
        ax.set_ylabel("theta_init")
        plt.colorbar(mesh, ax=ax, label="Growth rate")
        if show:
            plt.show()
        return ax


def cobra_grate_path(extension, directory=None):
    """
    Return the standard COBRA growth-rate filename for an extension.
    """
    base = Path(directory) if directory else Path(".")
    return base / f"cobra_grate.{extension}"


def write_cobra_grate(
    path,
    init_zeta,
    init_theta,
    surfaces,
    grate,
    radios,
    l_geom_input=True,
    l_tokamak_input=False,
):
    """
    Write a COBRA growth-rate file matching the Fortran output format.
    """
    init_zeta = np.asarray(init_zeta, dtype=np.float64)
    init_theta = np.asarray(init_theta, dtype=np.float64)
    surfaces = np.asarray(surfaces, dtype=np.int64)
    grate = np.asarray(grate, dtype=np.float64)
    radios = np.asarray(radios, dtype=np.float64)

    ntheta = init_theta.size
    nzeta = init_zeta.size
    nlis = surfaces.size

    if grate.shape != (nlis, ntheta, nzeta):
        raise ValueError(
            "grate shape must be (nsurface, ntheta, nzeta); "
            f"got {grate.shape} for ({nlis}, {ntheta}, {nzeta})"
        )
    if radios.shape[0] != nlis:
        raise ValueError("radios length must match surfaces length")

    path = Path(path)
    with path.open("w", encoding="ascii") as handle:
        for j in range(ntheta):
            for i in range(nzeta):
                if l_geom_input:
                    h1 = init_zeta[i]
                    h2 = init_theta[j]
                else:
                    if l_tokamak_input:
                        h1 = init_zeta[i]
                        h2 = init_theta[j]
                    else:
                        h1 = init_theta[j]
                        h2 = init_zeta[i]
                handle.write(f"{h1:10.3E}{h2:10.3E}{nlis:5d}\n")
                for s_idx, surf in enumerate(surfaces):
                    handle.write(
                        f"{int(surf):4d}"
                        f"{radios[s_idx]:16.8E}"
                        f"{grate[s_idx, j, i]:16.8E}\n"
                    )


def _require_netcdf():
    if netCDF4 is None:
        raise ImportError(
            "netCDF4 is required to load wout files; "
            "install with `pip install netCDF4`."
        )


def _decode_netcdf_variable(var, data):
    if netCDF4 is None:
        return np.asarray(data)
    if hasattr(data, "filled"):
        data = data.filled()
    data = np.asarray(data)
    if getattr(var, "dtype", None) is not None and var.dtype.kind == "S":
        try:
            return netCDF4.chartostring(data)
        except Exception:
            return data
    return data


def load_wout(path=None, data=None, variables=None):
    """
    Load VMEC wout NetCDF data from disk or in-memory bytes.

    Parameters
    ----------
    path : str or Path, optional
        Path to a wout NetCDF file on disk.
    data : bytes, memoryview, netCDF4.Dataset, or Mapping, optional
        In-memory NetCDF buffer or already-loaded variables mapping.
    variables : sequence of str, optional
        Variable names to load; defaults to all variables in the file.
    """
    if path is not None and data is not None:
        raise ValueError("Provide either path or data, not both")

    if isinstance(data, WoutData):
        return data

    if isinstance(data, dict):
        variables_out = {name: np.asarray(val) for name, val in data.items()}
        return WoutData(variables=variables_out, attrs={}, source="in-memory")

    if path is not None:
        _require_netcdf()
        dataset = netCDF4.Dataset(os.fspath(path), mode="r")
        close_dataset = True
        source = str(path)
    elif data is not None:
        _require_netcdf()
        if isinstance(data, (bytes, bytearray, memoryview)):
            dataset = netCDF4.Dataset("inmemory.nc", mode="r", memory=data)
            close_dataset = True
            source = "in-memory"
        else:
            dataset = data
            close_dataset = False
            source = "in-memory"
    else:
        raise ValueError("Provide a path or in-memory data")

    try:
        if variables is None:
            variables = list(dataset.variables.keys())
        variables_out = {}
        for name in variables:
            var = dataset.variables[name]
            variables_out[name] = _decode_netcdf_variable(var, var[...])
        attrs = {name: getattr(dataset, name) for name in dataset.ncattrs()}
    finally:
        if close_dataset:
            dataset.close()

    return WoutData(variables=variables_out, attrs=attrs, source=source)


def cleanup():
    """Release COBRAVMEC module state and any loaded WOUT data."""
    _core = _get_core()
    _core.cobra_cleanup()
