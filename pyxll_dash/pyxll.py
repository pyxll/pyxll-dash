"""Entry points for registering this package 
with the PyXLL Excel add-in.
"""
import pyxll
import logging

_log = logging.getLogger(__name__)


def modules():
    """Returns the modules that PyXLL should load on startup."""

    if not pyxll.__version__.endswith("dev"):
        version = tuple(map(int, pyxll.__version__.split(".")[:3]))
        if version < (5, 9, 0):
            _log.error("PyXLL version >= 5.9.0 is required to use pyxll_dash.")
            return []

    return [
        "pyxll_dash.dash_bridge"
    ]
