# %% --- Imports -----------------------------------------------------------------------
import pathlib

import matplotlib
import matplotlib.axes as maxes
import matplotlib.backends.backend_qt5agg as mqt5agg
import matplotlib.figure as mfigure
from PyQt5 import QtWidgets, uic

# %% --- Constants ---------------------------------------------------------------------
# %% THIS_DIR
THIS_DIR = pathlib.Path(__file__).parent.absolute()


# %% --- Classes -----------------------------------------------------------------------
# %% HeatMouse
class HeatMouseMainWindow(QtWidgets.QMainWindow):
    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        self._axes = None
        self._figure = None
        super().__init__()
        self._initialize_gui()

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
        return self.figure.canvas

    # %% figure
    @property
    def figure(self) -> mfigure.Figure:
        """Get the figure for drawing."""
        if self._figure is None:
            self._figure = self._create_figure()
        return self._figure

    # %% --- Methods -------------------------------------------------------------------
    def draw(self, data):
        self.axes.imshow(data)

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _create_canvas
    def _create_canvas(self, figure: mfigure.Figure) -> mqt5agg.FigureCanvasQTAgg:
        return mqt5agg.FigureCanvasQTAgg(figure)

    # %% _create_figure
    def _create_figure(self) -> mfigure.Figure:
        figure = mfigure.Figure()
        self._create_canvas(figure)
        return figure

    # %% _init_axes
    def _init_axes(self):
        """Initialize the axes."""
        if self.axes:
            self.axes.remove()
        self.figure.subplots_adjust(hspace=0.8, wspace=0.3)
        axes = self.figure.add_subplot()
        self.axes = axes

    # %% _initialize_gui
    def _initialize_gui(self):
        """
        Initialize the GUI at the end of `__init__` method.
        """
        self._load_ui()
        self.button_action = QtWidgets.QAction("Start", self)
        self.toolBar.addAction(self.button_action)
        # self.widget_Canvas.layout().addWidget(self.toolbar)
        self.widget_Canvas.layout().addWidget(self.canvas)
        self._init_axes()

    # %% _load_ui
    def _load_ui(self):
        ui_path = THIS_DIR.joinpath("heatmouse.ui")
        uic.loadUi(str(ui_path), self)
