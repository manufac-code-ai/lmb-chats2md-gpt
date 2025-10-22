#!/usr/bin/env python3
import json
import os
import argparse
import sys
import csv
from datetime import datetime
from src.common.config.config import INPUT_FOLDER, INPUT_FILE, ARCHIVE_DIR, INDEX_FILE, RECURSION_LIMIT
from src.common.utils import load_index, write_csv_index, sanitize_filename, generate_unique_filename, hash_content
from src.llm_chatgpt.processor import extract_metadata, format_yaml_header, analyze_conversation
from src.llm_chatgpt.parser import get_conversation

sys.setrecursionlimit(RECURSION_LIMIT)

def main(use_date_folders):
    input_path = os.path.join(INPUT_FOLDER, INPUT_FILE)
    if not os.path.isdir(INPUT_FOLDER) or not os.path.exists(input_path):
        print(f"Error: {input_path} not found or inaccessible.")
        return

    if not os.path.isdir(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    index = load_index(INDEX_FILE)
    metadata_list = []
    
    total_roles = {}
    total_tool_types = {}
    total_assistant_json = 0

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            title = sanitize_filename(item.get("title"))
            root_node_id = next(node_id for node_id, node in item['mapping'].items() if node.get('parent') is None)
            conversation_list = []
            is_voice = get_conversation(root_node_id, item['mapping'], conversation_list)
            conversation_text = '\n'.join(conversation_list)

            date_obj = datetime.fromtimestamp(item["create_time"])
            key = (date_obj.strftime("%Y-%m-%d %H:%M"), title)
            content_hash = hash_content(conversation_text)

            if use_date_folders:
                year_folder = os.path.join(ARCHIVE_DIR, str(date_obj.year))
                month_folder = date_obj.strftime("%y%m") + "00"
                date_folder = os.path.join(year_folder, month_folder)
                if not os.path.isdir(date_folder):
                    os.makedirs(date_folder)
                file_path = generate_unique_filename(date_folder, title, date_obj)
            else:
                file_path = generate_unique_filename(ARCHIVE_DIR, title, date_obj)

            roles, tool_types, assistant_json = analyze_conversation(item['mapping'])
            for role, count in roles.items():
                total_roles[role] = total_roles.get(role, 0) + count
            for tool, count in tool_types.items():
                total_tool_types[tool] = total_tool_types.get(tool, 0) + count
            total_assistant_json += assistant_json

            if '{' in conversation_text:
                print(f"Warning: Possible JSON leftover in {file_path}")

            if key not in index or index[key]["hash"] != content_hash:
                meta = extract_metadata(item, conversation_text, is_voice)
                yaml_header = format_yaml_header(meta)
                with open(file_path, 'w', encoding='utf-8') as outfile:
                    outfile.write(yaml_header + conversation_text)
                meta["filename"] = os.path.splitext(os.path.basename(file_path))[0]
                meta["content_hash"] = content_hash
                metadata_list.append(meta)
                print(f"Updated: {file_path}")
            else:
                print(f"Skipped: {file_path} (unchanged)")

    if metadata_list:
        existing_metas = []
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_metas = list(reader)
        all_metas = existing_metas + metadata_list
        write_csv_index(all_metas, INDEX_FILE)

    print("\n=== Analysis Summary ===")
    print("Total Role Counts:")
    for role, count in total_roles.items():
        print(f"  {role}: {count}")
    print("Total Tool Types:")
    for tool, count in total_tool_types.items():
        print(f"  {tool}: {count}")
    print(f"Total Assistant JSON Instances: {total_assistant_json}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process ChatGPT conversation data.')
    parser.add_argument('--no-folders', action='store_true',
                        help='Store files in a single output directory (default: use date folders)')
    args = parser.parse_args()
    main(use_date_folders=not args.no_folders)