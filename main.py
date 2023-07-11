import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PyQt6.QtCore import QBuffer, QIODeviceBase, Qt
from PyQt6.QtGui import QImage, QKeyEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from export import Export
from run_provider import RunProvider
from run_provider_all import RunProviderAll
from video_annotation_ui import Ui_MainWindow

image_suffix = ['png', 'jpg', 'jpeg', 'bmp']
video_suffix = ['mp4', 'avi', 'mkv', 'flv', 'rmvb', 'rm', 'mov', 'wmv', 'mpg', 'mpeg', 'm4v', '3gp', '3g2', 'asf', 'asx', 'vob', 'ts', 'm2ts', 'divx', 'f4v', 'm2v', 'dat', 'tp', 'webm', 'mts', 'mxf', 'mpe', 'mpv', 'm2t', 'ogv', 'swf', 'drc', 'gif', 'gifv', 'mng', 'avi', 'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv', 'mp4', 'm4p', 'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'gif', 'webm', 'vob', 'ogv', 'drc', 'gifv', 'mng', 'avi', 'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv', 'mp4', 'm4p', 'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'gif', 'webm', 'vob', 'ogv', 'drc', 'gifv', 'mng']


class ImageProvider(object):
    def __init__(self, filename):
        self.filename = filename
        self.image = QImage(filename)

    def set_index(self, index):
        pass

    def get_image(self):
        return self.image

    def get_index(self):
        return 0

    def get_total(self):
        return 1


class ImageWriter(object):
    def __init__(self, filename):
        self.filename = filename

    def write(self, image: QImage):
        image.save(self.filename)

    def release(self):
        pass


