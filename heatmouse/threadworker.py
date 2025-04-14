import threading

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

import heatmouse.activewindow as hactivewindow
import heatmouse.listener as hlistener


class Worker(QRunnable):
    """
    Worker thread
    """

    def __init__(self):
        super(Worker, self).__init__()
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
                        print(
                            f"Application: {active_window.window}, Button: {event[0]},",
                            " Location: {event[1]}, {event[2]}",
                        )
            except KeyboardInterrupt:
                print("Stopping the listener...")
                self.key_listener.stop()
                self.event_thread.join()  # Ensure the thread is closed
                print("Listener stopped.")

        except Exception as e:
            self.signals.error.emit(e)

    def stop(self):
        self.key_listener.stop()


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
    error = pyqtSignal(tuple)
    update = pyqtSignal(tuple)
