import io

from PIL import Image
from PyQt6.QtCore import QBuffer, QIODeviceBase, QObject, QThread
from PyQt6.QtWidgets import QDialog, QProgressBar, QVBoxLayout


class RunProviderProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run Provider")
        self.setMinimumSize(300, 100)
        self.setMaximumSize(300, 100)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setTextVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)

    def start_animation(self):
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFormat("Processing...")
        self.progress_bar.setRange(0, 0)

    def stop_animation(self):
        self.close()


class RunProvider(QThread):
    def __init__(self, image, provider, annotation_type, show_text, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.image = image
        self.provider = provider
        self.annotation_type = annotation_type
        self.show_text = show_text
        self.annotations = None
        dialog = RunProviderProgressDialog(parent)
        self.finished.connect(dialog.stop_animation)
        self.start()
        dialog.start_animation()
        dialog.exec()

    def run(self):
        buffer = QBuffer()
        buffer.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        self.image.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        annotations = self.provider.run(pil_im, self.annotation_type, self.show_text)
        self.annotations = annotations
