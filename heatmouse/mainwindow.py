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

import heatmouse.activeicon as hactiveicon
import heatmouse.database as hdatabase
import heatmouse.listitemdelegate as hlistitemdelegate
import heatmouse.threadworker as hthreadworker

# %% --- Constants ---------------------------------------------------------------------
# %% THIS_DIR
THIS_DIR = pathlib.Path(__file__).parent.absolute()
# %% DESC_ROLE
DESC_ROLE = QtCore.Qt.UserRole + 1


# %% --- Classes -----------------------------------------------------------------------
# %% HeatMouse
class HeatMouseMainWindow(QtWidgets.QMainWindow):
    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self, parent=None):
        self._active_window = None
        self._axes = None
        self._bins = None
        self._canvas = None
        self._data = None
        self._database = None
        self._db_data = None
        self._figure = None
        self._parent = parent
        self._selection = None
        self._screensize = None
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
                return None
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

    @bins.setter
    def bins(self, value):
        xbins = np.linspace(0, self.screensize[0], int(self.screensize[0] / value))
        ybins = np.linspace(0, self.screensize[1], int(self.screensize[1] / value))
        self._bins = (ybins, xbins)

    # %% active_window
    @property
    def active_window(self) -> str:
        return self._active_window

    @active_window.setter
    def active_window(self, window):
        if (window != self._active_window) and (window is not None) and (window != ""):
            self._active_window = window.replace("'", "")
            self._window_change()

    # %% selection
    @property
    def selection(self) -> str:
        return self._selection

    @selection.setter
    def selection(self, window):
        if (window != self._selection) and (window is not None) and (window != ""):
            self._selection = window
            self._window_change()
            self.filter_task()

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

        self.selection = "Heat Mouse"
        self.active_window = "Heat Mouse"
        self.filter_task()
        self.stackedWidget.setCurrentIndex(1)
        self.listWidget_ActiveApp.setCurrentRow(0)
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.toolBar.setVisible(True)

    # %% listener_stop
    def listener_stop(self):
        self.listener_worker.stop()
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)

    # %% filter_task
    def filter_task(self):
        data = self.data
        if self.selection != self.active_window:
            data = self._data[self.selection]
        self.filter_worker = hthreadworker.FilterWorker(
            self.heatmap, data, self.bins, self.axes
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
        self.database.connection.close()
        event.accept()

    # %% resizeEvent
    def resizeEvent(self, event: QtGui.QResizeEvent):
        try:
            height = self.listWidget_ActiveApp.itemDelegate().totalHeight
        except AttributeError:
            return
        self.listWidget_ActiveApp.setFixedSize(
            self.listWidget_ActiveApp.sizeHint().width(),
            height + 2,
        )

    # %% update_filter
    def update_filter(self, value):
        self.bins = value
        if not self.filter_worker_active:
            self.filter_task()
        else:
            self.awaiting_filter = True

    # %% populate_applist
    def populate_applist(self):
        self.listWidget_Apps.clear()
        self.listWidget_ActiveApp.clear()
        for application, table in self._data.items():
            item = QtWidgets.QListWidgetItem()
            item.setText(application)
            item.setData(DESC_ROLE, f"Data points: {len(table[0])}")
            icon_loc = self.database.get_icon(application)
            if icon_loc is None:
                icon_loc = str(THIS_DIR.joinpath("images\\noicon.png"))
            item.setIcon(QtGui.QIcon(icon_loc))
            if application == self.active_window:
                self.listWidget_ActiveApp.addItem(item)
                if application == self.selection:
                    self.listWidget_ActiveApp.setCurrentItem(item)
            else:
                self.listWidget_Apps.addItem(item)
                if application == self.selection:
                    self.listWidget_Apps.setCurrentItem(item)

    # %% update_activeapp
    def update_activeapp(self):
        item = self.listWidget_ActiveApp.item(0)
        item.setData(DESC_ROLE, f"Data points: {len(self.data[0])}")

    # %% on_button_Start_clicked
    @QtCore.pyqtSlot()
    def on_button_Start_clicked(self):
        self.listener_task()

    # %% on_listWidget_Apps
    def on_listWidget_Apps(self, item):
        self.listWidget_ActiveApp.clearSelection()
        selection = item.text()
        if selection != self.selection:
            self.selection = selection

    # %% on_listWidget_ActiveApp
    def on_listWidget_ActiveApp(self, item):
        self.listWidget_Apps.clearSelection()
        selection = item.text()
        if selection != self.selection:
            self.selection = selection

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _check_filter_queue
    def _check_filter_queue(self):
        if self.awaiting_filter:
            self.awaiting_filter = False
            self.filter_task()

    # %% _store_data
    def _store_data(self):
        all_data = copy.deepcopy(self._data)
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
        if self.data is None:
            return
        self.data[0].append(event[0])
        self.data[1].append(event[1])
        self.data[2].append(event[2])
        self.update_activeapp()
        if (not self.filter_worker_active) and (self.selection == self.active_window):
            self.filter_task()
        elif self.selection == self.active_window:
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
        if self.database.get_icon(self.active_window) is None:
            icon = hactiveicon.get_active_window_icon(self.active_window)
            self.database.store_icon(self.active_window, icon)
            self.data
        self.populate_applist()
        self.label_Title.setText(self.selection)
        self.canvas.resize_event()

    # %% _init_axes
    def _init_axes(self):
        """Initialize the axes."""
        if self.axes:
            self.axes.remove()
        axes = self.figure.add_subplot()
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        self.background = self.canvas.copy_from_bbox(axes.bbox)
        self.axes = axes

        self.figure.tight_layout(pad=0.0)

    # %% _init_gui
    def _init_gui(self):
        """
        Initialize the GUI at the end of `__init__` method.
        """
        self._load_ui()
        # Load Window
        self.resize(2000, 1200)
        self.setWindowTitle("Heat Mouse")
        icon_loc = str(THIS_DIR.joinpath("images\\heatmouse.png"))
        self.setWindowIcon(QtGui.QIcon(icon_loc))
        self.widget_Canvas.layout().addWidget(self.canvas)
        self.stackedWidget.setCurrentIndex(0)
        # Load Toolbar
        icon_loc = str(THIS_DIR.joinpath("images\\play.png"))
        self.start_action = QtWidgets.QAction(QtGui.QIcon(icon_loc), "Start", self)
        self.start_action.triggered.connect(self.listener_task)
        self.toolBar.addAction(self.start_action)
        icon_loc = str(THIS_DIR.joinpath("images\\stop.png"))
        self.stop_action = QtWidgets.QAction(QtGui.QIcon(icon_loc), "Stop", self)
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.listener_stop)
        self.toolBar.addAction(self.stop_action)
        self.toolBar.addSeparator()
        self.label_FilterFactor = QtWidgets.QLabel("Gaussian\nFilter Factor:  ")
        self.toolBar.addWidget(self.label_FilterFactor)
        self.spinbox_FilterFactor = QtWidgets.QSpinBox()
        self.spinbox_FilterFactor.setMinimum(1)
        self.spinbox_FilterFactor.setMaximum(100)
        self.spinbox_FilterFactor.setValue(4)
        self.bins = 4
        self.spinbox_FilterFactor.valueChanged.connect(self.update_filter)
        self.toolBar.addWidget(self.spinbox_FilterFactor)
        self.toolBar.addSeparator()
        self.toolBar.setVisible(False)
        # Update styles
        QtGui.QFontDatabase.addApplicationFont(
            str(THIS_DIR.joinpath("resources\\PublicPixel.ttf"))
        )
        font = QtGui.QFont("Public Pixel", 14)
        self.label_Title.setFont(font)
        self.button_Start.setFont(font)
        self.centralwidget.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralwidget.setStyleSheet("background-color: white")
        # Set delegate and populate application list
        delegate = hlistitemdelegate.ListItemDelegate(self.listWidget_Apps)
        self.listWidget_Apps.setItemDelegate(delegate)
        self.listWidget_Apps.itemClicked.connect(self.on_listWidget_Apps)
        delegate = hlistitemdelegate.ListItemDelegate(self.listWidget_ActiveApp)
        self.listWidget_ActiveApp.setItemDelegate(delegate)
        self.listWidget_ActiveApp.itemClicked.connect(self.on_listWidget_ActiveApp)
        self.populate_applist()
        self.resizeEvent(None)
        # Initialize axes
        self._init_axes()

    # %% _load_ui
    def _load_ui(self):
        ui_path = THIS_DIR.joinpath("heatmouse.ui")
        uic.loadUi(str(ui_path), self)
