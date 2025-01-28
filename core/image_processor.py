import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image as im
from .image import Image
from .description import Description

class ImageProcessor:
    """
    Loads images from a folder into a list of Image objects.
    Automatically converts .npz files to .png before processing.
    """
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.images = []

    def _convert_npz_to_png(self, npz_path, output_path):
        """
        Converts a .npz file into a .png image and saves it.

        Parameters:
        npz_path (str): Path to the .npz file.
        output_path (str): Path to save the .png file.
        """
        with np.load(npz_path) as npz:
            arr = np.ma.MaskedArray(**npz)

        # Select RGB bands (example: red=60, green=16, blue=4)
        red_band = arr[60, :, :].data
        green_band = arr[16, :, :].data
        blue_band = arr[4, :, :].data

        # Normalize bands
        red_band = red_band / np.max(red_band)
        green_band = green_band / np.max(green_band)
        blue_band = blue_band / np.max(blue_band)

        # Create RGB image
        rgb_image = np.dstack((red_band, green_band, blue_band))
        rgb_image_normalized = (rgb_image * 255).astype(np.uint8)

        # Save as .png
        image = im.fromarray(rgb_image_normalized)
        image.save(output_path)

    def load_images(self):
        if not os.path.isdir(self.folder_path):
            raise ValueError(f"'{self.folder_path}' is not a valid folder.")

        # Gather files from the folder
        items = os.listdir(self.folder_path)
        files = [
            f for f in items
            if os.path.isfile(os.path.join(self.folder_path, f))
        ]

        for file_name in files:
            file_path = os.path.join(self.folder_path, file_name)
            if file_name.endswith('.npz'):
                # Convert .npz to .png
                png_file_name = file_name.replace('.npz', '.png')
                png_file_path = os.path.join(self.folder_path, png_file_name)

                # Convert only if .png does not already exist
                if not os.path.exists(png_file_path):
                    self._convert_npz_to_png(file_path, png_file_path)

        # Filter only .png files for Image objects
        png_files = [
            f for f in os.listdir(self.folder_path)
            if f.endswith('.png')
        ]

        # Create Image objects
        self.images = [Image(os.path.join(self.folder_path, f)) for f in png_files]
