import math

from PyQt6.QtWidgets import QLabel, QInputDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QMouseEvent
from PyQt6.QtCore import QRect, Qt


class AnnoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pos = None
        self.annotation_type = 'rectangle'
        self.show_text = False
        self.annotation = None
        self.annotations = []
        self.redo_stack = []
        self.on_annotation_updated = None

    def paintEvent(self, event):
        ret = super().paintEvent(event)

        painter = QPainter(self)

        if self.current_pos is not None:
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(255, 255, 255, 128))
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(0, self.current_pos.y(), self.width(), self.current_pos.y())
            painter.drawLine(self.current_pos.x(), 0, self.current_pos.x(), self.height())

        if self.annotations is not None and len(self.annotations) > 0:
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(0, 255, 0))
            painter.setPen(pen)
            for annotation in self.annotations:
                self.paint_annotation(painter, annotation)
        if self.annotation is not None:
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(255, 0, 0))
            painter.setPen(pen)
            self.paint_annotation(painter, self.annotation)

        return ret

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            x = x / self.width()
            y = y / self.height()
            self.annotation = {
                'type': self.annotation_type,
                'x': x,
                'y': y,
                'x2': x,
                'y2': y
            }
        self.update()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.annotation is not None:
            x = event.pos().x()
            y = event.pos().y()
            x = max(0, min(x, self.width()))
            y = max(0, min(y, self.height()))
            x = x / self.width()
            y = y / self.height()
            self.annotation['x2'] = x
            self.annotation['y2'] = y
            if self.annotation['type'] != 'point':
                w = int(self.annotation['x2'] * self.width()) - int(self.annotation['x'] * self.width())
                h = int(self.annotation['y2'] * self.height()) - int(self.annotation['y'] * self.height())
                if math.sqrt(w ** 2 + h ** 2) < 5:
                    self.annotation = None
            if self.annotation is not None:
                if self.annotation['type'] == "rectangle":
                    self.annotation['x'], self.annotation['x2'] = sorted([self.annotation['x'], self.annotation['x2']])
                    self.annotation['y'], self.annotation['y2'] = sorted([self.annotation['y'], self.annotation['y2']])
                if self.show_text or event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    text, ok = QInputDialog.getText(self, "Input", "Please input text")
                    if ok:
                        self.annotation['text'] = text
                self.annotations.append(self.annotation)
                self.annotation = None
            self.redo_stack = []
            self.notify()
        if event.button() == Qt.MouseButton.RightButton:
            if self.annotation is not None:
                self.annotation = None
            else:
                x = event.pos().x()
                y = event.pos().y()
                nearest = None
                nearest_d = float('inf')
                for i, annotation in enumerate(self.annotations):
                    if annotation['type'] == 'point':
                        anno_x = int(annotation['x2'] * self.width())
                        anno_y = int(annotation['y2'] * self.height())
                        d = math.sqrt((x - anno_x) ** 2 + (y - anno_y) ** 2)
                        if d < 5:
                            if nearest_d > d:
                                nearest_d = d
                                nearest = i
                    elif annotation['type'] == 'circle':
                        anno_x = int(annotation['x'] * self.width())
                        anno_y = int(annotation['y'] * self.height())
                        anno_x2 = int(annotation['x2'] * self.width())
                        anno_y2 = int(annotation['y2'] * self.height())
                        r = int(math.sqrt((anno_x2 - anno_x) ** 2 + (anno_y2 - anno_y) ** 2))
                        d = math.sqrt((x - anno_x) ** 2 + (y - anno_y) ** 2)
                        if d < r:
                            if nearest_d > d:
                                nearest_d = d
                                nearest = i
                    elif annotation['type'] == 'rectangle':
                        anno_x = int(annotation['x'] * self.width())
                        anno_y = int(annotation['y'] * self.height())
                        anno_x2 = int(annotation['x2'] * self.width())
                        anno_y2 = int(annotation['y2'] * self.height())
                        if x >= anno_x and x <= anno_x2 and y >= anno_y and y <= anno_y2:
                            cx = (anno_x + anno_x2) / 2
                            cy = (anno_y + anno_y2) / 2
                            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                            if nearest_d > d:
                                nearest_d = d
                                nearest = i
                if nearest is not None:
                    self.redo_stack.append(self.annotations.pop(nearest))
                    self.notify()
        self.update()
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.annotation is not None:
            x = event.pos().x()
            y = event.pos().y()
            x = max(0, min(x, self.width()))
            y = max(0, min(y, self.height()))
            x = x / self.width()
            y = y / self.height()
            self.annotation['x2'] = x
            self.annotation['y2'] = y
        self.current_pos = event.pos()
        self.update()
        return super().mouseMoveEvent(event)

    def notify(self):
        if self.on_annotation_updated is not None:
            self.on_annotation_updated(self.annotations)

    def set_annotations(self, annotations):
        self.annotations = annotations
        self.redo_stack = []
        self.annotation = None
        self.notify()
        self.update()

    def add_annotations(self, annotations):
        self.set_annotations(self.annotations + annotations)

    def add_annotation(self, annotation):
        self.add_annotations([annotation])

    def undo(self):
        if len(self.annotations) > 0:
            self.redo_stack.append(self.annotations.pop())
            self.notify()
            self.update()

    def redo(self):
        if len(self.redo_stack) > 0:
            self.annotations.append(self.redo_stack.pop())
            self.notify()
            self.update()

    @staticmethod
    def paint_annotation(painter: QPainter, annotation):
        x = int(annotation['x'] * painter.window().width())
        y = int(annotation['y'] * painter.window().height())
        x2 = int(annotation['x2'] * painter.window().width())
        y2 = int(annotation['y2'] * painter.window().height())
        if annotation['type'] == 'point':
            painter.drawPoint(x2, y2)
        elif annotation['type'] == 'circle':
            painter.drawEllipse(x, y, x2 - x, y2 - y)
        elif annotation['type'] == 'rectangle':
            painter.drawRect(QRect(x, y, x2 - x, y2 - y))
        if 'text' in annotation and annotation['text'] != '':
            text = annotation['text']
            font = QFont("Microsoft YaHei")
            font.setPointSize(12)
            painter.setFont(font)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(text)
            foreground_color = painter.pen().color()
            background_color = QColor(255 - foreground_color.red(), 255 - foreground_color.green(), 255 - foreground_color.blue(), 128)
            if annotation["type"] == 'point':
                x = x - rect.width() // 2
                y = y - 5
            elif annotation["type"] == 'circle':
                radius = int(math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2))
                x = x - rect.width() // 2
                y = y - radius - 5
            elif annotation["type"] == 'rectangle':
                y = y - 5
            painter.fillRect(rect.translated(x, y), background_color)
            painter.drawText(x, y, text)
