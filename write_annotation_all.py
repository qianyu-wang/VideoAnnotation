
import io
import json

from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice, QObject, QThread, Signal
from PySide6.QtWidgets import QDialog, QProgressBar, QVBoxLayout


class WriteAnnotationAllProgressDialog(QDialog):
    def __init__(self, max_num, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Write Annotation for All Frames")
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


class WriteAnnotationAll(QThread):
    progress_updated = Signal(int)

    def __init__(self, image_provider, annotation_dir, annotation, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.image_provider = image_provider
        self.annotation_dir = annotation_dir
        self.annotation = annotation
        self.start_index = image_provider.get_index() + 1
        self.end_index = image_provider.get_total()
        dialog = WriteAnnotationAllProgressDialog(self.end_index - self.start_index, parent)
        self.progress_updated.connect(dialog.set_progress)
        self.start()
        dialog.exec()

    def run(self):
        for i in range(self.start_index, self.end_index):
            anno_file = self.annotation_dir / f"{i:08d}.json"
            if anno_file.exists():
                annotations = json.loads(anno_file.read_text(encoding='utf-8'))
            else:
                annotations = []
            print(f"Writing annotation for frame {i} to {str(anno_file)}")
            annotations.append(self.annotation)
            anno_file.write_text(json.dumps(annotations, ensure_ascii=False, indent=4), encoding='utf-8')
            self.progress_updated.emit(i - self.start_index + 1)
