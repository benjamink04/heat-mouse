"""
Initialize the Heat Mouse package.

Constants
---------
APP_NAME : str
    The application name.
APP_VERSION : str
    The application version in the format 'YYYY.MM.XX'.

Functions
---------
setup_app_constants
    Set the entt_common constants for running Heat Mouse.
"""

# %% --- Imports -----------------------------------------------------------------------
import importlib.metadata as _md
import pathlib
import sys

from PyQt5 import QtWidgets

# import heatmouse

# %% --- Constants ---------------------------------------------------------------------
# %% __version__
__version__ = _md.version(__name__)
# %% qtapp
qtapp = QtWidgets.QApplication(sys.argv)
# %% APP_NAME
APP_NAME: str = "Heat_Mouse"
""" The application name."""
# %% APP_VERSION
APP_VERSION: str = __version__.partition("+")[0]
"""The application version in the format 'YYYY.MM.XXX'."""
# %% THIS_DIR
THIS_DIR: pathlib.Path = pathlib.Path(__file__).parent.absolute()
# %% ERROR_DIR
ERROR_DIR = THIS_DIR.parent
# %% ERROR_FILE
ERROR_FILE = THIS_DIR.parent.joinpath("heatmouse_errors.txt")
