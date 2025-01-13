# core/exporter.py

import os
import csv
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

class Exporter:
    def export_to_excel(self, images, save_path: str):
        """
        Exports descriptions to an Excel file.
        """
        workbook = xlsxwriter.Workbook(save_path)
        worksheet = workbook.add_worksheet("Descriptions")

        # Headers
        worksheet.write("A1", "Image File")
        worksheet.write("B1", "Description")

        for idx, img in enumerate(images, start=2):
            worksheet.write(f"A{idx}", os.path.basename(img.path))
            worksheet.write(f"B{idx}", img.description.content if img.description else "")

        workbook.close()

    def export_to_csv(self, images, save_path: str):
        """
        Exports descriptions to a CSV file.
        """
        with open(save_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Image File", "Description"])
            for img in images:
                writer.writerow([
                    os.path.basename(img.path),
                    img.description.content if img.description else ""
                ])

    def export_to_txt(self, images, save_path: str):
        """
        Exports descriptions to a TXT file.
        """
        with open(save_path, mode="w", encoding="utf-8") as txtfile:
            for img in images:
                txtfile.write(f"Image File: {os.path.basename(img.path)}\n")
                desc = img.description.content if img.description else ""
                txtfile.write(f"Description:\n{desc}\n\n")
    
    def export_to_pdf(self, images, save_path: str):
        """
        Exports descriptions to a PDF, embedding each image and its description.
        """
        c = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4

        y_position = height - inch  # Start from top, 1 inch margin
        x_position = inch

        for img in images:
            # Draw image (thumbnail-size to fit on page)
            # Convert the image to a ReportLab-readable format
            try:
                # Could do image resizing with PIL if desired
                img_reader = ImageReader(img.path)
                c.drawImage(img_reader, x_position, y_position - 3*inch, width=3*inch, height=3*inch)
            except Exception:
                # If image can't be opened, skip or write a placeholder
                c.drawString(x_position, y_position, "Error loading image")

            # Draw description text
            description_text = img.description.content if img.description else ""
            text_x = x_position + 3.2*inch
            text_y = y_position - inch  # place text next to image

            c.setFont("Helvetica", 11)
            # Write file name
            c.drawString(text_x, y_position, f"Image: {os.path.basename(img.path)}")
            # Write description
            c.drawString(text_x, text_y, "Description:")
            # More advanced text wrapping can be done with textobjects or paragraphs
            # For simplicity, just show first ~100 chars or so
            wrapped_desc = self._wrap_text(description_text, 50)
            offset = 20
            for line in wrapped_desc:
                text_y -= offset
                c.drawString(text_x, text_y, line)

            # Move to next position
            y_position -= 4*inch
            # If we go beyond bottom margin, start a new page
            if y_position < inch:
                c.showPage()
                y_position = height - inch

        c.save()

    def _wrap_text(self, text, width=50):
        """
        Naive text wrapping by splitting on spaces. 
        For more robust solutions, consider using ReportLab's paragraph features.
        """
        words = text.split()
        lines = []
        current_line = []
        current_len = 0

        for w in words:
            if current_len + len(w) + 1 <= width:
                current_line.append(w)
                current_len += len(w) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)
        if current_line:
            lines.append(" ".join(current_line))

        return lines
