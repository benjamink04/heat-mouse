# %% --- Imports -----------------------------------------------------------------------
import ctypes
import pathlib
import threading

import numpy as np
from PyQt5 import QtWidgets, uic

import heatmouse.activewindow as hactivewindow
import heatmouse.listener as hlistener
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
        self._screensize = None
        self._data = None
        self._window = None

    # %% --- Properties ----------------------------------------------------------------
    # %% screensize
    @property
    def screensize(self) -> tuple[int, int]:
        if self._screensize is None:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            self._screensize = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        return self._screensize

    # %% data
    @property
    def data(self) -> np.array:
        if self._data is None:
            self._data = np.zeros(self.screensize)
        return self._data

    # %% window
    @property
    def window(self) -> QtWidgets.QMainWindow:
        if self._window is None:
            self._window = hmainwindow.HeatMouseMainWindow()
        return self._window

    # %% --- Methods -------------------------------------------------------------------
    # %% run_gui
    def run_gui(self):
        self._init_connections()
        self.window.show()
        return self.window

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
                    self.data[event[1], event[2]] += 1
                    self.window.draw(self.data)
                    # print(
                    #     f"Application: {active_window.window}, Button: {event[0]}, Location: {event[1]}, {event[2]}"
                    # )
        except KeyboardInterrupt:
            print("Stopping the listener...")
            key_listener.stop()
            event_thread.join()  # Ensure the thread is closed
            print("Listener stopped.")

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _init_connections
    def _init_connections(self):
        self.window.button_action.triggered.connect(self.run_listener)
