
import json
from PyQt6.QtWidgets import QDialog, QProgressBar, QVBoxLayout
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor

from anno_label import AnnoLabel


class ExportProgressDialog(QDialog):
    def __init__(self, max_num, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export")
        self.setMinimumSize(300, 100)
        self.setMaximumSize(300, 100)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(max_num)

        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)

    def set_progress(self, value):
        self.progress_bar.setValue(value)
        if value == self.progress_bar.maximum():
            self.close()


class Export(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, image_provider, image_writer, annotation_dir, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.image_provider = image_provider
        self.image_writer = image_writer
        self.annotation_dir = annotation_dir
        dialog = ExportProgressDialog(image_provider.get_total(), parent)
        self.progress_updated.connect(dialog.set_progress)
        self.start()
        dialog.exec()

    def run(self):
        for i in range(self.image_provider.get_total()):
            self.image_provider.set_index(i)
            image = self.image_provider.get_image()
            anno_file = self.annotation_dir / f"{i:08d}.json"
            if anno_file.exists():
                annotations = json.loads(anno_file.read_text(encoding='utf-8'))
            else:
                annotations = []
            painter = QPainter(image)
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(0, 255, 0))
            painter.setPen(pen)
            for annotation in annotations:
                AnnoLabel.paint_annotation(painter, annotation)
            self.image_writer.write(image)
            self.progress_updated.emit(i + 1)
            painter.end()
        self.image_writer.release()
