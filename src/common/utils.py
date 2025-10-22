import os
import csv
import hashlib

def sanitize_filename(filename):
    """
    Sanitize filenames by removing invalid characters.
    
    Args:
        filename (str): The filename to sanitize.
    
    Returns:
        str: The sanitized filename.
    """
    if filename is None or filename.strip() == "":
        return "noname"
    invalid_characters = '<>:"/\\|?*\n\t'
    for char in invalid_characters:
        filename = filename.replace(char, '')
    return filename

def generate_unique_filename(base_path, title, timestamp):
    """
    Generate a unique filename for the Markdown file.
    
    Args:
        base_path (str): The base directory path.
        title (str): The title of the conversation.
        timestamp (datetime): The creation timestamp.
    
    Returns:
        str: The full path to the unique filename.
    """
    title = title if title.strip() != "" else "noname"
    timestamp_str = timestamp.strftime("%y%m%d-%H%M")
    file_path = os.path.join(base_path, f"{timestamp_str} {title}.md")
    return file_path

def hash_content(conversation_text):
    """
    Generate an MD5 hash of the conversation text.
    
    Args:
        conversation_text (str): The text to hash.
    
    Returns:
        str: The MD5 hash as a hexadecimal string.
    """
    return hashlib.md5(conversation_text.encode('utf-8')).hexdigest()

def load_index(index_file):
    """
    Load the existing CSV index if it exists.
    
    Args:
        index_file (str): The path to the CSV index file.
    
    Returns:
        dict: A dictionary mapping keys to index entries.
    """
    index = {}
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["Created"], row["Filename"].split(" ", 1)[1])
                index[key] = {"path": row["Filename"], "hash": row.get("content_hash", "")}
    return index

def write_csv_index(metadata_list, index_file):
    """
    Write the CSV index with updated metadata.
    
    Args:
        metadata_list (list): List of metadata dictionaries.
        index_file (str): The path to the CSV index file.
    """
    # Convert all keys to expected case for sorting
    for meta in metadata_list:
        if "Created" in meta and "created" not in meta:
            meta["created"] = meta["Created"]
        elif "created" in meta and "Created" not in meta:
            meta["Created"] = meta["created"]
            
    # Sort by created date
    metadata_list.sort(key=lambda meta: meta.get("created", meta.get("Created", "")))
    
    fieldnames = ["Filename", "Created", "Modified", "Word Count", "Char Count",
                  "User Posts", "Assistant Posts", "Tool Posts", "Status", "Voice", "content_hash"]
    
    with open(index_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for meta in metadata_list:
            writer.writerow({
                "Filename": meta.get("filename", meta.get("Filename", "")),
                "Created": meta.get("created", meta.get("Created", "")),
                "Modified": meta.get("modified", meta.get("Modified", "")),
                "Word Count": meta.get("word_count", meta.get("Word Count", 0)),
                "Char Count": meta.get("char_count", meta.get("Char Count", 0)),
                "User Posts": meta.get("user_posts", meta.get("User Posts", 0)),
                "Assistant Posts": meta.get("assistant_posts", meta.get("Assistant Posts", 0)),
                "Tool Posts": meta.get("tool_posts", meta.get("Tool Posts", 0)),
                "Status": meta.get("status", meta.get("Status", "")),
                "Voice": meta.get("voice", meta.get("Voice", "")),
                "content_hash": meta.get("content_hash", meta.get("content_hash", ""))
            })