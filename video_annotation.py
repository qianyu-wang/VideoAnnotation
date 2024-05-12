import io
import json
import sys
from copy import deepcopy
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage, QKeyEvent, QPixmap
from PySide6.QtWidgets import (QApplication, QColorDialog, QFileDialog,
                               QMainWindow, QMessageBox)

from export import Export
from run_provider import RunProvider
from run_provider_all import RunProviderAll
from video_annotation_ui import Ui_MainWindow
from write_annotation_all import WriteAnnotationAll

image_suffix = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'gif', 'webp', 'ico', 'jpe', 'jp2', 'j2k', 'jpf', 'jpx', 'jpm', 'mj2', 'svg', 'svgz', 'eps', 'psd', 'ai', 'cdr', 'dxf', 'wmf', 'emf', 'tga', 'icns', 'jp2', 'j2k', 'jpf', 'jpx', 'jpm', 'mj2', 'svg', 'svgz', 'eps', 'psd', 'ai', 'cdr', 'dxf', 'wmf', 'emf', 'tga', 'icns', 'jp2', 'j2k', 'jpf', 'jpx', 'jpm', 'mj2', 'svg', 'svgz', 'eps', 'psd', 'ai', 'cdr', 'dxf', 'wmf', 'emf', 'tga', 'icns']
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
        image = QImage(
            frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
        return image

    def get_index(self):
        return self.frame_index

    def get_total(self):
        return self.frame_count


class VideoWriter(object):
    def __init__(self, filename, src_filename) -> None:
        self.filename = filename
        src_video = cv2.VideoCapture(src_filename)
        self.video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), src_video.get(cv2.CAP_PROP_FPS), (int(
            src_video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(src_video.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        src_video.release()

    def write(self, image: QImage):
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        image.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        self.video.write(cv2.cvtColor(np.asarray(pil_im), cv2.COLOR_RGB2BGR))

    def release(self):
        self.video.release()


class ImageFolderProvider(object):
    def __init__(self, folder):
        self.filename = folder
        self.images = list(folder.glob('*'))
        self.index = 0

    def set_index(self, index):
        self.index = index
        if self.index < 0:
            self.index = 0
        if self.index >= len(self.images):
            self.index = len(self.images) - 1

    def get_image(self):
        return QImage(str(self.images[self.index]))

    def get_index(self):
        return self.index

    def get_total(self):
        return len(self.images)


class ImageFolderWriter(object):
    def __init__(self, folder):
        self.filename = folder
        self.index = 0

    def write(self, image: QImage):
        dest_path = self.filename / f"{self.index:08d}.png"
        dest_path.parent.mkdir(exist_ok=True, parents=True)
        image.save(str(dest_path))
        self.index += 1

    def release(self):
        pass


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
        self.ui.button_change_color.clicked.connect(self.change_color)
        self.ui.button_copy_to_all.clicked.connect(self.copy_to_all)
        self.ui.text_file.returnPressed.connect(self.load_file)
        self.ui.text_current.returnPressed.connect(self.load_image)
        self.ui.combo_type.currentTextChanged.connect(self.type_changed)
        self.ui.label_anno.on_annotation_updated = self.save_annotation

        self.ui.label_color.setStyleSheet(f"background-color: rgb({self.ui.label_anno.color.red()}, {self.ui.label_anno.color.green()}, {self.ui.label_anno.color.blue()});")

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
        if self.file_path is None:
            QMessageBox.critical(self, 'Error', 'Please select a file')
            return
        elif self.file_path.is_dir():
            image_provider = ImageFolderProvider(self.file_path)
            image_writer = ImageFolderWriter(
                self.file_path.parent / f"{self.file_path.stem}_render")
        elif self.file_path.suffix in image_suffix:
            image_provider = ImageProvider(str(self.file_path))
            image_writer = ImageWriter(str(
                self.file_path.parent / f"{self.file_path.stem}_render{self.file_path.suffix}"))
        elif self.file_path.suffix.split('.')[-1] in video_suffix:
            image_provider = VideoProvider(str(self.file_path))
            image_writer = VideoWriter(str(
                self.file_path.parent / f"{self.file_path.stem}_render{self.file_path.suffix}"), str(self.file_path))
        else:
            QMessageBox.critical(self, 'Error', 'Unsupported file format')
            return
        Export(image_provider, image_writer, self.annotation_dir, self)
        QMessageBox.information(self, 'Information',
                                f'Export to {image_writer.filename} finished.')

    def change_color(self):
        color = QColorDialog.getColor(
            initial=self.ui.label_anno.color, parent=self)
        if color.isValid():
            self.ui.label_anno.color = color
            self.ui.label_color.setStyleSheet(f"background-color: rgb({self.ui.label_anno.color.red()}, {self.ui.label_anno.color.green()}, {self.ui.label_anno.color.blue()});")
            self.ui.label_anno.update()

    def copy_to_all(self):
        if len(self.ui.label_anno.annotation_list) == 0:
            return
        annotation = self.ui.label_anno.annotation_list.annotations[-1]
        WriteAnnotationAll(self.image_provider, self.annotation_dir, annotation, self)
        self.load_image()
        QMessageBox.information(
            self, 'Information', f'Write anotation to all frames finished')

    def load_provider(self):
        provider_name = self.ui.combo_anno_provider.currentText()
        if provider_name == "":
            QMessageBox.critical(
                self, 'Error', 'Please select a anno provider')
            return False
        if self.anno_provider_name != provider_name or self.anno_provider is None:
            get_provider = __import__(f"anno_provider.{provider_name}", fromlist=[
                                      'get_provider']).get_provider
            self.anno_provider = get_provider(self)
        if self.anno_provider is None:
            QMessageBox.critical(
                self, 'Error', f'Cannot load anno provider: {self.anno_provider_name}')
            return False
        self.anno_provider_name = provider_name
        return True

    def run_provider(self):
        if not self.load_provider():
            return
        provider = RunProvider(self.image_provider.get_image(
        ), self.anno_provider, self.ui.combo_type.currentText(), self.ui.label_anno.color.getRgb()[:3], self)
        if provider.annotations is not None:
            self.ui.label_anno.batch_add_annotation(provider.annotations)
            self.ui.label_anno.update()

    def run_provider_all(self):
        if not self.load_provider():
            return
        RunProviderAll(self.image_provider, self.anno_provider, self.annotation_dir,
                       self.ui.combo_type.currentText(),
                       self.ui.label_anno.color.getRgb()[:3], self)
        self.load_image()
        QMessageBox.information(
            self, 'Information', f'Run provider {self.anno_provider_name} finished')

    def type_changed(self):
        self.ui.label_anno.annotation_type = self.ui.combo_type.currentText()

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
        suffixes = ' '.join(
            [f"*.{suffix}" for suffix in image_suffix + video_suffix])
        filename = QFileDialog.getOpenFileName(
            self, 'Choose', '', f'Images/Videos ({suffixes})')[0]
        if filename == '':
            return
        self.ui.text_file.setText(filename)
        self.load_file()

    def load_file(self):
        self.file_path = Path(self.ui.text_file.text())
        if not self.file_path.exists():
            QMessageBox.critical(self, 'Error', 'File not exists')
            return
        if self.file_path.is_dir():
            self.image_provider = ImageFolderProvider(self.file_path)
        elif self.file_path.suffix in image_suffix:
            self.image_provider = ImageProvider(str(self.file_path))
        elif self.file_path.suffix.split('.')[-1] in video_suffix:
            self.image_provider = VideoProvider(str(self.file_path))
        else:
            QMessageBox.critical(self, 'Error', 'Unsupported file format')
            return
        self.annotation_dir = self.file_path.parent / \
            f"{self.file_path.stem}_annotations"
        self.annotation_dir.mkdir(exist_ok=True, parents=True)
        self.ui.text_file.setText(str(self.file_path.absolute()))
        self.ui.label_total.setText(f"/{self.image_provider.get_total()}")
        self.ui.text_current.setText(str(self.image_provider.get_index() + 1))
        self.ui.label_anno.setEnabled(True)
        self.load_image()

    def load_image(self):
        self.image_provider.set_index(int(self.ui.text_current.text()) - 1)
        self.ui.text_current.setText(str(self.image_provider.get_index() + 1))
        pixmap = QPixmap.fromImage(self.image_provider.get_image().scaled(self.ui.label_anno.size(
        ), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.ui.label_anno.setPixmap(pixmap)
        anno_file = self.annotation_dir / \
            f"{self.image_provider.get_index():08d}.json"
        if anno_file.exists():
            annotations = json.loads(anno_file.read_text(encoding='utf-8'))
        else:
            annotations = []
        if len(annotations) == 0:
            annotations = self.predict_by_track()
        self.ui.label_anno.init_annotations(annotations)

    def predict_by_track(self):
        current_index = self.image_provider.get_index()
        if current_index == 0:
            return []
        previous_index = current_index - 1
        anno_file = self.annotation_dir / f"{previous_index:08d}.json"
        if not anno_file.exists():
            return []
        previous_annotations = json.loads(anno_file.read_text(encoding='utf-8'))
        if len(previous_annotations) == 0:
            return []
        self.image_provider.set_index(previous_index)
        previous_image = self.image_provider.get_image()
        self.image_provider.set_index(current_index)
        img = previous_image
        buffer_ = img.bits()
        buffer_.cast('B').release()
        cv2_img = np.asarray(buffer_).reshape(img.height(), img.width(), 4)
        cv_previous_image = cv2.cvtColor(cv2_img, cv2.COLOR_RGBA2BGR)
        current_image: QImage = self.image_provider.get_image()
        img = current_image
        buffer_ = img.bits()
        buffer_.cast("B").release()
        cv2_img = np.asarray(buffer_).reshape(img.height(), img.width(), 4)
        cv_current_image = cv2.cvtColor(cv2_img, cv2.COLOR_RGBA2BGR)
        current_annotations = []
        for annotation in previous_annotations:
            if annotation['type'] in ['rectangle']:
                x1 = int(annotation['x'] * previous_image.width())
                y1 = int(annotation['y'] * previous_image.height())
                x2 = int(annotation['x2'] * previous_image.width())
                y2 = int(annotation["y2"] * previous_image.height())
                param = cv2.TrackerCSRT.Params()
                param.use_hog = True
                param.use_color_names = True
                tracker = cv2.TrackerCSRT.create(param)
                tracker.init(cv_previous_image, (x1, y1, x2 - x1, y2 - y1))
                success, predit_box = tracker.update(cv_current_image)
                x, y, w, h = predit_box
                if success:
                    annotation = deepcopy(annotation)
                    annotation['x'] = x / current_image.width()
                    annotation['y'] = y / current_image.height()
                    annotation['x2'] = (x + w) / current_image.width()
                    annotation['y2'] = (y + h) / current_image.height()
                    current_annotations.append(annotation)
        self.save_annotation(current_annotations)
        return current_annotations

    def save_annotation(self, annotations):
        anno_file = self.annotation_dir / \
            f"{self.image_provider.get_index():08d}.json"
        anno_file.write_text(json.dumps(
            annotations, indent=4, ensure_ascii=False), encoding='utf-8')

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
