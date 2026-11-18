"""Smoke test: the package imports and exposes a version string."""

import brixgate


def test_version_is_defined() -> None:
    """The package must expose a non-empty version string."""
    assert isinstance(brixgate.__version__, str)
    assert brixgate.__version__
