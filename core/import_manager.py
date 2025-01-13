# core/import_manager.py
class ImportManager:
    """
    Checks or imports required libraries.
    Placeholder for advanced checks if needed.
    """
    @staticmethod
    def ensure_imports():
        try:
            import ollama
            import reportlab
            import xlsxwriter
        except ImportError as e:
            raise ImportError(
                f"Required library missing: {e.name}. "
                "Please install all required packages."
            )
