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
        c = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4

        y_position = height - inch  # Start from top, 1 inch margin
        x_position = inch

        for img in images:
            try:
                img_reader = ImageReader(img.path)
                # Draw image (reduce the space between image and text)
                # Let's place the image at (x_position, y_position - 2.5 inches)
                c.drawImage(img_reader, x_position, y_position - 2.5*inch, width=2.5*inch, height=2.5*inch)
            except Exception:
                c.drawString(x_position, y_position, "Error loading image")

            # Print description next to or just below the image
            description_text = img.description.content if img.description else ""
            # Move text above or to the right (depending on design)
            text_x = x_position + 2.6*inch  # small gap
            text_y = y_position - 0.5*inch  # half-inch below top margin

            c.setFont("Helvetica", 11)
            c.drawString(text_x, y_position, f"Image: {os.path.basename(img.path)}")
            c.drawString(text_x, text_y, "Description:")

            # Wrap or place the description text
            wrapped_desc = self._wrap_text(description_text, 50)
            line_height = 14
            for line in wrapped_desc:
                text_y -= line_height
                c.drawString(text_x, text_y, line)

            # After drawing image + text, move down a smaller step
            y_position -= 3 * inch  # previously 4 or more
            if y_position < 1.5 * inch:
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
