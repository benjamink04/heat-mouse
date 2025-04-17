from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QColor, QFont, QFontMetrics
from PyQt5.QtWidgets import QStyle  # Import QStyle for state flags
from PyQt5.QtWidgets import QStyledItemDelegate

# Custom role to store description
DescriptionRole = Qt.UserRole + 1


class ListItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Define margins and spacing
        self.iconSize = QSize(32, 32)  # Size of the icon
        self.margin = 5  # Margin around the item
        self.textSpacing = 2  # Spacing between title and description

    def sizeHint(self, option, index):
        # Calculate the size needed for the item
        title = index.data(Qt.DisplayRole)  # The title text
        description = index.data(DescriptionRole)  # The description text

        # Font for title (bold)
        titleFont = QFont()
        titleFont.setBold(True)
        titleFontMetrics = QFontMetrics(
            titleFont
        )  # Create QFontMetrics for the bold font

        # Font metrics for description (regular)
        descFont = option.font
        descMetrics = QFontMetrics(descFont)

        # Calculate width and height
        titleWidth = titleFontMetrics.boundingRect(title).width()
        descWidth = descMetrics.boundingRect(description).width()
        textWidth = max(titleWidth, descWidth)

        # Height: icon height + title height + description height + margins
        titleHeight = titleFontMetrics.height()
        descHeight = descMetrics.height()
        self.totalHeight = titleHeight + self.textSpacing + descHeight + 2 * self.margin

        # Width: icon width + text width + margins
        totalWidth = self.iconSize.width() + self.margin + textWidth + 2 * self.margin

        return QSize(
            totalWidth, max(self.iconSize.height() + 2 * self.margin, self.totalHeight)
        )

    def paint(self, painter, option, index):
        painter.save()

        # Draw background (highlight if selected)
        if (
            option.state & QStyle.State_Selected
        ):  # Use QStyle.State_Selected instead of Qt.Selected
            painter.fillRect(
                option.rect, QColor(255, 255, 0, 100)
            )  # Yellow highlight with transparency

        # Get the icon, title, and description
        icon = index.data(Qt.DecorationRole)  # Icon
        title = index.data(Qt.DisplayRole)  # Title
        description = index.data(DescriptionRole)  # Description

        # Define the layout rectangles
        iconRect = QRect(
            option.rect.left() + self.margin,
            option.rect.top() + (option.rect.height() - self.iconSize.height()) // 2,
            self.iconSize.width(),
            self.iconSize.height(),
        )

        # Text area starts to the right of the icon
        textLeft = iconRect.right() + self.margin
        textRect = QRect(
            textLeft,
            option.rect.top() + self.margin,
            option.rect.width() - textLeft - self.margin,
            option.rect.height() - 2 * self.margin,
        )

        # Draw the icon
        if icon:
            icon.paint(painter, iconRect, Qt.AlignCenter)

        # Draw the title (bold)
        titleFont = QFont()
        titleFont.setBold(True)
        painter.setFont(titleFont)
        titleRect = QRect(
            textRect.left(),
            textRect.top(),
            textRect.width(),
            option.fontMetrics.height(),
        )
        painter.drawText(titleRect, Qt.AlignLeft | Qt.AlignTop, title)

        # Draw the description (regular font, below the title)
        descFont = QFont()
        painter.setFont(descFont)
        descRect = QRect(
            textRect.left(),
            titleRect.bottom() + self.textSpacing,
            textRect.width(),
            option.fontMetrics.height(),
        )
        painter.setPen(QColor(100, 100, 100))  # Slightly gray for description
        painter.drawText(descRect, Qt.AlignLeft | Qt.AlignTop, description)

        painter.restore()
