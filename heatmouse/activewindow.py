"""
The HeatMouse active window class used to retrieve the current active window.

Classes
-------
ActiveWindow
    Monitors the active window on the user monitor.
"""

# %% --- Imports -----------------------------------------------------------------------
import ctypes
from ctypes import wintypes

import psutil
import win32gui

# %% --- Constants ---------------------------------------------------------------------
# %% APP_DICT
APP_DICT = {"explorer.exe": "File Explorer", "Photos.exe": "Photos"}


# %% --- Classes -----------------------------------------------------------------------
# %% ActiveWindow
class ActiveWindow:
    """
    Monitors the active window on the user monitor.

    Properties
    ----------
    active_process: str
        Get the active process name.
    window: str
        Get the active window name.

    Methods
    -------
    get_active_window_title: str
        Returns the title of the currently active window.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    def __init__(self):
        self._window = None

    # %% --- Properties ----------------------------------------------------------------
    # %% active_process
    @property
    def active_process(self) -> str:
        """
        Get the active process name.

        Returns
        -------
        str
            Active process name.
        """
        user32 = ctypes.windll.user32
        h_wnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
        return psutil.Process(pid.value).name()

    # %% window
    @property
    def window(self) -> str:
        """
        Get the active window name.

        Returns
        -------
        str
            Active window name.
        """
        active_window = self.get_active_window_title()
        if self._window != active_window:
            self._window = active_window
        return self._window

    # %% --- Methods -------------------------------------------------------------------
    # %% get_active_window_title
    def get_active_window_title(self) -> str:
        """
        Returns the title of the currently active window.

        Returns
        -------
        str
            Active window name.
        """
        active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if self.active_process in APP_DICT.keys():
            active_window = APP_DICT[self.active_process]
        else:
            try:
                active_window = active_window.rsplit(" - ", 1)[1]
            except IndexError:
                pass
        return active_window
