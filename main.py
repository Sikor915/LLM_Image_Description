from ollama import chat
import ollama
import os
import xlsxwriter
import re
from rich.console import Console
from rich.table import Table
from rich.progress import track
from tqdm import tqdm

# Create a console for rich output
console = Console()

def get_file_names(folder_path, items):
    items[:] = os.listdir(folder_path)  # List all items in the folder
    files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
    return files, items

# User input with visual feedback
console.print("[bold cyan]Enter the path to the folder that has images in it:[/bold cyan]", end=" ")
folder_path = input()
match = re.search(r'[^\\/]+$', folder_path)
workbook_name = str(match.group()) + '.xlsx'
workbook = xlsxwriter.Workbook(workbook_name)
worksheet = workbook.add_worksheet()
console.print(f"[bold green]Generating report: {workbook_name}[/bold green]")
items = []
get_file_names(folder_path, items)

# Table to display results
table = Table(title="Image Descriptions")
table.add_column("Image File", style="bold yellow")
table.add_column("Description", style="bold green")

for x in tqdm(range(len(items)), desc="Processing images..."):
    image_path = os.path.join(folder_path, items[x])
    response = ollama.chat(
        model='llama3.2-vision',
        messages=[
            {
                'role': 'user',
                'content': 'This is an image taken from a plane, describe it',
                'images': [image_path]
            }
        ]
    )
    # Check if "content" exists in the response
    match = re.search(r"content='(.*?)'", str(response))
    if match:
        description = match.group(1)
    else:
        description = "No description found or an error occurred."
    
    # Write to Excel
    worksheet.write('A' + str(x + 2), items[x])  # Write file name
    worksheet.write('B' + str(x + 2), description)  # Write description

    # Add to the table for CLI output
    table.add_row(items[x], description)

workbook.close()

# Display the summary table
console.print(table)
console.print("[bold green]Done! Your report is ready.[/bold green]")
