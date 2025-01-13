# core/batch.py

from .description import Description

class Batch:
    """
    Coordinates describing each image in the batch using the DescriptionGenerator.
    """
    def __init__(self, image_processor, description_generator):
        self.image_processor = image_processor
        self.description_generator = description_generator

    def process_images(self):
        for img in self.image_processor.images:
            text = self.description_generator.generate_description(img.path)
            img.description = Description(text)