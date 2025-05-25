"""
Configuration settings for ChatGPT Markdown converter.
This module centralizes all configurable parameters.
"""
import os

# Default paths (portable for any user)
INPUT_FOLDER = "./input"
INPUT_FILE = "conversations.json"
ARCHIVE_DIR = "./output"

# Processing settings
USE_DATE_FOLDERS = True
RECURSION_LIMIT = 5000

# Try to import local configuration overrides
try:
    from config.config_loc import *
except ImportError:
    # No local config found, using defaults
    pass

# Derived settings
INDEX_FILE = os.path.join(ARCHIVE_DIR, "_index.csv")