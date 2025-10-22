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
TEST_MODE = False

# Try to import local configuration overrides
try:
    from .config_loc import *
except ImportError:
    # No local config found, using defaults
    pass

# Override paths for test mode
if TEST_MODE:
    INPUT_FOLDER = "_testing/input"
    ARCHIVE_DIR = "_testing/output"

# Derived settings
INDEX_FILE = os.path.join(ARCHIVE_DIR, "_index.csv")