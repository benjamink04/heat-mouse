# %% --- Imports -----------------------------------------------------------------------
import pathlib
import threading

from PyQt5 import QtCore, QtWidgets, uic

import heatmouse.activewindow as hactivewindow
import heatmouse.listener as hlistener

# %% --- Constants ---------------------------------------------------------------------
# %% THIS_DIR
THIS_DIR = pathlib.Path(__file__).parent.absolute()


# %% --- Classes -----------------------------------------------------------------------
# %% HeatMouse
class HeatMouse(QtWidgets.QMainWindow):
    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        super().__init__()

    # %% --- Methods -------------------------------------------------------------------
    # %% run_listener
    def run_listener(self):
        active_window = hactivewindow.ActiveWindow()
        key_listener = hlistener.KeyListener()
        event_thread = threading.Thread(target=key_listener.run)
        event_thread.daemon = True
        event_thread.start()

        try:
            while event_thread.is_alive():
                event = key_listener.get_next_event(timeout=1)
                if event:
                    print(
                        f"Application: {active_window.window}, Button: {event[0]}, Location: {event[1]}, {event[2]}"
                    )
        except KeyboardInterrupt:
            print("Stopping the listener...")
            key_listener.stop()
            event_thread.join()  # Ensure the thread is closed
            print("Listener stopped.")

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _load_ui
    def _load_ui(self):
        ui_path = THIS_DIR.joinpath("heatmouse.ui")
        uic.loadUi(str(ui_path), self)
