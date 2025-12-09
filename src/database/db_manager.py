"""
Database Manager

Handles database initialization, connection management, and data loading from CSV files.
"""

import sqlite3
import os
from pathlib import Path
import pandas as pd
from typing import Dict

from src.config import DB_DIR, DB_PATH, CSV_FILES


def initialize_database(force_recreate: bool = False) -> str:
    """
    Initialize the SQLite database from CSV files.
    
    Creates the database directory if it doesn't exist, loads CSV data into
    pandas DataFrames, and creates SQLite tables from the DataFrames.
    
    Args:
        force_recreate: If True, recreate database even if it exists.
                       If False, skip if database already exists.
    
    Returns:
        str: Path to the created database file
        
    Raises:
        FileNotFoundError: If any CSV file is missing
        Exception: If database creation fails
    """
    # Check if database already exists
    if DB_PATH.exists() and not force_recreate:
        print(f"Database already exists at: {DB_PATH}")
        return str(DB_PATH)
    
    # Create database directory if it doesn't exist
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all CSV files into DataFrames
    print("Loading CSV data...")
    dataframes = {}
    
    for table_name, csv_path in CSV_FILES.items():
        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {csv_path}\n"
                f"Please ensure all data files are in the 'data' directory."
            )
        
        # Load CSV into DataFrame
        df = pd.read_csv(csv_path)
        dataframes[table_name] = df
        print(f"  ✓ Loaded {table_name}: {len(df)} rows")
    
    # Create SQLite database
    print(f"\nCreating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Create tables from DataFrames
        for table_name, df in dataframes.items():
            # Write DataFrame to SQLite table
            # if_exists='replace' will drop and recreate the table
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"  ✓ Created table '{table_name}' in database")
        
        # Commit changes
        conn.commit()
        print(f"\n✓ Database initialization complete!")
        print(f"  Location: {DB_PATH}")
        print(f"  Tables created: {len(dataframes)}")
        
    except Exception as e:
        print(f"\n✗ Error creating database: {e}")
        raise
    
    finally:
        # Always close the connection
        conn.close()
    
    return str(DB_PATH)


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection object
        
    Raises:
        FileNotFoundError: If database doesn't exist
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at: {DB_PATH}\n"
            f"Please run initialize_database() first."
        )
    
    return sqlite3.connect(DB_PATH)


def verify_database() -> Dict[str, int]:
    """
    Verify database exists and contains expected tables.
    
    Returns:
        Dict[str, int]: Dictionary mapping table names to row counts
        
    Raises:
        FileNotFoundError: If database doesn't exist
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at: {DB_PATH}\n"
            f"Please run initialize_database() first."
        )
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Get row count for each table
    table_counts = {}
    for (table_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        table_counts[table_name] = count
    
    conn.close()
    
    return table_counts


if __name__ == "__main__":
    # Allow running this module directly to initialize the database
    print("=" * 80)
    print("Database Initialization")
    print("=" * 80)
    print()
    
    db_path = initialize_database(force_recreate=False)
    
    print("\nVerifying database...")
    table_counts = verify_database()
    
    print("\nDatabase Summary:")
    print("-" * 80)
    for table_name, count in table_counts.items():
        print(f"  {table_name:25} {count:>10,} rows")
    print("-" * 80)
