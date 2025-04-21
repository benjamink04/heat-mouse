"""
The thread worker classes.

Classes
-------
FilterWorker
    The Gaussian filter worker thread.
ListenerWorker
    The mouse listener worker thread.
WorkerSignals
    Defines the signals available from a running worker thread.
"""

# %% --- Imports -----------------------------------------------------------------------
import threading

import numpy as np
from astropy.convolution import convolve
from astropy.convolution.kernels import Gaussian2DKernel
from PyQt5 import QtCore

import heatmouse.activewindow as hactivewindow
import heatmouse.listener as hlistener


# %% --- Classes -----------------------------------------------------------------------
# %% FilterWorker
class FilterWorker(QtCore.QRunnable):
    """
    The Gaussian filter worker thread.

    Methods
    -------
    run
        Run the Gaussian filter worker thread.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self, heatmap, data, bins, axes):
        super().__init__()
        self.signals = WorkerSignals()
        self.data = data
        self.heatmap = heatmap
        self.bins = bins
        self.axes = axes

    # %% --- Methods -------------------------------------------------------------------
    # %% run
    @QtCore.pyqtSlot()
    def run(self):
        """Run the Gaussian filter worker thread."""
        heatmap, _, _ = np.histogram2d(
            self.data[1],
            self.data[0],
            bins=self.bins,
        )
        if self.heatmap is None:
            self.heatmap = self.axes.imshow(
                convolve(heatmap, Gaussian2DKernel(2, 2)),
                cmap="viridis",
                extent=[0, len(self.bins[1]), 0, len(self.bins[0])],
            )
        else:
            self.heatmap.set_array(convolve(heatmap, Gaussian2DKernel(2, 2)))

        try:
            self.signals.result.emit(self.heatmap)
            self.signals.finished.emit()
        except RuntimeError:
            pass


# %% ListenerWorker
class ListenerWorker(QtCore.QRunnable):
    """
    The mouse listener worker thread.

    Methods
    -------
    stop
        Stop the listener worker.
    run
        Run the listener worker thread.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.key_listener = hlistener.KeyListener()
        self.event_thread = threading.Thread(target=self.key_listener.run)

    # %% --- Methods -------------------------------------------------------------------
    # %% stop
    def stop(self):
        """Stop the listener worker."""
        self.key_listener.stop()

    # %% run
    @QtCore.pyqtSlot()
    def run(self):
        """Run the listener worker thread."""
        try:
            active_window = hactivewindow.ActiveWindow()
            self.event_thread.daemon = True
            self.event_thread.start()
            while self.event_thread.is_alive():
                event = self.key_listener.get_next_event(timeout=1)
                if event:
                    self.signals.update.emit((active_window.window, event))
        except Exception as e:
            self.signals.error.emit(e)


# %% WorkerSignals
class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:
    error
        `tuple` (exctype, value, traceback.format_exc() )
    finished
        No data
    result
        `object` data returned from processing, anything
    update
        `tuple` data updated during processing, anything
    """

    error = QtCore.pyqtSignal(tuple)
    finished = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal(tuple)
