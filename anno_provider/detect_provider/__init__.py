from .detect_provider import DetectAnnoProvider


def get_provider(parent):
    return DetectAnnoProvider(parent)
