"""
Initialize the Heat Mouse package.
"""

# %% --- Imports -----------------------------------------------------------------------
import ctypes
import importlib.metadata as _md
import pathlib
import sys

from PyQt5 import QtWidgets

# %% --- Constants ---------------------------------------------------------------------
# %% __version__
__version__ = _md.version(__name__)
# %% qtapp
qtapp = QtWidgets.QApplication(sys.argv)
# %% myappid
myappid = "heatmouse.main"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
# %% THIS_DIR
THIS_DIR: pathlib.Path = pathlib.Path(__file__).parent.absolute()
# %% PARENT_DIR
PARENT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.absolute()
