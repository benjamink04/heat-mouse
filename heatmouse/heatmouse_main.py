#!/usr/bin/env python #
"""
The Heat Mouse primary class.

Classes
-------
HeatMouse
    The main Heat Mouse class.
"""
# %% --- Imports -----------------------------------------------------------------------
from PyQt5 import QtWidgets

import heatmouse.mainwindow as hmainwindow


# %% --- Classes -----------------------------------------------------------------------
# %% HeatMouse
class HeatMouse:
    """
    The main Heat Mouse class.

    Properties
    ----------
    window : QtWidgets.QMainWindow
        Stores the GUI window object.

    Methods
    -------
    run_gui
        Run Heat Mouse as a GUI.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        self._window = None

    # %% --- Properties ----------------------------------------------------------------
    # %% window
    @property
    def window(self) -> QtWidgets.QMainWindow:
        """
        Stores the GUI window object.

        Returns
        -------
        QtWidgets.QMainWindow:
            GUI window object.
        """
        return self._window

    # %% --- Methods -------------------------------------------------------------------
    # %% run_gui
    def run_gui(self):
        """Run Heat Mouse as a GUI."""
        self._window = hmainwindow.HeatMouseMainWindow()
        self.window.show()
        return self.window
