# %% --- Imports -----------------------------------------------------------------------
import copy
import ctypes
import pathlib
from collections import Counter

import matplotlib.axes as maxes
import matplotlib.backends.backend_qt5agg as mqt5agg
import matplotlib.figure as mfigure
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import heatmouse.database as hdatabase
import heatmouse.threadworker as hthreadworker

# %% --- Constants ---------------------------------------------------------------------
# %% THIS_DIR
THIS_DIR = pathlib.Path(__file__).parent.absolute()


# %% --- Classes -----------------------------------------------------------------------
# %% HeatMouse
class HeatMouseMainWindow(QtWidgets.QMainWindow):
    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self, parent=None):
        self._screensize = None
        self._active_window = None
        self._data = None
        self._db_data = None
        self._axes = None
        self._canvas = None
        self._figure = None
        self._bins = None
        self._database = None
        self._parent = parent
        self._threadpool = QtCore.QThreadPool()
        super().__init__()
        self.heatmap = None
        self.filter_worker_active = False
        self.awaiting_filter = False

        self._init_gui()

    # %% --- Properties ----------------------------------------------------------------
    # %% axes
    @property
    def axes(self) -> maxes.Axes:
        """Get or set the axes for the graphs."""
        return self._axes

    @axes.setter
    def axes(self, axes: maxes.Axes):
        self._axes = axes

    # %% canvas
    @property
    def canvas(self) -> mqt5agg.FigureCanvasQTAgg:
        """Get the canvas for the figure."""
        if self._canvas is None:
            self._canvas = mqt5agg.FigureCanvasQTAgg(self.figure)
        return self._canvas

    # %% figure
    @property
    def figure(self) -> mfigure.Figure:
        """Get the figure for drawing."""
        if self._figure is None:
            self._figure = mfigure.Figure()
        return self._figure

    # %% database
    @property
    def database(self) -> hdatabase.Database:
        """Get the HeatMouse database"""
        if self._database is None:
            self._database = hdatabase.Database()
        return self._database

    # %% parent
    @property
    def parent(self):
        return self._parent

    # %% threadpool
    @property
    def threadpool(self):
        return self._threadpool

    # %% screensize
    @property
    def screensize(self) -> tuple[int, int]:
        if self._screensize is None:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            self._screensize = (
                user32.GetSystemMetrics(0),
                user32.GetSystemMetrics(1),
            )
        return self._screensize

    # %% data
    @property
    def data(self) -> dict[str : tuple[list, list, list]]:
        if self._data is None:
            self._data = copy.deepcopy(self.db_data)
        try:
            return self._data[self.active_window]
        except KeyError:
            if self.active_window is None:
                return
            self._data[self.active_window] = ([], [], [])
            return self._data[self.active_window]

    # %% db_data
    @property
    def db_data(self) -> dict[str : tuple[list, list, list]]:
        if self._db_data is None:
            self._db_data = self.database.get_all_data()
        return self._db_data

    # %% bins
    @property
    def bins(self) -> tuple[np.array, np.array]:
        if self._bins is None:
            xbins = np.linspace(0, self.screensize[0], self.screensize[0])
            ybins = np.linspace(0, self.screensize[1], self.screensize[1])
            self._bins = (ybins, xbins)
        return self._bins

    # %% active_window
    @property
    def active_window(self) -> str:
        return self._active_window

    @active_window.setter
    def active_window(self, window):
        if (window != self._active_window) and (window is not None) and (window != ""):
            self._active_window = window
            self._window_change()

    # %% --- Methods -------------------------------------------------------------------
    # %% draw
    def draw(self, heatmap):
        self.filter_worker_active = False
        self.heatmap = heatmap
        self.canvas.restore_region(self.background)
        self.axes.draw_artist(self.heatmap)
        self.canvas.blit(self.axes.bbox)
        # self.axes.imshow(self.data, cmap="viridis")
        # self.canvas.draw()

    # %% listener_task
    def listener_task(self):
        self.listener_worker = hthreadworker.ListenerWorker()
        self.listener_worker.signals.update.connect(self._update_data)
        self.listener_worker.signals.finished.connect(self._task_finished)
        self.threadpool.start(self.listener_worker)

    # %% filter_task
    def filter_task(self):
        self.filter_worker = hthreadworker.FilterWorker(
            self.heatmap, self.data, self.bins, self.axes
        )
        self.filter_worker.signals.result.connect(self.draw)
        self.filter_worker.signals.result.connect(self._check_filter_queue)
        self.filter_worker_active = True
        self.threadpool.start(self.filter_worker)

    # %% closeEvent
    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            self.listener_worker.stop()
            self.filter_worker.stop()
        except AttributeError:
            pass
        self._store_data()
        event.accept()

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _check_filter_queue
    def _check_filter_queue(self):
        if self.awaiting_filter:
            self.awaiting_filter = False
            self.filter_task()

    # %% _store_data
    def _store_data(self):
        all_data = copy.deepcopy(self._data)
        print(self.db_data)
        for key, table_data in self.db_data.items():
            new_data = []
            for all_col, db_col in zip(all_data[key], table_data):
                new_data.append(list((Counter(all_col) - Counter(db_col)).elements()))
            all_data[key] = tuple(new_data)
        self.database.store_all_data(all_data)

    # %% _update_data
    def _update_data(self, values):
        event = values[1]
        if (
            (event[0] > self.screensize[0])
            or (event[1] > self.screensize[1])
            or (values[0] is None)
        ):
            return
        self.active_window = values[0]
        self.data[0].append(event[0])
        self.data[1].append(event[1])
        self.data[2].append(event[2])
        if not self.filter_worker_active:
            self.filter_task()
        else:
            self.awaiting_filter = True

    # %% _task_finished
    def _task_finished(self, out=None):
        print(out)

    # %% _create_canvas
    def _create_canvas(self, figure: mfigure.Figure) -> mqt5agg.FigureCanvasQTAgg:
        return mqt5agg.FigureCanvasQTAgg(figure)

    # %% _create_figure
    def _create_figure(self) -> mfigure.Figure:
        return mfigure.Figure()

    # %% _window_change
    def _window_change(self):
        # self.axes.clear()
        self.axes.set_title(self.active_window)
        self.canvas.resize_event()
        # self.background = self.canvas.copy_from_bbox(self.axes.bbox)
        # self.canvas.restore_region(self.background)
        # self.canvas.blit(self.axes.bbox)
        # self.heatmap = None

    # %% _init_axes
    def _init_axes(self):
        """Initialize the axes."""
        if self.axes:
            self.axes.remove()
        axes = self.figure.add_subplot()
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        self.background = self.canvas.copy_from_bbox(axes.bbox)

        # self.figure.colorbar(label="Value")
        self.axes = axes

    # %% _init_gui
    def _init_gui(self):
        """
        Initialize the GUI at the end of `__init__` method.
        """
        self._load_ui()
        self.button_action = QtWidgets.QAction("Start", self)
        self.button_action.triggered.connect(self.listener_task)
        self.toolBar.addAction(self.button_action)
        self.widget_Canvas.layout().addWidget(self.canvas)
        self._init_axes()

    # %% _load_ui
    def _load_ui(self):
        ui_path = THIS_DIR.joinpath("heatmouse.ui")
        uic.loadUi(str(ui_path), self)
