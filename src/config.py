"""
Configuration Module

Centralized configuration management for the Text-to-SQL application.
Contains database settings, LLM configuration, and application constants.
"""

import os
from pathlib import Path


# PROJECT PATHS


# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory containing CSV files
DATA_DIR = PROJECT_ROOT / "data"

# Database directory for SQLite files
DB_DIR = PROJECT_ROOT / "db_data"

# Database file name
DB_NAME = "ecommerce.db"

# Full database path
DB_PATH = DB_DIR / DB_NAME



# LLM CONFIGURATION

# Google Gemini model name
LLM_MODEL = "gemini-2.5-flash"

# Temperature for LLM responses (0 = deterministic, 1 = creative)
LLM_TEMPERATURE = 0

# Maximum tokens for LLM responses (None = no limit)
LLM_MAX_TOKENS = None

# Timeout for LLM requests in seconds (None = no timeout)
LLM_TIMEOUT = None

# Maximum retries for LLM requests
LLM_MAX_RETRIES = 2


# APPLICATION SETTINGS

# Maximum number of retry attempts for SQL error correction
MAX_SQL_RETRY_ATTEMPTS = 3

# Default limit for SQL query results
DEFAULT_SQL_LIMIT = 10


# CSV DATA FILES

# Dictionary mapping table names to their CSV file paths
CSV_FILES = {
    "products": DATA_DIR / "products.csv",
    "users": DATA_DIR / "users.csv",
    "orders": DATA_DIR / "orders.csv",
    "order_items": DATA_DIR / "order_items.csv",
    "inventory_items": DATA_DIR / "inventory_items.csv",
    "distribution_centers": DATA_DIR / "distribution_centers.csv",
    "events": DATA_DIR / "events.csv",
}



# ENVIRONMENT VARIABLES


def get_google_api_key() -> str:
    """
    Retrieve the Google API key from environment variables.
    
    Returns:
        str: The Google API key
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    return api_key
