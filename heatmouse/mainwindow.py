# %% --- Imports -----------------------------------------------------------------------
import ctypes
import pathlib

# import threading
import time

# import matplotlib
import matplotlib.axes as maxes
import matplotlib.backends.backend_qt5agg as mqt5agg
import matplotlib.figure as mfigure
import numpy as np
from astropy.convolution import convolve
from astropy.convolution.kernels import Gaussian2DKernel
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import heatmouse.threadworker as hthreadworker

# matplotlib.use("GTKAgg")

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
        self._data = None
        self._axes = None
        self._canvas = None
        self._figure = None
        self._parent = parent
        self._threadpool = QtCore.QThreadPool()
        super().__init__()
        self.heatmap = None
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
    def data(self) -> tuple[list, list]:
        if self._data is None:
            self._data = ([], [])
        return self._data

    # %% --- Methods -------------------------------------------------------------------
    # %% draw
    def draw(self):
        heatmap, _, _ = np.histogram2d(
            self.data[0],
            self.data[1],
            bins=(self.screensize[1], self.screensize[0]),
        )
        if self.heatmap is None:
            self.heatmap = self.axes.imshow(
                convolve(heatmap, Gaussian2DKernel(2, 2)), cmap="viridis"
            )
        else:
            tic = time.time()
            self.heatmap.set_array(convolve(heatmap, Gaussian2DKernel(2, 2)))
            print(time.time() - tic)
        self.canvas.restore_region(self.background)
        self.axes.draw_artist(self.heatmap)
        self.canvas.blit(self.axes.bbox)
        # self.axes.imshow(self.data, cmap="viridis")
        # self.canvas.draw()

    # %% thread_task
    def thread_task(self):
        self.worker = hthreadworker.Worker()
        self.worker.signals.update.connect(self._update_data)
        self.worker.signals.finished.connect(self._task_finished)
        self.threadpool.start(self.worker)

    # %% closeEvent
    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            self.worker.stop()
        except AttributeError:
            pass
        event.accept()

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _update_data
    def _update_data(self, values):
        # active_window = values[0]
        event = values[1]

        self.data[0].append(event[1])
        self.data[1].append(event[2])
        self.draw()

    # %% _task_finished
    def _task_finished(self, out=None):
        print(out)

    # %% _create_canvas
    def _create_canvas(self, figure: mfigure.Figure) -> mqt5agg.FigureCanvasQTAgg:
        return mqt5agg.FigureCanvasQTAgg(figure)

    # %% _create_figure
    def _create_figure(self) -> mfigure.Figure:
        return mfigure.Figure()

    # %% _init_axes
    def _init_axes(self):
        """Initialize the axes."""
        if self.axes:
            self.axes.remove()
        axes = self.figure.add_subplot()
        axes.set_xlim(0, self.screensize[0])
        axes.set_ylim(0, self.screensize[1])
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
        self.button_action.triggered.connect(self.thread_task)
        self.toolBar.addAction(self.button_action)
        # self.widget_Canvas.layout().addWidget(self.toolbar)
        self.widget_Canvas.layout().addWidget(self.canvas)
        self._init_axes()

    # %% _load_ui
    def _load_ui(self):
        ui_path = THIS_DIR.joinpath("heatmouse.ui")
        uic.loadUi(str(ui_path), self)
