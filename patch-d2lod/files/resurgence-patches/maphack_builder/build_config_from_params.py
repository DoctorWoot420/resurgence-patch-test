from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/merge-files', methods=['POST'])
def merge_files():
    data = request.json

    # Access the rune_design key in a case-insensitive manner
    rune_design_param = data.get('rune_design', '').lower()
    if rune_design_param not in ['cosmic rainbow', 'classic']:
        return jsonify({"error": "Invalid rune_design parameter"}), 400
    
    # Access the rune_design key in a case-insensitive manner
    filter_blocks_param = data.get('filter_blocks', '').lower()
    if filter_blocks_param not in ['sorceress', 'paladin', 'necromancer', 'amazon', 'assassin', 'barbarian', 'druid']:
        return jsonify({"error": "Invalid filter_blocks parameter"}), 400

    # Fetch base file
    base_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/BH_cosmic.cfg"
    base_response = requests.get(base_url)
    if base_response.status_code != 200:
        return jsonify({"error": "Failed to fetch base file"}), 400
    base_content = base_response.text

    # Fetch rune design block file
    if rune_design_param == 'cosmic-rainbow':
        rune_design_block_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/filter-blocks/runes-cosmic-rainbow.bh"
    else:
        rune_design_block_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/filter-blocks/runes-classic.bh"

    rune_design_block_response = requests.get(rune_design_block_url)
    if rune_design_block_response.status_code != 200:
        return jsonify({"error": f"Failed to fetch block file for {rune_design_param}"}), 400
    rune_design_block_content = rune_design_block_response.text

    # Insert block content into base content
    base_lines = base_content.splitlines()
    rune_design_insert_index = None
    for i, line in enumerate(base_lines):
        if "// start runes block" in line.lower():
            rune_design_insert_index = i + 3
            break

    if rune_design_insert_index is None:
        return jsonify({"error": "Indicator '// START RUNES BLOCK' not found in base file"}), 400
    


    # Fetch filter blocks block file
    if filter_blocks_param == 'sorceress':
        filter_blocks_block_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/filter-blocks/builds-sorceress.bh"
    if filter_blocks_param == 'barbarian':
        filter_blocks_block_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/filter-blocks/builds-barbarian.bh"
    if filter_blocks_param == 'leveling mid gear':
        filter_blocks_block_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/filter-blocks/leveling-mid-gear.bh"
    else:
        filter_blocks_block_url = "https://raw.githubusercontent.com/DoctorWoot420/cosmic-resurgence-bh/main/new-temp/filter-blocks/builds-sorceress.bh"

    filter_blocks_block_response = requests.get(filter_blocks_block_url)
    if filter_blocks_block_response.status_code != 200:
        return jsonify({"error": f"Failed to fetch block file for {filter_blocks_param}"}), 400
    filter_blocks_block_content = filter_blocks_block_response.text

    # Insert block content into base content
    base_lines = base_content.splitlines()
    filter_blocks_insert_index = None
    for i, line in enumerate(base_lines):
        if "// start filter blocks" in line.lower():
            filter_blocks_insert_index = i + 3
            break

    if filter_blocks_insert_index is None:
        return jsonify({"error": "Indicator '// START FILTER BLOCKS' not found in base file"}), 400


    # Build merged file lines from all blocks

    merged_lines = base_lines[:filter_blocks_insert_index] + filter_blocks_block_content.splitlines() + base_lines[filter_blocks_insert_index:rune_design_insert_index] + rune_design_block_content.splitlines() + base_lines[rune_design_insert_index:]
    merged_content = "\n".join(merged_lines)

    return merged_content

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8083)
