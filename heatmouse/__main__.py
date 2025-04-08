"""Run the Heat Mouse."""

# %% --- Imports -----------------------------------------------------------------------
import sys

from PyQt5 import QtWidgets

from heatmouse import heatmouse_main


# %% --- Functions ---------------------------------------------------------------------
# %% run
def run() -> QtWidgets.QMainWindow:
    """
    Run the RNPT.

    Parameters
    ----------
    show_about : bool
        If True shows the about GUI
    project_file : str
        The project file

    Returns
    -------
    ui : QtWidgets.QMainWindow
        The main window
    """
    ui = heatmouse_main.HeatMouse()
    return ui.run_gui()
    # ui.run_listener()


# %% --- Main Block --------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = run()
    sys.exit(app.exec_())
