import threading

import numpy as np
from astropy.convolution import convolve
from astropy.convolution.kernels import Gaussian2DKernel
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

import heatmouse.activewindow as hactivewindow
import heatmouse.listener as hlistener


class ListenerWorker(QRunnable):
    """
    Listener worker thread
    """

    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.key_listener = hlistener.KeyListener()
        self.event_thread = threading.Thread(target=self.key_listener.run)

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            active_window = hactivewindow.ActiveWindow()

            self.event_thread.daemon = True
            self.event_thread.start()

            try:
                while self.event_thread.is_alive():
                    event = self.key_listener.get_next_event(timeout=1)
                    if event:

                        self.signals.update.emit((active_window.window, event))
                        # print(
                        #     f"Application: {active_window.window}, Button: {event[0]},",
                        #     f" Location: {event[1]}, {event[2]}",
                        # )
            except KeyboardInterrupt:
                pass
                # print("Stopping the listener...")
                # self.key_listener.stop()
                # self.event_thread.join()  # Ensure the thread is closed
                # print("Listener stopped.")

        except Exception as e:
            self.signals.error.emit(e)

    def stop(self):
        self.key_listener.stop()


class FilterWorker(QRunnable):
    """
    Filter worker thread
    """

    def __init__(self, heatmap, data, bins, axes):
        super().__init__()
        self.signals = WorkerSignals()
        self.data = data
        self.heatmap = heatmap
        self.bins = bins
        self.axes = axes

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
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
            # self.heatmap.set_array(heatmap)

        self.signals.result.emit(self.heatmap)
        self.signals.finished.emit()


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress
    """

    finished = pyqtSignal()
    result = pyqtSignal(object)
    error = pyqtSignal(tuple)
    update = pyqtSignal(tuple)
