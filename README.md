# Convert Your Downloaded ChatGPT Archive Conversations to Markdown

## Overview

This project processes conversation data exported from ChatGPT (in JSON format) and converts it into individual Markdown files. The application is designed to work with modern ChatGPT export formats and organizes the output by default into a structured folder hierarchy based on year and month. Each Markdown file is prefixed with a date-time stamp in the format `YYMMDD-HHMM` followed by the sanitized conversation title, making it easy to track when each conversation occurred.

You can export your ChatGPT data by following the official OpenAI documentation:

[How do I export my ChatGPT history and data?](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)

## Note

This repository starts with a single commit to provide a clean, focused version for public sharing.

## Getting Started

### Prerequisites

- Python 3.x (tested with Python 3.10+)
- Command line/terminal access

### Installation & Configuration

1. Clone or download this repository to your local machine.
2. Create your local configuration file:
   ```bash
   cp config/config.py config/config_loc.py
   ```
3. Edit `config/config_loc.py` to set your specific paths:
   ```python
   INPUT_FOLDER = "/path/to/your/input/folder"
   ARCHIVE_DIR = "/path/to/your/output/folder"
   ```
4. No additional libraries are required since the script uses only the Python Standard Library.

### Usage

To run the script with the default settings (which use the folder hierarchy):

```bash
python main.py
```

This will:

- Process the conversations JSON file from the configured INPUT_FOLDER
- Output Markdown files to ARCHIVE_DIR organized by year and month
- Create/update a CSV index file (`_index.csv`) in the output directory
- Skip unchanged conversations based on content hash comparison

If you prefer to have all Markdown files output into a single folder without the date-based hierarchy, run:

```bash
python main.py --no-folders
```

### First Run Setup

If you haven't created `config/config_loc.py`, the script will use default relative paths:

- Input: `./input/conversations.json`
- Output: `./output/`

This allows immediate testing with sample data placed in an `input` folder.

### Output Structure

By default, the output will be organized as follows:

```
output/
  ├── _index.csv                         # CSV index of all conversations
  ├── 2023/
  │     ├── 230300/                      # Month folder (YYMM00)
  │     │      ├── 230215-1030 Conversation Title.md
  │     │      ├── 230220-1405 Another Conversation.md
  ├── 2024/
         ├── 240100/
         │      ├── 240105-0915 Yet Another Chat.md
```

With the `--no-folders` option, all Markdown files will be placed directly in the output directory.

## Project Structure

- **`main.py`**: The main script that orchestrates the conversion process
- **`parser.py`**: Handles parsing the conversation structure from JSON
- **`chat_processor.py`**: Contains functions for analyzing conversations and metadata
- **`utils.py`**: Utility functions for file handling and CSV operations
- **`config/`**: Configuration files (create `config_loc.py` for your paths)
- **`README.md`**: This documentation file

### Features

- Converts ChatGPT conversations to Markdown with proper formatting
- Detects and properly formats web search results and code execution outputs
- Identifies voice conversations and includes audio duration information
- Maintains a CSV index with metadata about each conversation
- Prevents duplicate processing by tracking content hashes
- Provides summary statistics about conversation types and content

### Analysis Summary

When you run the script, it provides an analysis summary in the terminal that looks like this:

```
=== Analysis Summary ===
Total Role Counts:
  system: 745
  user: 17475
  tool: 3126
  assistant: 20947
Total Tool Types:
  unknown: 19
Total Assistant JSON Instances: 0
```

This summary provides:

- **Role Counts**: How many messages from each participant type (system, user, assistant, tool)
- **Tool Types**: Counts of different tool types used in conversations
  - "unknown" tool types are those not explicitly handled by the script (currently only "web_search" and "code_interpreter" have specific handlers)
- **Assistant JSON Instances**: Count of JSON data found in assistant messages

### File Processing

The script uses content hashing to avoid reprocessing unchanged conversations. When a conversation is unchanged, you'll see output like:

```
Skipped: /path/to/output/2023/230100/230131-1731 Example Conversation.md (unchanged)
```

This efficiency feature helps when repeatedly processing large export files.

## License and Attribution

This project is open source and available under the MIT License.

This script is a modified version of the [gavi/chatgpt-markdown](https://github.com/gavi/chatgpt-markdown) repository. Proper attribution is given to the original author, and modifications have been made to support configurable input/output directories and to implement a folder hierarchy based on year and month.

For more details, please refer to the LICENSE file.
