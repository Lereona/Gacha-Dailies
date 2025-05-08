from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QTimer, QPoint, Signal

class RemovableListWidget(QListWidget):
    longPressed = Signal(QListWidgetItem)
    itemClickedForDelete = Signal(QListWidgetItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.timeout.connect(self._on_long_press)
        self._pressed_item = None
        self._pressed_pos = QPoint()
        self.delete_mode = False
        self._shake_timers = []
        self.setDragDropMode(QListWidget.NoDragDrop)
        self.setDragEnabled(False)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            self._pressed_item = item
            self._pressed_pos = event.pos()
            if not self.delete_mode:
                self._long_press_timer.start(1500)  # 1.5 seconds
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._long_press_timer.stop()
        if self.delete_mode:
            item = self.itemAt(event.pos())
            if item:
                self.itemClickedForDelete.emit(item)
        self._pressed_item = None
        # Disable drag after reordering
        self.setDragDropMode(QListWidget.NoDragDrop)
        self.setDragEnabled(False)
        super().mouseReleaseEvent(event)

    def _on_long_press(self):
        if self._pressed_item and not self.delete_mode:
            self.longPressed.emit(self._pressed_item)

    def set_delete_mode(self, enabled):
        self.delete_mode = enabled
        self.setDragEnabled(not enabled)
        if enabled:
            self.start_shake()
        else:
            self.stop_shake()

    def enable_reorder_mode(self):
        if not self.delete_mode:
            self.setDragDropMode(QListWidget.InternalMove)
            self.setDragEnabled(True)
            self.setDefaultDropAction(Qt.MoveAction)

    def start_shake(self):
        for i in range(self.count()):
            item_widget = self.itemWidget(self.item(i))
            if not item_widget:
                item_widget = self.visualItemRect(self.item(i))
            timer = QTimer(self)
            timer.timeout.connect(lambda i=i: self._shake_item(i))
            timer.start(80 + (i % 3) * 20)
            self._shake_timers.append(timer)

    def stop_shake(self):
        for timer in self._shake_timers:
            timer.stop()
        self._shake_timers.clear()
        self.viewport().update()

    def _shake_item(self, i):
        self.viewport().update(self.visualItemRect(self.item(i)))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.delete_mode:
            from PySide6.QtGui import QPainter
            painter = QPainter(self.viewport())
            for i in range(self.count()):
                rect = self.visualItemRect(self.item(i))
                offset = 2 * ((i % 2) * 2 - 1)
                painter.save()
                painter.translate(rect.center())
                painter.rotate(offset)
                painter.translate(-rect.center())
                painter.restore() 