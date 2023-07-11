import abc
import copy
import math
from typing import List

from PyQt6.QtWidgets import QLabel, QInputDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QMouseEvent
from PyQt6.QtCore import QRect, Qt


class AnnotationList(object):
    def __init__(self) -> None:
        self.annotations = []

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, index):
        if index is None or index < 0 or index >= len(self.annotations):
            return None
        return self.annotations[index]

    def add(self, annotation, index=None):
        if index is None:
            self.annotations.append(annotation)
        else:
            self.annotations.insert(index, annotation)

    def batch_add(self, annotations, index=None):
        if index is None:
            self.annotations.extend(annotations)
        else:
            self.annotations = self.annotations[:index] + annotations + self.annotations[index:]

    def remove(self, index):
        if index is None:
            deleted = self.annotations.pop()
        else:
            deleted = self.annotations.pop(index)
        return deleted

    def batch_remove(self, count, index=None):
        if index is None:
            deleted = self.annotations[-count:]
            self.annotations = self.annotations[:-count]
        else:
            deleted = self.annotations[index:index + count]
            self.annotations = self.annotations[:index] + self.annotations[index + count:]
        return deleted

    def remove_all(self):
        deleted = copy.deepcopy(self.annotations)
        self.annotations.clear()
        return deleted


class Command(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def undo(self):
        pass


class AddAnnotationCommand(Command):
    def __init__(self, annotation_list: AnnotationList, annotation=None, index=None):
        self.annotation_list = annotation_list
        self.annotation = annotation
        self.index = index

    def execute(self):
        self.annotation_list.add(self.annotation, self.index)

    def undo(self):
        self.annotation_list.remove(self.index)


class DeleteAnnotationCommand(Command):
    def __init__(self, annotation_list: AnnotationList, index=None):
        self.annotation_list = annotation_list
        self.index = index
        self.annotation = None

    def execute(self):
        self.annotation = self.annotation_list.remove(self.index)

    def undo(self):
        self.annotation_list.add(self.annotation, self.index)


class DeleteAllAnnotationCommand(Command):
    def __init__(self, annotation_list: AnnotationList):
        self.annotation_list = annotation_list
        self.annotations = None

    def execute(self):
        self.annotations = self.annotation_list.remove_all()

    def undo(self):
        self.annotation_list.batch_add(self.annotations)


class BatchAddAnnotationCommand(Command):
    def __init__(self, annotation_list: AnnotationList, annotations=None, index=None):
        self.annotation_list = annotation_list
        self.annotations = annotations
        self.index = index

    def execute(self):
        self.annotation_list.batch_add(self.annotations, self.index)

    def undo(self):
        self.annotation_list.batch_remove(self.index, len(self.annotations))


class BatchDeleteAnnotationCommand(Command):
    def __init__(self, annotation_list: AnnotationList, count: int, index: int = None):
        self.annotation_list = annotation_list
        self.index = index
        self.count = count
        self.annotations = None

    def execute(self):
        self.annotations = self.annotation_list.batch_remove(self.count, self.index)

    def undo(self):
        self.annotation_list.batch_add(self.annotations, self.index)


class AnnoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pos = None
        self.selected_annotation_index = None
        self.annotation_type = 'rectangle'
        self.show_text = False
        self.annotation = None
        self.annotation_list = AnnotationList()
        self.history: List[Command] = []
        self.undo_history: List[Command] = []
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
        if len(self.annotation_list) > 0:
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(0, 255, 0))
            painter.setPen(pen)
            for i in range(len(self.annotation_list)):
                self.paint_annotation(painter, self.annotation_list[i])
        if self.annotation is not None:
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(255, 0, 0))
            painter.setPen(pen)
            self.paint_annotation(painter, self.annotation)
        if self.selected_annotation_index is not None:
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(255, 255, 0))
            painter.setPen(pen)
            self.paint_annotation(painter, self.annotation_list[self.selected_annotation_index])
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
                self.add_annotation(self.annotation)
                self.annotation = None
        if event.button() == Qt.MouseButton.RightButton:
            if self.annotation is not None:
                self.annotation = None
            else:
                x = event.pos().x()
                y = event.pos().y()
                if self.selected_annotation_index is not None:
                    self.delete_annotation(self.selected_annotation_index)
                    self.selected_annotation_index = self.find_nearest_annotation(x, y)
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
        if event.button() == Qt.MouseButton.NoButton:
            x = event.pos().x()
            y = event.pos().y()
            nearest = self.find_nearest_annotation(x, y)
            self.selected_annotation_index = nearest
        self.current_pos = event.pos()
        self.update()
        return super().mouseMoveEvent(event)

    def notify(self):
        if self.on_annotation_updated is not None:
            self.on_annotation_updated(self.annotation_list.annotations)

    def init_annotations(self, annotations):
        self.annotation_list.remove_all()
        self.annotation_list.batch_add(annotations)
        self.history = []
        self.undo_history = []
        self.annotation = None
        self.notify()
        self.update()

    def execute_command(self, command: Command):
        command.execute()
        self.history.append(command)
        self.undo_history.clear()
        self.notify()
        self.update()

    def undo(self):
        if len(self.history) == 0:
            return
        command = self.history.pop()
        command.undo()
        self.undo_history.append(command)
        self.notify()
        self.update()

    def redo(self):
        if len(self.undo_history) == 0:
            return
        command = self.undo_history.pop()
        command.execute()
        self.history.append(command)
        self.notify()
        self.update()

    def add_annotation(self, annotation):
        command = AddAnnotationCommand(self.annotation_list, annotation)
        self.execute_command(command)

    def batch_add_annotation(self, annotations):
        command = BatchAddAnnotationCommand(self.annotation_list, annotations)
        self.execute_command(command)

    def delete_annotation(self, index):
        command = DeleteAnnotationCommand(self.annotation_list, index)
        self.execute_command(command)

    def delete_all_annotation(self):
        command = DeleteAllAnnotationCommand(self.annotation_list)
        self.execute_command(command)

    @staticmethod
    def paint_annotation(painter: QPainter, annotation):
        if annotation is None:
            return
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

    def find_nearest_annotation(self, x, y):
        nearest = None
        nearest_d = float('inf')
        for i in range(len(self.annotation_list)):
            annotation = self.annotation_list[i]
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
        return nearest
