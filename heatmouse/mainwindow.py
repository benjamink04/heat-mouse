"""
The Main Window class used by Heat Mouse to generate the GUI.

Classes
-------
HeatMouseMainWindow
    Generates the main window object for Heat Mouse.
"""

# %% --- Imports -----------------------------------------------------------------------
import copy
import ctypes
import pathlib
from collections import Counter

import matplotlib
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
    """
    Generates the main window object for Heat Mouse.

    Properties
    ----------
    active_window : str
        Get the active window name.
    bins : tuple[np.array, np.array]
        Get the histogram bin sizes, based on the chosen Gaussian filter factor.
    canvas : mqt5agg.FigureCanvasQTAgg
        Get the canvas for the figure.
    data : tuple[list, list, list]
        Get the Heat Mouse click data for a specific application.
    database : hdatabase.Database
        Get the Heat Mouse database class object.
    db_data : dict[str : tuple[list, list, list]]
        Get the stored data from the Heat Mouse database. Used to update the data
        property and compare against new click data.
    figure : mfigure.Figure
        Get the main window figure for drawing.
    screensize : tuple[int, int]
        Get the active monitor screen size.
    selection : str
        Get the selected application to display data.

    Methods
    -------
    closeEvent
        Override closeEvent to close active threads and the sql database.
    draw
        Draw updated heatmap on the canvas.
    filter_task
        Init a worker thread to filter data and prepare it for plotting.
    listener_stop
        Stop the listener thread.
    listener_task
        Init a worker thread to listen for mouse clicks on the system.
    on_button_Start_clicked
        Connect button_Start widget to start the listener worker.
    on_listWidget_Apps
        Connect the listWidget_Apps widget to click events.
    on_listWidget_ActiveApp
        Connect the on_listWidget_ActiveApp widget to click events.
    resizeEvent
        Override the resizeEvent to update the listWidget sizes.
    update_filter
        Update the filter on Gaussian filter factor changes.

    Protected Methods
    -----------------
    _check_filter_queue
        Check if filter task has a request in the queue.
    _init_axes
        Initialize the axes.
    _init_figure
        Initialize the figure.
    _init_gui
        Initialize the GUI at the end of `__init__` method.
    _load_ui
        Load the ui file for the GUI.
    _populate_applist
        Populate the list widgets with application data.
    _show_error_message
        Displays an error message in a pop-up dialog.
    _store_data
        Separate new data from existing data and store it in the database.
    _update_activeapp
        Update the data points value for the active application.
    _update_data
        Update the data property with new click data.
    _window_change
        Update the data, GUI, and plot window upon active window change.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        self._active_window: str = None
        self._bins: tuple[np.array, np.array] = None
        self._canvas: mqt5agg.FigureCanvasQTAgg = None
        self._data: dict[str : tuple[list, list, list]] = None
        self._database: hdatabase.Database = None
        self._db_data: dict[str : tuple[list, list, list]] = None
        self._figure: mfigure.Figure = None
        self._screensize: tuple[int, int] = None
        self._selection: str = None
        self.awaiting_filter: bool = False
        self.axes: maxes.Axes = None
        self.background: matplotlib.backends._backend_agg.BufferRegion = None
        self.filter_worker: hthreadworker.FilterWorker = None
        self.filter_worker_active: bool = False
        self.heatmap: np.histogram2d = None
        self.listener_worker: hthreadworker.ListenerWorker = None
        self.threadpool: QtCore.QThreadPool = QtCore.QThreadPool()
        super().__init__()

        self._init_gui()

    # %% --- Properties ----------------------------------------------------------------
    # %% active_window
    @property
    def active_window(self) -> str:
        """
        Get the active window name.

        Returns
        -------
        str
            Active window name.
        """
        return self._active_window

    @active_window.setter
    def active_window(self, window):
        if (window != self._active_window) and (window is not None) and (window != ""):
            self._active_window = window.replace("'", "")
            self._window_change()

    # %% bins
    @property
    def bins(self) -> tuple[np.array, np.array]:
        """
        Get the histogram bin sizes, based on the chosen Gaussian filter factor.

        Returns
        -------
        tuple[np.array, np.array]
            2D bin stored as (X, Y).
        """
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

    # %% canvas
    @property
    def canvas(self) -> mqt5agg.FigureCanvasQTAgg:
        """
        Get the canvas for the figure.

        Returns
        -------
        mqt5agg.FigureCanvasQTAgg
            Canvas for the figure.
        """
        if self._canvas is None:
            self._canvas = mqt5agg.FigureCanvasQTAgg(self.figure)
        return self._canvas

    # %% data
    @property
    def data(self) -> tuple[list, list, list]:
        """Get the Heat Mouse click data for a specific application.

        Returns
        -------
        tuple[list, list, list]
            Tuple stored as (X-Position, Y-Position, Button).
        """
        if self._data is None:
            self._data = copy.deepcopy(self.db_data)
        try:
            return self._data[self.active_window]
        except KeyError:
            if self.active_window is None:
                return None
            self._data[self.active_window] = ([], [], [])
            return self._data[self.active_window]

    # %% database
    @property
    def database(self) -> hdatabase.Database:
        """
        Get the Heat Mouse database class object.

        Returns
        -------
        hdatabase.Database
            Heat Mouse database class object.
        """
        if self._database is None:
            self._database = hdatabase.Database()
        return self._database

    # %% db_data
    @property
    def db_data(self) -> dict[str : tuple[list, list, list]]:
        """
        Get the stored data from the Heat Mouse database.

        Used to update the data property and compare against new click data.

        Returns
        -------
        dict[str : tuple[list, list, list]]
            Dictionary stored as: {Application-Name: (X-Position, Y-Position, Button)}
        """
        if self._db_data is None:
            self._db_data = self.database.get_all_data()
        return self._db_data

    # %% figure
    @property
    def figure(self) -> mfigure.Figure:
        """
        Get the main window figure for drawing.

        Returns
        -------
        mfigure.Figure
            Main window figure.
        """
        if self._figure is None:
            self._figure = mfigure.Figure()
        return self._figure

    # %% screensize
    @property
    def screensize(self) -> tuple[int, int]:
        """
        Get the active monitor screen size.

        Returns
        -------
        tuple[int, int]
            Screensize tuple stored as (X, Y).
        """
        if self._screensize is None:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            self._screensize = (
                user32.GetSystemMetrics(0),
                user32.GetSystemMetrics(1),
            )
        return self._screensize

    # %% selection
    @property
    def selection(self) -> str:
        """
        Get the selected application to display data.

        Returns
        -------
        str
            Selected application name.
        """
        return self._selection

    @selection.setter
    def selection(self, window):
        if (window != self._selection) and (window is not None) and (window != ""):
            self._selection = window
            self._window_change()
            self.filter_task()

    # %% --- Methods -------------------------------------------------------------------
    # %% closeEvent
    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Override closeEvent to close active threads and the sql database.

        Arguments
        ---------
        event: QtGui.QCloseEvent
            The window close event.
        """
        try:
            self.listener_worker.stop()
            self.filter_worker.stop()
        except AttributeError:
            pass
        self._store_data()
        self.database.connection.close()
        event.accept()

    # %% draw
    def draw(self, heatmap: np.histogram2d):
        """
        Draw updated heatmap on the canvas.

        Arguments
        ---------
        heatmap: np.histogram2d
            Filtered histogram data.
        """
        self.filter_worker_active = False
        self.heatmap = heatmap
        self.canvas.restore_region(self.background)
        self.axes.draw_artist(self.heatmap)
        self.canvas.blit(self.axes.bbox)

    # %% filter_task
    def filter_task(self):
        """Init a worker thread to filter data and prepare it for plotting."""
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

    # %% listener_stop
    def listener_stop(self):
        """Stop the listener thread."""
        self.listener_worker.stop()
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)

    # %% listener_task
    def listener_task(self):
        """Init a worker thread to listen for mouse clicks on the system."""
        self.listener_worker = hthreadworker.ListenerWorker()
        self.listener_worker.signals.update.connect(self._update_data)
        self.listener_worker.signals.error.connect(self._show_error_message)
        self.threadpool.start(self.listener_worker)
        # Update GUI to listening-mode
        self.selection = "Heat Mouse"
        self.active_window = "Heat Mouse"
        self.filter_task()
        self.stackedWidget.setCurrentIndex(1)
        self.listWidget_ActiveApp.setCurrentRow(0)
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.toolBar.setVisible(True)

    # %% on_button_Start_clicked
    @QtCore.pyqtSlot()
    def on_button_Start_clicked(self):
        """Connect button_Start widget to start the listener worker."""
        self.listener_task()

    # %% on_listWidget_Apps
    def on_listWidget_Apps(self, item: QtWidgets.QListWidgetItem):
        """
        Connect the listWidget_Apps widget to click events.

        Arguments
        ---------
        item: QtWidgets.QListWidgetItem
            The selected list widget item.
        """
        self.listWidget_ActiveApp.clearSelection()
        selection = item.text()
        if selection != self.selection:
            self.selection = selection

    # %% on_listWidget_ActiveApp
    def on_listWidget_ActiveApp(self, item: QtWidgets.QListWidgetItem):
        """
        Connect the on_listWidget_ActiveApp widget to click events.

        Arguments
        ---------
        item: QtWidgets.QListWidgetItem
            The selected list widget item.
        """
        self.listWidget_Apps.clearSelection()
        selection = item.text()
        if selection != self.selection:
            self.selection = selection

    # %% resizeEvent
    def resizeEvent(self, event: QtGui.QResizeEvent):
        """
        Override the resizeEvent to update the listWidget sizes.

        Arguments
        ---------
        event: QtGui.QResizeEvent
            The window resize event.
        """
        try:
            height = self.listWidget_ActiveApp.itemDelegate().totalHeight
        except AttributeError:
            return
        self.listWidget_ActiveApp.setFixedSize(
            self.listWidget_ActiveApp.sizeHint().width(),
            height + 2,
        )

    # %% update_filter
    def update_filter(self, value: int):
        """
        Update the filter on Gaussian filter factor changes.

        Arguments
        ---------
        value: int
            The selected Gaussian filter value.
        """
        self.bins = value
        if not self.filter_worker_active:
            self.filter_task()
        else:
            self.awaiting_filter = True

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _check_filter_queue
    def _check_filter_queue(self):
        """Check if filter task has a request in the queue."""
        if self.awaiting_filter:
            self.awaiting_filter = False
            self.filter_task()

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

    # %% _init_figure
    def _init_figure(self):
        """Initialize the figure."""
        self.figure.tight_layout(pad=0.0)

    # %% _init_gui
    def _init_gui(self):
        """Initialize the GUI at the end of `__init__` method."""
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
        self._populate_applist()
        self.resizeEvent(None)
        # Initialize axes and figure
        self._init_axes()
        self._init_figure()

    # %% _load_ui
    def _load_ui(self):
        """Load the ui file for the GUI."""
        ui_path = THIS_DIR.joinpath("heatmouse.ui")
        uic.loadUi(str(ui_path), self)

    # %% _populate_applist
    def _populate_applist(self):
        """Populate the list widgets with application data."""
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

    # %% _show_error_message
    def _show_error_message(self, message: str):
        """
        Displays an error message in a pop-up dialog.

        Arguments
        ---------
        message: str
            The error message.
        """
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    # %% _store_data
    def _store_data(self):
        """Separate new data from existing data and store it in the database."""
        all_data = copy.deepcopy(self._data)
        for key, table_data in self.db_data.items():
            new_data = []
            for all_col, db_col in zip(all_data[key], table_data):
                new_data.append(list((Counter(all_col) - Counter(db_col)).elements()))
            all_data[key] = tuple(new_data)
        self.database.store_all_data(all_data)

    # %% _update_activeapp
    def _update_activeapp(self):
        """Update the data points value for the active application."""
        item = self.listWidget_ActiveApp.item(0)
        item.setData(DESC_ROLE, f"Data points: {len(self.data[0])}")

    # %% _update_data
    def _update_data(self, values: tuple[str, tuple[int, int, str]]):
        """
        Update the data property with new click data.

        Arguments
        ---------
        values: tuple[str, tuple[int, int, str]]
            Click event values and application name to be stored in the database.
        """
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
        self._update_activeapp()
        if (not self.filter_worker_active) and (self.selection == self.active_window):
            self.filter_task()
        elif self.selection == self.active_window:
            self.awaiting_filter = True

    # %% _window_change
    def _window_change(self):
        """Update the data, GUI, and plot window upon active window change."""
        if self.database.get_icon(self.active_window) is None:
            icon = hactiveicon.get_active_window_icon(self.active_window)
            self.database.store_icon(self.active_window, icon)
            self.data
        self._populate_applist()
        self.label_Title.setText(self.selection)
        self.canvas.resize_event()
