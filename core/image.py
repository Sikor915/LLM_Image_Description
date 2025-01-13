# core/image.py
from .description import Description

class Image:
    def __init__(self, path: str):
        self.path = path
        # Initialize with an empty Description so it's never None.
        self.description = Description("")  
