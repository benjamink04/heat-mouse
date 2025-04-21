"""
The item delegate class used by Heat Mouse to adjust the design of application items.

Classes
-------
ListItemDelegate
    Creates the custom list item.
"""

# %% --- Imports -----------------------------------------------------------------------
from PyQt5 import QtCore, QtGui, QtWidgets

# %% --- Constants ---------------------------------------------------------------------
# %% DESC_ROLE
DESC_ROLE = QtCore.Qt.UserRole + 1


# %% --- Classes -----------------------------------------------------------------------
# %% ListItemDelegate
class ListItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    Creates the custom list item.

    Methods
    -------
    paint
        Stylize the item.
    sizeHint
        Calculate the size needed for the item.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self, parent=None):
        super().__init__(parent)
        # Define icon size, margins, and spacing.
        self.iconSize = QtCore.QSize(32, 32)
        self.margin = 5
        self.textSpacing = 2

    # %% --- Methods -------------------------------------------------------------------
    # %% paint
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        """
        Stylize the item.

        Returns
        -------
        QtGui.QPainter
            The item QPainter object.
        """
        painter.save()
        # Draw background (highlight if selected)
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, QtGui.QColor(255, 255, 0, 100))
        # Get the icon, title, and description
        icon = index.data(QtCore.Qt.DecorationRole)
        title = index.data(QtCore.Qt.DisplayRole)
        description = index.data(DESC_ROLE)
        # Define the layout rectangles
        iconRect = QtCore.QRect(
            option.rect.left() + self.margin,
            option.rect.top() + (option.rect.height() - self.iconSize.height()) // 2,
            self.iconSize.width(),
            self.iconSize.height(),
        )
        # Text area starts to the right of the icon
        textLeft = iconRect.right() + self.margin
        textRect = QtCore.QRect(
            textLeft,
            option.rect.top() + self.margin,
            option.rect.width() - textLeft - self.margin,
            option.rect.height() - 2 * self.margin,
        )
        # Draw the icon
        if icon:
            icon.paint(painter, iconRect, QtCore.Qt.AlignCenter)
        # Draw the title (bold)
        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        painter.setFont(titleFont)
        titleRect = QtCore.QRect(
            textRect.left(),
            textRect.top(),
            textRect.width(),
            option.fontMetrics.height(),
        )
        painter.drawText(titleRect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, title)
        # Draw the description (regular font, below the title)
        descFont = QtGui.QFont()
        painter.setFont(descFont)
        descRect = QtCore.QRect(
            textRect.left(),
            titleRect.bottom() + self.textSpacing,
            textRect.width(),
            option.fontMetrics.height(),
        )
        painter.setPen(QtGui.QColor(100, 100, 100))  # Slightly gray for description
        painter.drawText(
            descRect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, description
        )
        painter.restore()

    # %% sizeHint
    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ):
        """
        Calculate the size needed for the item.

        Returns
        -------
        QtCore.QSize
            The item QSize object.
        """
        title = index.data(QtCore.Qt.DisplayRole)
        description = index.data(DESC_ROLE)
        # Font for title (bold)
        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFontMetrics = QtGui.QFontMetrics(titleFont)
        # Font metrics for description (regular)
        descFont = option.font
        descMetrics = QtGui.QFontMetrics(descFont)
        # Calculate width and height
        titleWidth = titleFontMetrics.boundingRect(title).width()
        descWidth = descMetrics.boundingRect(description).width()
        textWidth = max(titleWidth, descWidth)
        # Height: icon height + title height + description height + margins
        titleHeight = titleFontMetrics.height()
        descHeight = descMetrics.height()
        self.totalHeight = titleHeight + self.textSpacing + descHeight + 2 * self.margin
        # Width: icon width + text width + margins
        self.totalWidth = (
            self.iconSize.width() + self.margin + textWidth + 2 * self.margin
        )
        return QtCore.QSize(
            self.totalWidth,
            max(self.iconSize.height() + 2 * self.margin, self.totalHeight),
        )