class VideoProvider(object):
    def __init__(self, filename):
        self.filename = filename
        self.video = cv2.VideoCapture(filename)
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_index = 0

    def set_index(self, index):
        self.frame_index = index
        if self.frame_index < 0:
            self.frame_index = 0
        if self.frame_index >= self.frame_count:
            self.frame_index = self.frame_count - 1

    def get_image(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
        ret, frame = self.video.read()
        if not ret:
            return None
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
        return image

    def get_index(self):
        return self.frame_index

    def get_total(self):
        return self.frame_count


class VideoWriter(object):
    def __init__(self, filename, src_filename) -> None:
        self.filename = filename
        src_video = cv2.VideoCapture(src_filename)
        self.video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), src_video.get(cv2.CAP_PROP_FPS), (int(src_video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(src_video.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        src_video.release()

    def write(self, image: QImage):
        buffer = QBuffer()
        buffer.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        image.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        self.video.write(cv2.cvtColor(np.asarray(pil_im), cv2.COLOR_RGB2BGR))

    def release(self):
        self.video.release()


class VideoAnnotationTool(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.file_path = None
        self.annotation_dir = None
        self.image_provider = None
        self.anno_provider_name = None
        self.anno_provider = None

        self.ui.button_select_file.clicked.connect(self.select_file)
        self.ui.button_next.clicked.connect(self.next_image)
        self.ui.button_previous.clicked.connect(self.previous_image)
        self.ui.button_undo.clicked.connect(self.undo)
        self.ui.button_redo.clicked.connect(self.redo)
        self.ui.button_reload_provider.clicked.connect(self.load_provider_list)
        self.ui.button_run_provider.clicked.connect(self.run_provider)
        self.ui.button_run_provider_all.clicked.connect(self.run_provider_all)
        self.ui.button_export.clicked.connect(self.export)
        self.ui.text_file.returnPressed.connect(self.load_file)
        self.ui.text_current.returnPressed.connect(self.load_image)
        self.ui.check_text.toggled.connect(self.type_changed)
        self.ui.combo_type.currentTextChanged.connect(self.type_changed)
        self.ui.label_anno.on_annotation_updated = self.save_annotation

        self.load_provider_list()

        self.installEventFilter(self)

    def load_provider_list(self):
        self.ui.combo_anno_provider.clear()
        self.ui.combo_anno_provider.addItem("")
        self.anno_provider_name = None
        self.anno_provider = None
        for provider_path in (Path(__file__).parent / "anno_provider").iterdir():
            if provider_path.is_file():
                self.ui.combo_anno_provider.addItem(provider_path.stem)
            elif provider_path.is_dir():
                self.ui.combo_anno_provider.addItem(provider_path.name)
        self.ui.combo_anno_provider.setCurrentIndex(0)

    def export(self):
        if self.file_path.suffix in image_suffix:
            image_provider = ImageProvider(str(self.file_path))
            image_writer = ImageWriter(str(self.file_path.parent / f"{self.file_path.stem}_render{self.file_path.suffix}"))
        elif self.file_path.suffix.split('.')[-1] in video_suffix:
            image_provider = VideoProvider(str(self.file_path))
            image_writer = VideoWriter(str(self.file_path.parent / f"{self.file_path.stem}_render{self.file_path.suffix}"), str(self.file_path))
        else:
            QMessageBox.critical(self, 'Error', 'Unsupported file format')
            return
        Export(image_provider, image_writer, self.annotation_dir, self)
        QMessageBox.information(self, 'Information', f'Export to {image_writer.filename} finished.')

    def load_provider(self):
        provider_name = self.ui.combo_anno_provider.currentText()
        if provider_name == "":
            QMessageBox.critical(self, 'Error', 'Please select a anno provider')
            return False
        if self.anno_provider_name != provider_name or self.anno_provider is None:
            get_provider = __import__(f"anno_provider.{provider_name}", fromlist=['get_provider']).get_provider
            self.anno_provider = get_provider(self)
        if self.anno_provider is None:
            QMessageBox.critical(self, 'Error', f'Cannot load anno provider: {self.anno_provider_name}')
            return False
        self.anno_provider_name = provider_name
        return True

    def run_provider(self):
        if not self.load_provider():
            return
        provider = RunProvider(self.image_provider.get_image(), self.anno_provider, self.ui.combo_type.currentText(), self.ui.check_text.isChecked(), self)
        if provider.annotations is not None:
            self.ui.label_anno.batch_add_annotation(provider.annotations)
            self.ui.label_anno.update()

    def run_provider_all(self):
        if not self.load_provider():
            return
        RunProviderAll(self.image_provider, self.anno_provider, self.annotation_dir, self.ui.combo_type.currentText(), self.ui.check_text.isChecked(), self)
        self.load_image()
        QMessageBox.information(self, 'Information', f'Run provider {self.anno_provider_name} finished')

    def type_changed(self):
        self.ui.label_anno.annotation_type = self.ui.combo_type.currentText()
        self.ui.label_anno.show_text = self.ui.check_text.isChecked()

    def next_image(self):
        self.ui.text_current.setText(str(int(self.ui.text_current.text()) + 1))
        self.load_image()

    def previous_image(self):
        self.ui.text_current.setText(str(int(self.ui.text_current.text()) - 1))
        self.load_image()

    def undo(self):
        self.ui.label_anno.undo()

    def redo(self):
        self.ui.label_anno.redo()

    def select_file(self):
        suffixes = ' '.join([f"*.{suffix}" for suffix in image_suffix + video_suffix])
        filename = QFileDialog.getOpenFileName(self, 'Choose', '', f'Images/Videos ({suffixes})')[0]
        if filename == '':
            return
        self.ui.text_file.setText(filename)
        self.load_file()

    def load_file(self):
        self.file_path = Path(self.ui.text_file.text())
        if not self.file_path.exists():
            QMessageBox.critical(self, 'Error', 'File not exists')
            return
        if self.file_path.suffix in image_suffix:
            self.image_provider = ImageProvider(str(self.file_path))
        elif self.file_path.suffix.split('.')[-1] in video_suffix:
            self.image_provider = VideoProvider(str(self.file_path))
        else:
            QMessageBox.critical(self, 'Error', 'Unsupported file format')
            return
        self.annotation_dir = self.file_path.parent / f"{self.file_path.stem}_annotations"
        self.annotation_dir.mkdir(exist_ok=True, parents=True)
        self.ui.text_file.setText(str(self.file_path.absolute()))
        self.ui.label_total.setText(f"/{self.image_provider.get_total()}")
        self.ui.text_current.setText(str(self.image_provider.get_index() + 1))
        self.ui.label_anno.setEnabled(True)
        self.load_image()

    def load_image(self):
        self.image_provider.set_index(int(self.ui.text_current.text()) - 1)
        self.ui.text_current.setText(str(self.image_provider.get_index() + 1))
        pixmap = QPixmap.fromImage(self.image_provider.get_image().scaled(self.ui.label_anno.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.ui.label_anno.setPixmap(pixmap)
        anno_file = self.annotation_dir / f"{self.image_provider.get_index():08d}.json"
        if anno_file.exists():
            annotations = json.loads(anno_file.read_text(encoding='utf-8'))
        else:
            annotations = []
        self.ui.label_anno.init_annotations(annotations)

    def save_annotation(self, annotations):
        anno_file = self.annotation_dir / f"{self.image_provider.get_index():08d}.json"
        anno_file.write_text(json.dumps(annotations, indent=4, ensure_ascii=False), encoding='utf-8')

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if self.image_provider is not None:
            if event.key() == Qt.Key.Key_Left:
                self.previous_image()
            elif event.key() == Qt.Key.Key_Right:
                self.next_image()
            elif event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.undo()
            elif event.key() == Qt.Key.Key_Y and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.redo()
            elif event.key() == Qt.Key.Key_Space:
                self.next_image()
        return super().keyReleaseEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    tool = VideoAnnotationTool()
    tool.show()

    sys.exit(app.exec())
