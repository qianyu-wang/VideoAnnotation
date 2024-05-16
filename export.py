import json
from PySide6.QtWidgets import QDialog, QProgressBar, QVBoxLayout, QInputDialog, QMessageBox
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QPainter, QPen, QColor

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
    progress_updated = Signal(int)

    def __init__(
        self,
        image_provider,
        image_writer,
        annotation_dir,
        default_color,
        default_text_color,
        default_font,
        default_font_size,
        default_thickness,
        parent: QObject | None = ...,
    ) -> None:
        super().__init__(parent)
        self.image_provider = image_provider
        self.image_writer = image_writer
        self.annotation_dir = annotation_dir
        self.default_color = default_color
        self.default_text_color = default_text_color
        self.default_font = default_font
        self.default_font_size = default_font_size
        self.default_thickness = default_thickness
        self.start_index = 0
        self.end_index = 0
        while True:
            text, ok = QInputDialog.getText(parent, "Export", f"Input export frame range start:end (e.g. 1:1000):", text=f"1:{image_provider.get_total()}")
            if not ok:
                return
            parts = text.split(':')
            if len(parts) != 2:
                QMessageBox.critical(parent, "Error", "Invalid input")
                continue
            try:
                parts = [int(part) for part in parts]
            except ValueError:
                QMessageBox.critical(parent, "Error", "Invalid input")
                continue
            self.start_index = parts[0] - 1
            self.end_index = parts[1]
            if self.start_index < 0 or self.end_index > image_provider.get_total() or self.start_index >= self.end_index:
                QMessageBox.critical(parent, "Error", "Invalid input")
                continue
            break
        dialog = ExportProgressDialog(self.end_index - self.start_index, parent)
        self.progress_updated.connect(dialog.set_progress)
        self.start()
        dialog.exec()

    def run(self):
        for i in range(self.start_index, self.end_index):
            self.image_provider.set_index(i)
            image = self.image_provider.get_image()
            anno_file = self.annotation_dir / f"{i:08d}.json"
            if anno_file.exists():
                annotations = json.loads(anno_file.read_text(encoding='utf-8'))
            else:
                annotations = []
            painter = QPainter(image)
            for annotation in annotations:
                AnnoLabel.paint_annotation(
                    painter,
                    annotation,
                    default_color=self.default_color,
                    default_text_color=self.default_text_color,
                    default_font=self.default_font,
                    default_font_size=self.default_font_size,
                    default_thickness=self.default_thickness,
                )
            self.image_writer.write(image)
            self.progress_updated.emit(i - self.start_index + 1)
            painter.end()
        self.image_writer.release()
