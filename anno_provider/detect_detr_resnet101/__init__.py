from .detect_detr_resnet101 import DetectDetrResnet101


def get_provider(parent):
    return DetectDetrResnet101(parent)
