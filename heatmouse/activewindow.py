import ctypes
from ctypes import wintypes

import psutil
import win32gui

# %% --- Constants ---------------------------------------------------------------------
# %% APP_DICT
APP_DICT = {"explorer.exe": "File Explorer"}


class ActiveWindow:
    def __init__(self):
        self.__window = None

    @property
    def window(self) -> str:
        active_window = self.get_active_window_title()
        if self.__window != active_window:
            self.__window = active_window
        return self.__window

    @property
    def active_process(self) -> str:
        user32 = ctypes.windll.user32
        h_wnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
        return psutil.Process(pid.value).name()

    def get_active_window_title(self):
        """Returns the title of the currently active window."""
        active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if self.active_process in APP_DICT.keys():
            active_window = APP_DICT[self.active_process]
        else:
            try:
                active_window = active_window.rsplit(" - ", 1)[1]
            except IndexError:
                pass
        return active_window
