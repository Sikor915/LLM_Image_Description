# gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from core.import_manager import ImportManager
from core.image_processor import ImageProcessor
from core.description_generator import DescriptionGenerator
from core.batch import Batch
from core.exporter import Exporter

import os

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Description Generator")

        # High-contrast style: white background, black text
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            ".",
            background="white",
            foreground="black",
            fieldbackground="white",
            bordercolor="black",
            highlightthickness=1
        )
        style.configure("TLabel", background="white", foreground="black")
        style.configure("TButton", background="white", foreground="black", padding=5)
        style.configure("TFrame", background="white")
        style.configure("TEntry", foreground="black")

        # Variables
        self.folder_path = tk.StringVar()
        self.save_path = tk.StringVar()
        # 1) Set the default export format to CSV instead of Excel:
        self.export_format = tk.StringVar(value="CSV")

        # Build the GUI
        self.create_widgets()

    def create_widgets(self):
        # Main container frame
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        # Folder selection
        folder_label = ttk.Label(container, text="Image Folder:")
        folder_label.grid(row=0, column=0, sticky="w", pady=5)
        folder_entry = ttk.Entry(container, textvariable=self.folder_path, width=50)
        folder_entry.grid(row=0, column=1, padx=5, pady=5)
        browse_folder_btn = ttk.Button(container, text="Browse", command=self.browse_folder)
        browse_folder_btn.grid(row=0, column=2, padx=5, pady=5)

        # Output file selection
        file_label = ttk.Label(container, text="Output File:")
        file_label.grid(row=1, column=0, sticky="w", pady=5)
        file_entry = ttk.Entry(container, textvariable=self.save_path, width=50)
        file_entry.grid(row=1, column=1, padx=5, pady=5)
        browse_file_btn = ttk.Button(container, text="Save As", command=self.choose_save_path)
        browse_file_btn.grid(row=1, column=2, padx=5, pady=5)

        # Export format selection
        format_label = ttk.Label(container, text="Export Format:")
        format_label.grid(row=2, column=0, sticky="w", pady=5)
        format_combo = ttk.Combobox(
            container,
            textvariable=self.export_format,
            values=["Excel", "CSV", "TXT", "PDF"],
            state="readonly"
        )
        format_combo.grid(row=2, column=1, padx=5, pady=5)

        # Generate button
        generate_btn = ttk.Button(container, text="Generate Descriptions", command=self.generate_descriptions)
        generate_btn.grid(row=3, column=0, columnspan=3, pady=10)

        # Progress bar
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            container, orient="horizontal", length=400, mode="determinate", variable=self.progress_var
        )
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=5)

        # Log text (white background, black text)
        self.log_text = tk.Text(container, height=10, bg="white", fg="black", wrap="word")
        self.log_text.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=5)
        container.rowconfigure(5, weight=1)  # Make the text widget expandable

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            self.folder_path.set(folder)

    def choose_save_path(self):
        """
        Based on chosen export format, set default extension.
        """
        selected_format = self.export_format.get().lower()
        if selected_format == "excel":
            ext = ".xlsx"
            filetypes = [("Excel files", "*.xlsx")]
        elif selected_format == "csv":
            ext = ".csv"
            filetypes = [("CSV files", "*.csv")]
        elif selected_format == "txt":
            ext = ".txt"
            filetypes = [("Text files", "*.txt")]
        else:  # pdf
            ext = ".pdf"
            filetypes = [("PDF files", "*.pdf")]

        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=ext,
            filetypes=filetypes
        )
        if path:
            self.save_path.set(path)

    def generate_descriptions(self):
        folder = self.folder_path.get().strip()
        save_path = self.save_path.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please select a valid folder with images.")
            return
        if not save_path:
            messagebox.showerror("Error", "Please specify an output file.")
            return

        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"Loading images from: {folder}\n")

        # Ensure imports
        try:
            ImportManager.ensure_imports()
        except ImportError as e:
            messagebox.showerror("Missing Library", str(e))
            return

        # Load images
        processor = ImageProcessor(folder)
        try:
            processor.load_images()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        total = len(processor.images)
        self.log_text.insert(tk.END, f"Found {total} images.\n")
        self.progress_var.set(0)
        self.progress_bar["maximum"] = total
        self.root.update_idletasks()

        generator = DescriptionGenerator()
        batch = Batch(processor, generator)

        # Process images
        index = 0
        for img in processor.images:
            self.log_text.insert(tk.END, f"Processing {os.path.basename(img.path)}...\n")
            self.log_text.see(tk.END)
            # Generate description
            desc_text = batch.description_generator.generate_description(img.path)
            img.description.content = desc_text  # store in existing object

            index += 1
            self.progress_var.set(index)
            self.root.update_idletasks()

        self.log_text.insert(tk.END, "All images processed.\n")

        # Export
        exporter = Exporter()
        export_format = self.export_format.get().lower()

        if export_format == "excel":
            exporter.export_to_excel(processor.images, save_path)
        elif export_format == "csv":
            exporter.export_to_csv(processor.images, save_path)
        elif export_format == "txt":
            exporter.export_to_txt(processor.images, save_path)
        else:  # pdf
            exporter.export_to_pdf(processor.images, save_path)

        self.log_text.insert(tk.END, f"Exported to: {save_path}\n")
        messagebox.showinfo("Done", f"Finished exporting to {save_path}!")
