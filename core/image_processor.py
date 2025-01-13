# core/image_processor.py

import os
from .image import Image
from .description import Description

class ImageProcessor:
    """
    Loads images from a folder into a list of Image objects.
    """
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.images = []

    def load_images(self):
        if not os.path.isdir(self.folder_path):
            raise ValueError(f"'{self.folder_path}' is not a valid folder.")

        # Gather files from the folder
        items = os.listdir(self.folder_path)
        files = [
            f for f in items
            if os.path.isfile(os.path.join(self.folder_path, f))
        ]

        # Create Image objects
        self.images = [Image(os.path.join(self.folder_path, f)) for f in files]
