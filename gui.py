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

        # Global style overrides
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
        style.configure("TCombobox", foreground="black")

        # Variables
        self.folder_path = tk.StringVar()
        self.save_path = tk.StringVar()
        self.export_format = tk.StringVar(value="CSV")  # Default export format

        # Store images (with descriptions) after generation
        self.images = []

        # Build the GUI
        self.create_widgets()

    def create_widgets(self):
        # Main container frame
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        # --- Folder selection ---
        folder_frame = ttk.Frame(container)
        folder_frame.pack(fill="x", pady=5)

        folder_label = ttk.Label(folder_frame, text="Image Folder:")
        folder_label.pack(side="left")

        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side="left", padx=5)

        browse_folder_btn = ttk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_folder,
            cursor="hand2"  # pointer cursor
        )
        browse_folder_btn.pack(side="left", padx=5)

        # --- Generate Descriptions Button & Progress Bar in the same row ---
        generate_frame = ttk.Frame(container)
        generate_frame.pack(fill="x", pady=5)

        generate_btn = ttk.Button(
            generate_frame,
            text="1) Generate Descriptions",
            command=self.generate_descriptions,
            cursor="hand2"  # pointer cursor
        )
        generate_btn.pack(side="left", padx=5)

        # Progress bar on the right of the Generate button
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            generate_frame,
            orient="horizontal",
            length=200,
            mode="determinate",
            variable=self.progress_var
        )
        self.progress_bar.pack(side="right", padx=5)

        # --- Export format selection ---
        format_frame = ttk.Frame(container)
        format_frame.pack(fill="x", pady=5)

        format_label = ttk.Label(format_frame, text="Export Format:")
        format_label.pack(side="left")

        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.export_format,
            values=["Excel", "CSV", "TXT", "PDF"],
            state="readonly",
            width=10
        )
        format_combo.pack(side="left", padx=5)
        # Bind the format selection change event to update the file extension
        format_combo.bind("<<ComboboxSelected>>", self.update_save_path_extension)

        # --- Output file selection ---
        output_frame = ttk.Frame(container)
        output_frame.pack(fill="x", pady=5)

        file_label = ttk.Label(output_frame, text="Output File:")
        file_label.pack(side="left")

        file_entry = ttk.Entry(output_frame, textvariable=self.save_path, width=50)
        file_entry.pack(side="left", padx=5)

        browse_file_btn = ttk.Button(
            output_frame,
            text="Save As",
            command=self.choose_save_path,
            cursor="hand2"  # pointer cursor
        )
        browse_file_btn.pack(side="left", padx=5)

        # --- Export Button ---
        export_frame = ttk.Frame(container)
        export_frame.pack(fill="x", pady=5)

        export_btn = ttk.Button(
            export_frame,
            text="2) Export",
            command=self.export_descriptions,
            cursor="hand2"  # pointer cursor
        )
        export_btn.pack(side="left", padx=5)

        # --- Log text (white background, black text) ---
        self.log_text = tk.Text(container, height=10, bg="white", fg="black", wrap="word")
        self.log_text.pack(fill="both", expand=True)

        # --- Authors note (one line) ---
        authors_note = (
            "Authors: Mateusz F., Justyn R., Kasper S., "
            "Mikołaj M., Konrad W., Krzysztof W."
        )
        authors_label = tk.Label(
            container,
            text=authors_note,
            bg="white",
            fg="black",
            font=("Helvetica", 8, "italic")
        )
        # Align bottom-right (if enough horizontal space, it will appear on one line)
        authors_label.pack(side="bottom", anchor="e", pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            self.folder_path.set(folder)

    def choose_save_path(self):
        """
        Based on chosen export format, set default extension.
        """
        selected_format = self.export_format.get().lower()
        ext = self.get_extension(selected_format)
        filetypes = [(f"{selected_format.upper()} files", f"*{ext}")]
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=ext,
            filetypes=filetypes
        )
        if path:
            self.save_path.set(path)

    def get_extension(self, format_type):
        """
        Return the correct file extension for the chosen format.
        """
        return {
            "excel": ".xlsx",
            "csv": ".csv",
            "txt": ".txt",
            "pdf": ".pdf"
        }.get(format_type, ".csv")

    def update_save_path_extension(self, event=None):
        """
        Update the file extension in the save path when the export format changes.
        """
        current_path = self.save_path.get().strip()
        if current_path:
            new_ext = self.get_extension(self.export_format.get().lower())
            base_path, _ = os.path.splitext(current_path)  # Remove old extension
            new_path = f"{base_path}{new_ext}"
            self.save_path.set(new_path)

    def generate_descriptions(self):
        folder = self.folder_path.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please select a folder with images first.")
            return

        # Clear old logs
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"Loading images from: {folder}\n")

        try:
            ImportManager.ensure_imports()
        except ImportError as e:
            messagebox.showerror("Missing Library", str(e))
            return

        processor = ImageProcessor(folder)
        try:
            processor.load_images()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        total = len(processor.images)
        self.log_text.insert(tk.END, f"Found {total} images.\n")

        self.progress_bar["maximum"] = total
        self.progress_var.set(0)

        generator = DescriptionGenerator()
        batch = Batch(processor, generator)

        for i, img in enumerate(processor.images, start=1):
            filename = os.path.basename(img.path)
            self.log_text.insert(tk.END, f"Processing {filename}...\n")
            self.log_text.see(tk.END)
            desc_text = batch.description_generator.generate_description(img.path)
            if img.description is None:
                from core.description import Description
                img.description = Description(desc_text)
            else:
                img.description.content = desc_text

            self.progress_var.set(i)
            self.root.update_idletasks()

        self.images = processor.images
        self.log_text.insert(tk.END, "All images processed.\n")
        messagebox.showinfo(
            "Done Generating",
            "Descriptions generated. Now select export format and file, then click Export!"
        )

    def export_descriptions(self):
        if not self.images:
            messagebox.showerror("Error", "No descriptions available. Please generate first.")
            return

        save_path = self.save_path.get().strip()
        if not save_path:
            messagebox.showerror("Error", "Please select an output file to export.")
            return

        export_format = self.export_format.get().lower()
        exporter = Exporter()

        self.log_text.insert(tk.END, f"Exporting to {export_format.upper()}...\n")
        self.log_text.see(tk.END)

        if export_format == "excel":
            exporter.export_to_excel(self.images, save_path)
        elif export_format == "csv":
            exporter.export_to_csv(self.images, save_path)
        elif export_format == "txt":
            exporter.export_to_txt(self.images, save_path)
        else:
            exporter.export_to_pdf(self.images, save_path)

        self.log_text.insert(tk.END, f"Exported to: {save_path}\n")
        messagebox.showinfo("Done", f"Finished exporting to {save_path}!")
