# core/description_generator.py

import re
import ollama

class DescriptionGenerator:
    """
    Uses ollama to generate descriptions for images.
    """
    def __init__(self, model_name="llama3.2-vision"):
        self.model_name = model_name

    def generate_description(self, image_path: str) -> str:
        """
        Send an image to the ollama model and return the text from its response.
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': 'This is an image taken from a plane, describe it',
                        'images': [image_path]
                    }
                ]
            )
            # Attempt to parse the 'content' field from the response text
            match = re.search(r"content='(.*?)'", str(response))
            if match:
                return match.group(1)
            else:
                return "No description found or an error occurred."
        except Exception as e:
            return f"Error generating description: {e}"
