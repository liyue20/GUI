import json

with open('your_file.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

html_content = data.get('layout_json', '')

with open('output.html', 'w', encoding='utf-8') as output_file:
    output_file.write(html_content)
