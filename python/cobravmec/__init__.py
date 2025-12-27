import sys
import os.path

sys.path.append(os.path.dirname(__file__))

_wrapper = None
try:
    from . import cobravmec as _wrapper  # f90wrap-generated module
except ImportError:
    try:
        from . import _cobravmec as _wrapper  # f2py extension fallback
    except ImportError:
        _wrapper = None

if _wrapper is not None:
    if hasattr(_wrapper, "cobra_api"):
        _wrapper = _wrapper.cobra_api
    if not hasattr(_wrapper, "cobra_run") and hasattr(_wrapper, "f90wrap_cobra_api__cobra_run"):
        _wrapper.cobra_run = _wrapper.f90wrap_cobra_api__cobra_run
    if not hasattr(_wrapper, "cobra_run") and hasattr(_wrapper, "f90wrap_cobra_api__cobra_run_alloc"):
        _wrapper.cobra_run = _wrapper.f90wrap_cobra_api__cobra_run_alloc
    if not hasattr(_wrapper, "cobra_run") and hasattr(_wrapper, "cobra_run_alloc"):
        _wrapper.cobra_run = _wrapper.cobra_run_alloc
    if not hasattr(_wrapper, "cobra_cleanup") and hasattr(_wrapper, "f90wrap_cobra_api__cobra_cleanup"):
        _wrapper.cobra_cleanup = _wrapper.f90wrap_cobra_api__cobra_cleanup
    if not hasattr(_wrapper, "cobra_deallocate") and hasattr(_wrapper, "f90wrap_cobra_api__cobra_deallocate"):
        _wrapper.cobra_deallocate = _wrapper.f90wrap_cobra_api__cobra_deallocate

    sys.modules[__name__ + ".cobravmec"] = _wrapper
from .api import (
    CobraPlotter,
    CobraResults,
    CobraRunner,
    WoutData,
    cleanup,
    cobra_grate_path,
    load_wout,
    run_ballooning,
    write_cobra_grate,
)

__all__ = [
    "CobraPlotter",
    "CobraResults",
    "CobraRunner",
    "WoutData",
    "cleanup",
    "cobra_grate_path",
    "load_wout",
    "run_ballooning",
    "write_cobra_grate",
]
