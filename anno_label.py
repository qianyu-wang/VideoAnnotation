import abc
import copy
import math
from typing import List

from PySide6.QtWidgets import QLabel, QInputDialog, QColorDialog
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QMouseEvent, QImage, QPixmap, QPainterPath
from PySide6.QtCore import QRect, QPoint, Qt


DEFAULT_COLOR = QColor(255, 0, 0, 255).name(QColor.NameFormat.HexArgb)
DEFAULT_TEXT_COLOR = QColor(255, 255, 0, 255).name(QColor.NameFormat.HexArgb)
DEFAULT_FONT_NAME = "Microsoft YaHei"
DEFAULT_FONT_SIZE = 0.04
DEFAULT_THICKNESS = 0.005


def to_color(color):
    if isinstance(color, str):
        return QColor.fromString(color)
    elif isinstance(color, list):
        return QColor(*color)
    elif isinstance(color, tuple):
        return QColor(*color)
    else:
        return QColor(color)


class AnnotationList(object):
    def __init__(self) -> None:
        self.annotations = []

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, index):
        if index is None or index < 0 or index >= len(self.annotations):
            return None
        return self.annotations[index]

    def __setitem__(self, index, annotation):
        if index is None or index < 0 or index >= len(self.annotations):
            return
        self.annotations[index] = annotation

    def add(self, annotation, index=None):
        if index is None:
            self.annotations.append(annotation)
        else:
            self.annotations.insert(index, annotation)

    def batch_add(self, annotations, index=None):
        if index is None:
            self.annotations.extend(annotations)
        else:
            self.annotations = (
                self.annotations[:index] + annotations + self.annotations[index:]
            )

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
            deleted = self.annotations[index : index + count]
            self.annotations = (
                self.annotations[:index] + self.annotations[index + count :]
            )
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
    def __init__(self, annotation_list: AnnotationList, annotation, index=None):
        self.annotation_list = annotation_list
        self.annotation = annotation
        self.index = index

    def execute(self):
        self.annotation_list.add(self.annotation, self.index)

    def undo(self):
        self.annotation_list.remove(self.index)


