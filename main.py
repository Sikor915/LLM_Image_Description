from ollama import chat
from ollama import ChatResponse
import ollama
import os
import xlsxwriter
import re

def get_file_names(folder_path, items):
  items[:] = os.listdir(folder_path)  # List all items in the folder
  files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
  return files, items

folder_path = input("enter the path to the folder that has images in it:")
match = re.search(r'[^\\/]+$', folder_path)
workbook_name = str(match.group()) + '.xlsx'
workbook = xlsxwriter.Workbook(workbook_name)
worksheet = workbook.add_worksheet()
print(match.group())
items = []
get_file_names(folder_path, items)
for x in range(len(items)):
  response = ollama.chat(
    model='llama3.2-vision',
    messages=[
      {
        'role': 'user',
        'content': 'this is an image taken from a plane, describe it',
        'images': ['' + folder_path + '/' + items[x]]
      }
    ]
  )
  print(str(response))
  match = re.search(r"content='(.*?)'", str(response))
  print(match)
  worksheet.write('A' + str(x + 2), items[x])
  worksheet.write('B' + str(x + 2), str(match.group(1)))
workbook.close()