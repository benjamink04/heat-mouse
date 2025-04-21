"""Run Heat Mouse."""

# %% --- Imports -----------------------------------------------------------------------
import sys

from PyQt5 import QtGui, QtWidgets

import heatmouse
from heatmouse import heatmouse_main


# %% --- Functions ---------------------------------------------------------------------
# %% run
def run() -> QtWidgets.QMainWindow:
    """
    Run Heat Mouse.

    Returns
    -------
    ui : QtWidgets.QMainWindow
        The main window
    """
    ui = heatmouse_main.HeatMouse()
    return ui.run_gui()


# %% --- Main Block --------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    icon_loc = str(heatmouse.THIS_DIR.joinpath("images\\heatmouse.ico"))
    app.setWindowIcon(QtGui.QIcon(icon_loc))
    window = run()
    sys.exit(app.exec_())
