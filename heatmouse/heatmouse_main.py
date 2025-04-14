# %% --- Imports -----------------------------------------------------------------------

import pathlib

from PyQt5 import QtWidgets

# import heatmouse.activewindow as hactivewindow
# import heatmouse.listener as hlistener
import heatmouse.mainwindow as hmainwindow

# %% --- Constants ---------------------------------------------------------------------
# %% THIS_DIR
THIS_DIR = pathlib.Path(__file__).parent.absolute()


# %% --- Classes -----------------------------------------------------------------------
# %% HeatMouse
class HeatMouse:
    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        self._window = None

    # %% --- Properties ----------------------------------------------------------------
    # %% window
    @property
    def window(self) -> QtWidgets.QMainWindow:
        return self._window

    # %% --- Methods -------------------------------------------------------------------
    # %% run_gui
    def run_gui(self):
        self._window = hmainwindow.HeatMouseMainWindow(parent=self)
        self.window.show()
        return self.window
