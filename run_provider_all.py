
import io
import json

from PIL import Image
from PyQt6.QtCore import QBuffer, QIODeviceBase, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QProgressBar, QVBoxLayout


class RunProviderAllProgressDialog(QDialog):
    def __init__(self, max_num, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run Provider All")
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


class RunProviderAll(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, image_provider, anno_provider, annotation_dir, annotation_type, show_text, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.image_provider = image_provider
        self.anno_provider = anno_provider
        self.annotation_dir = annotation_dir
        self.annotation_type = annotation_type
        self.show_text = show_text
        dialog = RunProviderAllProgressDialog(image_provider.get_total(), parent)
        self.progress_updated.connect(dialog.set_progress)
        self.start()
        dialog.exec()

    def run(self):
        for i in range(self.image_provider.get_index(), self.image_provider.get_total()):
            self.image_provider.set_index(i)
            image = self.image_provider.get_image()
            buffer = QBuffer()
            buffer.open(QIODeviceBase.OpenModeFlag.ReadWrite)
            image.save(buffer, "PNG")
            pil_im = Image.open(io.BytesIO(buffer.data()))
            annotations = self.anno_provider.run(pil_im, self.annotation_type, self.show_text)
            anno_file = self.annotation_dir / f"{i:08d}.json"
            anno_file.write_text(json.dumps(annotations, ensure_ascii=False, indent=4), encoding='utf-8')
            self.progress_updated.emit(i + 1)
