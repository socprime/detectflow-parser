"""Schema Parser - DSL pipeline for parsing and transforming events."""

from functools import lru_cache
from importlib.metadata import version as get_package_version

from schema_parser.manager import ParserManager
from schema_parser.sigma_validation import (
    SigmaNotSupported,
    SigmaValidator,
    ValidationResult,
)

__all__ = [
    "ParserManager",
    "SigmaValidator",
    "ValidationResult",
    "SigmaNotSupported",
    "__version__",
]


@lru_cache(maxsize=1)
def get_version() -> str:
    """Get version from package metadata (pyproject.toml).

    Returns:
        Version string (e.g., "0.4.0") or "dev" if not installed as package.
    """
    try:
        return get_package_version("schema-parser")
    except Exception:
        return "dev"


__version__ = get_version()
