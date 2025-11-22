#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE Rankings Database Insert Generator
Generates SQL INSERT statements from filtered CSV/JSON files
"""

import pandas as pd
import os
import glob
import json
from typing import List

def clean_value(value):
    """Clean and format value for SQL insertion"""
    if pd.isna(value) or value == '':
        return 'NULL'

    # Convert to string and handle special characters
    value_str = str(value).strip()

    # Handle percentages (remove % sign)
    if value_str.endswith('%'):
        value_str = value_str[:-1]

    # Handle ratios (replace : with /)
    if ' : ' in value_str:
        value_str = value_str.replace(' : ', '/')

    # Escape single quotes for SQL
    value_str = value_str.replace("'", "''")

    return f"'{value_str}'"

def generate_rankings_insert(df: pd.DataFrame, year: int) -> List[str]:
    """Generate INSERT statements for Rankings table"""
    inserts = []

    for _, row in df.iterrows():
        values = [
            str(year),  # year
            clean_value(row.get('Rank', '')),
            clean_value(row.get('rank_prefix', '')),  # rank_prefix
            clean_value(row.get('Name', '')),
            clean_value(row.get('Overall', '')),
            clean_value(row.get('Teaching', '')),
            clean_value(row.get('Research Environment', '')),
            clean_value(row.get('Research Quality', '')),
            clean_value(row.get('Industry', '')),
            clean_value(row.get('International Outlook', ''))
        ]

        sql = f"INSERT INTO Rankings (year, rank, rank_prefix, name, overall, teaching, research_environment, research_quality, industry, international_outlook) VALUES ({', '.join(values)});"
        inserts.append(sql)

    return inserts

def generate_key_statistics_insert(df: pd.DataFrame, year: int) -> List[str]:
    """Generate INSERT statements for Key_Statistics table"""
    inserts = []

    for _, row in df.iterrows():
        values = [
            str(year),  # year
            clean_value(row.get('Rank', '')),
            clean_value(row.get('rank_prefix', '')),  # rank_prefix
            clean_value(row.get('Name', '')),
            clean_value(row.get('No. of FTE students', '')),
            clean_value(row.get('No. of students per staff', '')),
            clean_value(row.get('International students', '')),
            clean_value(row.get('Female:Male ratio', ''))
        ]

        sql = f"INSERT INTO Key_Statistics (year, rank, rank_prefix, name, fte_students, students_per_staff, international_students, female_male_ratio) VALUES ({', '.join(values)});"
        inserts.append(sql)

    return inserts

def create_table_sql():
    """Generate table creation SQL"""
    tables_sql = """
-- Rankings Table
CREATE TABLE IF NOT EXISTS Rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    rank TEXT,
    rank_prefix TEXT,
    name TEXT NOT NULL,
    overall TEXT,
    teaching TEXT,
    research_environment TEXT,
    research_quality TEXT,
    industry TEXT,
    international_outlook TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Key Statistics Table
CREATE TABLE IF NOT EXISTS Key_Statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    rank TEXT,
    rank_prefix TEXT,
    name TEXT NOT NULL,
    fte_students TEXT,
    students_per_staff TEXT,
    international_students TEXT,
    female_male_ratio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_rankings_year ON Rankings(year);
CREATE INDEX IF NOT EXISTS idx_rankings_name ON Rankings(name);
CREATE INDEX IF NOT EXISTS idx_key_stats_year ON Key_Statistics(year);
CREATE INDEX IF NOT EXISTS idx_key_stats_name ON Key_Statistics(name);
"""
    return tables_sql

def process_csv_files():
    """Process all CSV files and generate SQL"""
    rankings_files = glob.glob("outputs/csv/THE_*_rankings.csv")
    key_stats_files = glob.glob("outputs/csv/THE_*_key_statistics.csv")

    all_sql = []

    # Add table creation SQL
    all_sql.append("-- Table Creation SQL")
    all_sql.append(create_table_sql())
    all_sql.append("\n-- Data Insert SQL\n")

    # Process Rankings files
    print("Processing Rankings files...")
    for csv_file in sorted(rankings_files):
        print(f"Reading: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            year = int(csv_file.split('_')[1])  # Extract year from filename

            inserts = generate_rankings_insert(df, year)
            all_sql.extend(inserts)
            print(f"Generated {len(inserts)} INSERT statements for Rankings {year}")

        except Exception as e:
            print(f"Error processing {csv_file}: {e}")

    # Process Key Statistics files
    print("\nProcessing Key Statistics files...")
    for csv_file in sorted(key_stats_files):
        print(f"Reading: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            year = int(csv_file.split('_')[1])  # Extract year from filename

            inserts = generate_key_statistics_insert(df, year)
            all_sql.extend(inserts)
            print(f"Generated {len(inserts)} INSERT statements for Key Statistics {year}")

        except Exception as e:
            print(f"Error processing {csv_file}: {e}")

    return all_sql

def save_sql_file(sql_statements: List[str], filename: str = "outputs/the_rankings_insert.sql"):
    """Save SQL statements to file"""
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))

    print(f"\n✅ SQL file saved: {filename}")
    print(f"Total SQL statements: {len(sql_statements)}")

def main():
    print("THE Rankings Database Insert Generator")
    print("=" * 50)

    if not os.path.exists("outputs/csv"):
        print("❌ outputs/csv directory not found!")
        print("Please run the_university_rankings_full.py first to generate data.")
        return

    # Generate SQL
    sql_statements = process_csv_files()

    # Save to file
    save_sql_file(sql_statements)

    print("\n📋 SQL File contains:")
    print("  - Table creation statements")
    print("  - INSERT statements for Rankings table")
    print("  - INSERT statements for Key_Statistics table")
    print("\n🔄 To use:")
    print("  sqlite3 your_database.db < the_rankings_insert.sql")

if __name__ == "__main__":
    main()
