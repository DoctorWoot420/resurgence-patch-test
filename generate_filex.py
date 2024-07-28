import os
import json
import datetime
import hashlib

file_names_to_ignore_crc = [
    "d2gl.ini",
    "d2fps.ini",
    "SGD2FreeResolution.json"
]

file_names_to_exclude = [
    "index.html",
    "manifest.json"
]

def compute_crc(file_path):
    buf_size = 65536  # Read file in chunks of 64kb
    crc = 0
    with open(file_path, 'rb') as f:
        while chunk := f.read(buf_size):
            crc = hashlib.crc32(chunk, crc)
    return format(crc & 0xFFFFFFFF, '08x')

def generate_html_index(folder_path, files):
    html_content = f"""
<html>
<head><title>Index of {folder_path}</title></head>
<body>
<h1>Index of {folder_path}</h1><hr><pre>
<a href="../index.html">../</a>
"""
    for file in files:
        if file['name'] not in file_names_to_exclude:
            file_link = f"{file['name']}/" if file['is_dir'] else file['name']
            html_content += f"<a href='{file_link}'>{file['name']}</a>"
            if not file['is_dir']:
                html_content += f"\t\t\t{file['last_modified']}\t\t\t{file['content_length']}\n"
            else:
                html_content += "\n"
    html_content += "</pre><hr></body></html>"
    return html_content

def process_folder(folder_path):
    files = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            files.append({
                'name': item,
                'last_modified': '',
                'content_length': '',
                'is_dir': True
            })
            process_folder(item_path)
        else:
            if item not in file_names_to_exclude:
                file_info = {
                    'name': item,
                    'crc': compute_crc(item_path),
                    'last_modified': datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat(),
                    'content_length': os.path.getsize(item_path),
                    'ignore_crc': item in file_names_to_ignore_crc,
                    'deprecated': False,
                    'is_dir': False
                }
                files.append(file_info)
    
    # Save the manifest for the current folder
    manifest = {'files': files}
    manifest_path = os.path.join(folder_path, 'manifest.json')
    with open(manifest_path, 'w') as manifest_file:
        json.dump(manifest, manifest_file, indent=2)
    
    # Generate HTML content for index.html file
    html_content = generate_html_index(folder_path, files)
    html_path = os.path.join(folder_path, 'index.html')
    with open(html_path, 'w') as html_file:
        html_file.write(html_content)

# Start processing from the specified folder
process_folder(os.path.join(os.environ['GITHUB_WORKSPACE'], 'patch-d2lod/files/resurgence-patches'))
