# core/image.py

class Image:
    """
    Represents a single image to be described.
    """
    def __init__(self, path: str):
        self.path = path
        self.description = None  # Will hold an instance of Description