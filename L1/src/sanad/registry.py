"""Choose component versions (provided; level 0).

sanad.toml names the version of each part, for example

    [parts]
    normalize = "v0_identity"
    tokenize  = "v0_whitespace"
    router    = "v0_majority"
    search    = "v0_exact"

A version is a module sanad/<part>/<version>.py. Old versions stay in place, so
any two can be compared on the same split.
"""
import importlib
import pkgutil
import tomllib
from pathlib import Path

LEVEL = 0
PARTS = ("normalize", "tokenize", "router", "search", "keyboard")
DEFAULTS = {"normalize": "v0_identity", "tokenize": "v0_whitespace",
            "router": "v0_majority", "search": "v0_exact", "keyboard": None}


def config(path=None):
    """Return {part: version} from sanad.toml (searched upwards) over DEFAULTS."""
    chosen = dict(DEFAULTS)
    if path is None:
        for d in (Path.cwd(), *Path.cwd().parents):
            if (d / "sanad.toml").exists():
                path = d / "sanad.toml"
                break
    if path is not None:
        with open(path, "rb") as f:
            chosen.update(tomllib.load(f).get("parts", {}))
    return chosen


def available(part):
    """Versions of a part that exist in this copy of the project, in order."""
    pkg = importlib.import_module(f"sanad.{part}")
    return sorted(m.name for m in pkgutil.iter_modules(pkg.__path__) if m.name.startswith("v"))


def load(part, version):
    """Import sanad.<part>.<version> and return the module."""
    if version not in available(part):
        raise LookupError(f"{part} has no version {version!r}; available: {available(part)}")
    return importlib.import_module(f"sanad.{part}.{version}")
