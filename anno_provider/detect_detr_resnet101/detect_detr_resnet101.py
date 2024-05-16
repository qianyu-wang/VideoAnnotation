from typing import Tuple
import torch
from PIL import Image
from PySide6.QtWidgets import QInputDialog
from transformers import DetrForObjectDetection, DetrImageProcessor


class DetectDetrResnet101(object):
    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-101")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-101")
        keep_label_text, ok = QInputDialog.getText(None, 'Input', 'Please input labels to keep, separated by ;, for example: 0;1;2')
        if not ok:
            keep_label_text = ""
        self.keep_labels: list[str] = keep_label_text.split(";")
        self.keep_labels = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), self.keep_labels)))
        self.text_template = ""
        self.text_template, ok = QInputDialog.getText(None, 'Input', 'Please input text template, use score and label for substitution, for example: {score:.2f} {label}')
        if not ok:
            self.text_template = ""

    def run(self, image: Image.Image, annotation_type: str, color: Tuple[int, int, int]):
        print("start detect.")
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
        print(len(results["boxes"]), "objects detected.")

        annotations = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            if len(self.keep_labels) > 0 and str(label.item()) not in self.keep_labels:
                print(f"Skip label {label.item()}.")
                continue
            box = [round(i, 2) for i in box.tolist()]
            box = [box[0] / image.width, box[1] / image.height, box[2] / image.width, box[3] / image.height]
            annotation = {
                "type": annotation_type,
                "x": box[0],
                "y": box[1],
                "x2": box[2],
                "y2": box[3],
            }
            if len(self.text_template) > 0:
                annotation["text"] = self.text_template.format(score=score, label=label)
            if color is not None:
                annotation["color"] = color
            annotations.append(annotation)
        print(f"return {len(annotations)} annotations.")
        return annotations