class ModifyAnnotationCommand(Command):
    def __init__(self, annotation_list: AnnotationList, annotation, index):
        self.annotation_list = annotation_list
        self.annotation = annotation
        self.index = index
        self.old_annotation = None

    def execute(self):
        self.old_annotation = self.annotation_list[self.index]
        self.annotation_list[self.index] = self.annotation

    def undo(self):
        self.annotation_list[self.index] = self.old_annotation


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
        self.annotation_type = "rectangle"
        self.annotation = None
        self.annotation_list = AnnotationList()
        self.label = ""
        self.history: List[Command] = []
        self.undo_history: List[Command] = []
        self.on_annotation_updated = None
        self.font_name = DEFAULT_FONT_NAME
        self.font_size = DEFAULT_FONT_SIZE  # 占图片高度的比例
        self.color = QColor(0, 255, 0, 255).name(QColor.NameFormat.HexArgb)
        self.fill_color = QColor(0, 255, 0, 0).name(QColor.NameFormat.HexArgb)
        self.thickness = DEFAULT_THICKNESS
        self.text_color = QColor(255, 255, 0, 255).name(QColor.NameFormat.HexArgb)
        self.label_fill_color = QColor(255, 255, 0, 0).name(QColor.NameFormat.HexArgb)
        self.mouse_font = QFont(DEFAULT_FONT_NAME)
        self.image = None
        self.image_region = [0, 0, 1, 1]  # [x, y, w, h]
        self.image_region_changed = False
        self.start_move_pos = None

    def set_image(self, image: QImage):
        if self.image != image:
            self.image = image
            self.image_region = [0, 0, 1, 1]  # [x, y, w, h]
            self.image_region_changed = True
            self.start_move_pos = None

    def update_image(self):
        if self.image is None or self.image.width() == 0 or self.image.height() == 0:
            return
        regioned_image = self.image.copy(
            int(self.image.width() * self.image_region[0]),
            int(self.image.height() * self.image_region[1]),
            int(self.image.width() * self.image_region[2]),
            int(self.image.height() * self.image_region[3]),
        )
        pixmap = QPixmap.fromImage(
            regioned_image.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.setPixmap(pixmap)

    def paintEvent(self, event):
        ret = super().paintEvent(event)
        if self.image is None:
            return ret
        if self.image_region_changed:
            self.update_image()
            self.image_region_changed = False
        painter = QPainter()
        painter.begin(self)
        if self.current_pos is not None:
            pen = QPen()
            pen.setWidth(2)
            pen.setColor(QColor(255, 255, 255, 128))
            pen.setWidth(int(DEFAULT_THICKNESS * painter.window().height()))
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(
                0, self.current_pos.y(), self.width(), self.current_pos.y()
            )
            painter.drawLine(
                self.current_pos.x(), 0, self.current_pos.x(), self.height()
            )
            x = int(((self.current_pos.x() / self.width()) * self.image_region[2] + self.image_region[0]) * self.image.width())
            y = int(((self.current_pos.y() / self.height()) * self.image_region[3] + self.image_region[1]) * self.image.height())
            text = f"({x},{y})"
            pen.setColor(QColor(255, 255, 255, 255))
            pen.setWidth(2)
            painter.setPen(pen)
            self.mouse_font.setPixelSize(int(painter.window().height() * DEFAULT_FONT_SIZE))
            painter.setFont(self.mouse_font)
            metrics = QFontMetrics(self.mouse_font)
            rect = metrics.boundingRect(text)
            x = self.current_pos.x() + 5
            y = self.current_pos.y() + rect.height() - metrics.descent() + 5
            if x + rect.width() > self.width():
                x = self.current_pos.x() - rect.width() - 5
            if y > self.height():
                y = self.current_pos.y() - rect.height() - metrics.descent() - 5
            painter.drawText(x, y, text)
        if self.selected_annotation_index is not None:
            annotation = copy.deepcopy(
                self.annotation_list[self.selected_annotation_index]
            )
            thickness = annotation.get("thickness", self.thickness)
            for key in [
                "text", "color", "fill_color", "thickness", "text_color", "text_fill_color", "font_name", "font_size"
            ]:
                if key in annotation:
                    del annotation[key]
            annotation["color"] = QColor(255, 255, 255, 255).name(QColor.NameFormat.HexArgb)
            annotation["thickness"] = thickness * 2
            self.paint_annotation(
                painter,
                annotation,
                region=self.image_region,
                status="drawing",
                default_color=self.color,
                default_text_color=self.text_color,
                default_thickness=self.thickness,
                default_font=self.font_name,
                default_font_size=self.font_size,
            )
        if len(self.annotation_list) > 0:
            pen = QPen()
            pen.setWidth(int(self.thickness * painter.window().height()))
            pen.setColor(QColor.fromString(self.color))
            painter.setPen(pen)
            if self.annotation is not None:
                status = "drawing other"
            else:
                status = None
            for i in range(len(self.annotation_list)):
                self.paint_annotation(
                    painter,
                    self.annotation_list[i],
                    region=self.image_region,
                    status=status,
                    default_color=self.color,
                    default_text_color=self.text_color,
                    default_thickness=self.thickness,
                    default_font=self.font_name,
                    default_font_size=self.font_size,
                )
        if self.annotation is not None:
            pen = QPen()
            pen.setWidth(int(self.thickness * painter.window().height()))
            pen.setColor(QColor.fromString(self.color))
            painter.setPen(pen)
            self.paint_annotation(
                painter,
                self.annotation,
                region=self.image_region,
                status="drawing",
                default_color=self.color,
                default_text_color=self.text_color,
                default_thickness=self.thickness,
                default_font=self.font_name,
                default_font_size=self.font_size,
            )
        painter.end()
        return ret

    def wheelEvent(self, event):
        if self.annotation is None and self.start_move_pos is None:
            if self.current_pos is not None:
                x = self.current_pos.x()
                y = self.current_pos.y()
            else:
                x = self.width() // 2
                y = self.height() // 2
            x = (x / self.width()) * self.image_region[2] + self.image_region[0]
            y = (y / self.height()) * self.image_region[3] + self.image_region[1]
            w = self.image_region[2]
            h = self.image_region[3]
            if event.angleDelta().y() > 0:
                w *= 0.9
                h *= 0.9
            else:
                w *= 1.1
                h *= 1.1
            w = max(0.1, min(w, 1))
            h = max(0.1, min(h, 1))
            x = x - (x - self.image_region[0]) / self.image_region[2] * w
            y = y - (y - self.image_region[1]) / self.image_region[3] * h
            self.image_region[0] = max(0, min(x, 1 - w))
            self.image_region[1] = max(0, min(y, 1 - h))
            self.image_region[2] = w
            self.image_region[3] = h
            self.image_region_changed = True
            self.update()
        return super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            x = (x / self.width()) * self.image_region[2] + self.image_region[0]
            y = (y / self.height()) * self.image_region[3] + self.image_region[1]
            x = max(0, min(x, 1))
            y = max(0, min(y, 1))
            self.annotation = {
                "type": self.annotation_type,
                "x": x,
                "y": y,
                "x2": x,
                "y2": y,
            }
        elif event.button() == Qt.MouseButton.MiddleButton:
            if self.annotation is None and self.start_move_pos is None:
                self.start_move_pos = event.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.annotation is not None:
            x = event.pos().x()
            y = event.pos().y()
            x = (x / self.width()) * self.image_region[2] + self.image_region[0]
            y = (y / self.height()) * self.image_region[3] + self.image_region[1]
            x = max(0, min(x, 1))
            y = max(0, min(y, 1))
            self.annotation["x2"] = x
            self.annotation["y2"] = y
            if self.annotation["type"] != "point":
                w = int((self.annotation["x2"] - self.annotation["x"]) * self.image.width())
                h = int((self.annotation["y2"] - self.annotation["y"]) * self.image.height())
                if w**2 + h**2 < 4**2:  # 小于4像素的annotation忽略
                    self.annotation = None
                    if self.selected_annotation_index is not None:
                        # 按住Ctrl修改选中的annotation的text
                        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                            text, ok = QInputDialog.getText(
                                self,
                                "Input",
                                "Please input text",
                                text=self.annotation_list[
                                    self.selected_annotation_index
                                ].get("text", ""),
                            )
                            if ok:
                                new_annotation = copy.deepcopy(
                                    self.annotation_list[self.selected_annotation_index]
                                )
                                new_annotation["text"] = text
                                self.execute_command(
                                    ModifyAnnotationCommand(
                                        self.annotation_list,
                                        new_annotation,
                                        self.selected_annotation_index,
                                    )
                                )
                        # 按住Alt修改选中的annotation的颜色
                        elif event.modifiers() == Qt.KeyboardModifier.AltModifier:
                            color = self.annotation_list[
                                self.selected_annotation_index
                            ].get("color", self.color)
                            color = QColorDialog.getColor(
                                initial=to_color(color),
                                parent=self,
                            )
                            if color.isValid():
                                new_annotation = copy.deepcopy(
                                    self.annotation_list[self.selected_annotation_index]
                                )
                                new_annotation["color"] = color.name(QColor.NameFormat.HexArgb)
                                self.execute_command(
                                    ModifyAnnotationCommand(
                                        self.annotation_list,
                                        new_annotation,
                                        self.selected_annotation_index,
                                    )
                                )
            if self.annotation is not None:
                if self.annotation["type"] in ["rectangle", "text"]:
                    self.annotation["x"], self.annotation["x2"] = sorted(
                        [self.annotation["x"], self.annotation["x2"]]
                    )
                    self.annotation["y"], self.annotation["y2"] = sorted(
                        [self.annotation["y"], self.annotation["y2"]]
                    )
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    text, ok = QInputDialog.getText(self, "Input", "Please input text")
                    if ok:
                        self.annotation["text"] = text
                        self.annotation["text_color"] = self.text_color.name(QColor.NameFormat.HexArgb)
                        self.annotation["text_fill_color"] = self.label_fill_color.name(QColor.NameFormat.HexArgb)
                        self.annotation["font_name"] = self.font_name
                        self.annotation["font_size"] = self.font_size
                        if self.annotation["type"] == "text":
                            font = QFont(self.font_name)
                            font.setPixelSize(
                                int(
                                    (self.annotation["y2"] - self.annotation["y"])
                                    * self.height()
                                    * 0.8
                                )
                            )
                            metrics = QFontMetrics(font)
                            self.annotation["x2"] = (
                                self.annotation["x"] * self.width()
                                + metrics.boundingRect(text).width()
                            ) / self.width()
                if "text" not in self.annotation:
                    self.annotation["text"] = self.label
                    self.annotation["text_color"] = self.text_color
                    self.annotation["text_fill_color"] = self.label_fill_color
                    self.annotation["font_name"] = self.font_name
                    self.annotation["font_size"] = self.font_size
                self.annotation["color"] = self.color
                self.annotation["fill_color"] = self.fill_color
                self.annotation["thickness"] = self.thickness
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
        if event.button() == Qt.MouseButton.MiddleButton:
            self.start_move_pos = None
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.annotation is not None:
            x = event.pos().x()
            y = event.pos().y()
            x = (x / self.width()) * self.image_region[2] + self.image_region[0]
            y = (y / self.height()) * self.image_region[3] + self.image_region[1]
            x = max(0, min(x, 1))
            y = max(0, min(y, 1))
            self.annotation["x2"] = x
            self.annotation["y2"] = y
        else:
            x = event.pos().x()
            y = event.pos().y()
            nearest = self.find_nearest_annotation(x, y)
            self.selected_annotation_index = nearest
            if self.start_move_pos is not None:
                move_x = (event.pos().x() - self.start_move_pos.x()) / self.width()
                move_y = (event.pos().y() - self.start_move_pos.y()) / self.height()

                # Adjust the move factors by the current zoom level
                move_x *= self.image_region[2]
                move_y *= self.image_region[3]

                new_region_x = self.image_region[0] - move_x
                new_region_y = self.image_region[1] - move_y

                self.image_region[0] = max(0, min(new_region_x, 1 - self.image_region[2]))
                self.image_region[1] = max(0, min(new_region_y, 1 - self.image_region[3]))

                self.image_region_changed = True
                self.start_move_pos = event.pos()
        self.current_pos = event.pos()
        self.update()
        return super().mouseMoveEvent(event)

    def notify(self):
        if self.on_annotation_updated is not None:
            self.on_annotation_updated(self.annotation_list.annotations)

    def init_annotations(self, annotations):
        self.annotation_list.remove_all()
        self.annotation_list.batch_add(annotations)
        self.selected_annotation_index = None
        self.history = []
        self.undo_history = []
        self.annotation = None
        self.notify()
        self.update()

    def clear_annotations(self):
        self.execute_command(DeleteAllAnnotationCommand(self.annotation_list))

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

    def find_nearest_annotation(self, x, y):
        nearest = None
        nearest_d = float("inf")
        for i in range(len(self.annotation_list)):
            annotation = self.annotation_list[i]
            if annotation["type"] == "point":
                anno_x = int((annotation["x2"] - self.image_region[0]) / self.image_region[2] * self.width())
                anno_y = int((annotation["y2"] - self.image_region[1]) / self.image_region[3] * self.height())
                d = math.sqrt((x - anno_x) ** 2 + (y - anno_y) ** 2)
                if d < 5:
                    if nearest_d > d:
                        nearest_d = d
                        nearest = i
            elif annotation["type"] == "circle":
                anno_x = int((annotation["x"] - self.image_region[0]) / self.image_region[2] * self.width())
                anno_y = int((annotation["y"] - self.image_region[1]) / self.image_region[3] * self.height())
                anno_x2 = int((annotation["x2"] - self.image_region[0]) / self.image_region[2] * self.width())
                anno_y2 = int((annotation["y2"] - self.image_region[1]) / self.image_region[3] * self.height())
                r = int(math.sqrt((anno_x2 - anno_x) ** 2 + (anno_y2 - anno_y) ** 2))
                d = math.sqrt((x - anno_x) ** 2 + (y - anno_y) ** 2)
                if d < r:
                    if nearest_d > d:
                        nearest_d = d
                        nearest = i
            elif annotation["type"] in ["rectangle", "text"]:
                anno_x = int((annotation["x"] - self.image_region[0]) / self.image_region[2] * self.width())
                anno_y = int((annotation["y"] - self.image_region[1]) / self.image_region[3] * self.height())
                anno_x2 = int((annotation["x2"] - self.image_region[0]) / self.image_region[2] * self.width())
                anno_y2 = int((annotation["y2"] - self.image_region[1]) / self.image_region[3] * self.height())
                if x >= anno_x and x <= anno_x2 and y >= anno_y and y <= anno_y2:
                    cx = (anno_x + anno_x2) / 2
                    cy = (anno_y + anno_y2) / 2
                    d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    if nearest_d > d:
                        nearest_d = d
                        nearest = i
        return nearest

    @staticmethod
    def paint_annotation(
        painter: QPainter,
        annotation,
        region=[0, 0, 1, 1],
        status=None,
        default_color=DEFAULT_COLOR,
        default_text_color=DEFAULT_TEXT_COLOR,
        default_font=DEFAULT_FONT_NAME,
        default_font_size=DEFAULT_FONT_SIZE,
        default_thickness=DEFAULT_THICKNESS,
    ):
        if annotation is None:
            return
        color = to_color(annotation.get("color", default_color))
        if status == "drawing other":
            color.setAlpha(100)
        pen = painter.pen()
        pen.setColor(color)
        painter.setPen(pen)
        thickness = int(annotation.get("thickness", default_thickness) * painter.window().height())
        pen = painter.pen()
        pen.setWidth(thickness)
        painter.setPen(pen)
        x = int((annotation["x"] - region[0]) / region[2] * painter.window().width())
        y = int((annotation["y"] - region[1]) / region[3] * painter.window().height())
        x2 = int((annotation["x2"] - region[0]) / region[2] * painter.window().width())
        y2 = int((annotation["y2"] - region[1]) / region[3] * painter.window().height())
        if annotation["type"] == "point":
            path = QPainterPath()
            path.addEllipse(QPoint(x2, y2), thickness // 2, thickness // 2)
            painter.fillPath(path, color)
        elif annotation["type"] == "circle":
            painter.drawEllipse(x, y, x2 - x, y2 - y)
        elif annotation["type"] == "rectangle":
            painter.drawRect(QRect(x, y, x2 - x, y2 - y))
        elif annotation["type"] == "text" and status == "drawing":
            painter.drawRect(QRect(x, y, x2 - x, y2 - y))
        if "text" in annotation and annotation["text"] != "":
            text = annotation.get("text", "")
            font_name = annotation.get("font_name", default_font)
            font_size = annotation.get("font_size", default_font_size)
            font = QFont(font_name)
            if annotation["type"] == "text":
                font.setPixelSize(int((y2 - y) * 0.8))
            else:
                font.setPixelSize(int(painter.window().height() * font_size))
            painter.setFont(font)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(text)
            if annotation['type'] == 'text':
                foreground_color = painter.pen().color()
            else:
                if "text_color" in annotation:
                    foreground_color = to_color(annotation["text_color"])
                else:
                    foreground_color = to_color(default_text_color)
            pen = painter.pen()
            pen.setColor(foreground_color)
            painter.setPen(pen)
            if annotation["type"] == "point":
                x = x - rect.width() // 2
                y = y - metrics.descent() - rect.height() // 3
            elif annotation["type"] == "circle":
                radius = int(math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2))
                x = x - rect.width() // 2
                y = y - radius - metrics.descent()
            elif annotation["type"] == "rectangle":
                y = y - metrics.descent()
            elif annotation["type"] == "text":
                x = x
                y = y2 - metrics.descent()
            if "text_fill_color" in annotation:
                background_color = to_color(annotation["text_fill_color"])
                painter.fillRect(rect.translated(x, y), background_color)
            painter.drawText(x, y, text)
