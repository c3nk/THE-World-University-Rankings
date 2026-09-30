#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE Rankings Database Insert Generator
Generates SQLite INSERT statements from filtered CSV files
"""

import pandas as pd
import os
from pathlib import Path
import re
from typing import Iterable, List, Optional

RANKINGS_COLUMNS = (
    'Rank', 'Name', 'Overall', 'Teaching', 'Research Environment',
    'Research Quality', 'Industry', 'International Outlook', 'Country',
)
KEY_STATISTICS_COLUMNS = (
    'Rank', 'Name', 'No. of FTE students', 'No. of students per staff',
    'International students', 'Female:Male ratio', 'Country',
)
IMPACT_OVERALL_COLUMNS = (
    'Rank', 'Name', 'Overall', 'SDG17_Score', 'Location', 'No. of FTE students',
    'No. of students per staff', 'International students', 'Female:Male ratio',
)
IMPACT_SDG_COLUMNS = (
    'Rank', 'Name', 'Overall', 'Location', 'No. of FTE students',
    'No. of students per staff', 'International students', 'Female:Male ratio',
)

def _is_blank(value) -> bool:
    """Return whether a CSV cell cannot satisfy a NOT NULL text column."""
    return pd.isna(value) or not str(value).strip()

def validate_frame(df: pd.DataFrame, columns: Iterable[str], source: str) -> None:
    """Reject frames that would fail import or omit part of the dataset."""
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{source}: missing required columns: {', '.join(missing)}")
    if any(_is_blank(value) for value in df['Name']):
        raise ValueError(f"{source}: university name is required")

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

def generate_rankings_insert(df: pd.DataFrame, year: int, subject: Optional[str] = None) -> List[str]:
    """Generate INSERT statements for Rankings table"""
    source = "Subject_Rankings" if subject is not None else "Rankings"
    validate_frame(df, RANKINGS_COLUMNS, source)
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
            clean_value(row.get('International Outlook', '')),
            clean_value(row.get('Country', ''))
        ]

        table = "Subject_Rankings" if subject is not None else "Rankings"
        subject_column = ", subject" if subject is not None else ""
        if subject is not None:
            values.append(clean_value(subject))

        sql = f"INSERT INTO {table} (year, rank, rank_prefix, name, overall, teaching, research_environment, research_quality, industry, international_outlook, country{subject_column}) VALUES ({', '.join(values)});"
        inserts.append(sql)

    return inserts

def generate_key_statistics_insert(df: pd.DataFrame, year: int, subject: Optional[str] = None) -> List[str]:
    """Generate INSERT statements for Key_Statistics table"""
    source = "Subject_Key_Statistics" if subject is not None else "Key_Statistics"
    validate_frame(df, KEY_STATISTICS_COLUMNS, source)
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
            clean_value(row.get('Female:Male ratio', '')),
            clean_value(row.get('Country', ''))
        ]

        table = "Subject_Key_Statistics" if subject is not None else "Key_Statistics"
        subject_column = ", subject" if subject is not None else ""
        if subject is not None:
            values.append(clean_value(subject))

        sql = f"INSERT INTO {table} (year, rank, rank_prefix, name, fte_students, students_per_staff, international_students, female_male_ratio, country{subject_column}) VALUES ({', '.join(values)});"
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
    country TEXT,
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
    country TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Impact Overall Table
CREATE TABLE IF NOT EXISTS Impact_Overall (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    rank TEXT,
    rank_prefix TEXT,
    name TEXT NOT NULL,
    overall TEXT,
    sdg17_score TEXT,
    location TEXT,
    fte_students TEXT,
    students_per_staff TEXT,
    international_students TEXT,
    female_male_ratio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Impact SDG Table
CREATE TABLE IF NOT EXISTS Impact_SDG (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sdg_number INTEGER NOT NULL CHECK (sdg_number BETWEEN 1 AND 17),
    year INTEGER NOT NULL,
    rank TEXT,
    rank_prefix TEXT,
    name TEXT NOT NULL,
    overall TEXT,
    sdg_score TEXT,
    sdg_rank TEXT,
    location TEXT,
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
CREATE INDEX IF NOT EXISTS idx_impact_overall_year ON Impact_Overall(year);
CREATE INDEX IF NOT EXISTS idx_impact_sdg_year ON Impact_SDG(year);
CREATE INDEX IF NOT EXISTS idx_impact_sdg_name ON Impact_SDG(name);
"""
    for table in ("Rankings", "Key_Statistics"):
        start = tables_sql.index(f"CREATE TABLE IF NOT EXISTS {table} (")
        end = tables_sql.index(");", start) + 2
        subject_sql = tables_sql[start:end].replace(
            f"{table} (", f"Subject_{table} (", 1
        ).replace("    year INTEGER NOT NULL,", "    year INTEGER NOT NULL,\n    subject TEXT NOT NULL,", 1)
        tables_sql += "\n" + subject_sql + "\n"
        tables_sql += f"CREATE INDEX IF NOT EXISTS idx_subject_{table.lower()} ON Subject_{table}(year, subject);\n"
    tables_sql += "CREATE INDEX IF NOT EXISTS idx_impact_sdg_number ON Impact_SDG(year, sdg_number);\n"
    return tables_sql

def generate_impact_overall_insert(df: pd.DataFrame, year: int) -> list:
    """Generate INSERT statements for Impact_Overall table"""
    validate_frame(df, IMPACT_OVERALL_COLUMNS, "Impact_Overall")
    inserts = []
    for _, row in df.iterrows():
        values = [
            str(year),
            clean_value(row.get('Rank', '')),
            clean_value(row.get('rank_prefix', '')),
            clean_value(row.get('Name', '')),
            clean_value(row.get('Overall', '')),
            clean_value(row.get('SDG17_Score', '')),
            clean_value(row.get('Location', '')),
            clean_value(row.get('No. of FTE students', '')),
            clean_value(row.get('No. of students per staff', '')),
            clean_value(row.get('International students', '')),
            clean_value(row.get('Female:Male ratio', '')),
        ]
        cols = 'year, rank, rank_prefix, name, overall, sdg17_score, location, fte_students, students_per_staff, international_students, female_male_ratio'
        sql = f"INSERT INTO Impact_Overall ({cols}) VALUES ({', '.join(values)});"
        inserts.append(sql)
    return inserts


def generate_impact_sdg_insert(df: pd.DataFrame, year: int, sdg_number: int) -> list:
    """Generate INSERT statements for Impact_SDG table"""
    inserts = []
    if not 1 <= sdg_number <= 17:
        raise ValueError("SDG number must be between 1 and 17")
    sdg_score_col = f"SDG{sdg_number}_Score"
    sdg_rank_col = f"SDG{sdg_number}_Rank"
    validate_frame(df, (*IMPACT_SDG_COLUMNS, sdg_score_col, sdg_rank_col), "Impact_SDG")

    for _, row in df.iterrows():
        values = [
            str(year),
            clean_value(row.get('Rank', '')),
            clean_value(row.get('rank_prefix', '')),
            clean_value(row.get('Name', '')),
            clean_value(row.get('Overall', '')),
            clean_value(row.get(sdg_score_col, '')),
            clean_value(row.get(sdg_rank_col, '')),
            clean_value(row.get('Location', '')),
            clean_value(row.get('No. of FTE students', '')),
            clean_value(row.get('No. of students per staff', '')),
            clean_value(row.get('International students', '')),
            clean_value(row.get('Female:Male ratio', '')),
        ]
        values.append(str(sdg_number))
        cols = 'year, rank, rank_prefix, name, overall, sdg_score, sdg_rank, location, fte_students, students_per_staff, international_students, female_male_ratio, sdg_number'
        sql = f"INSERT INTO Impact_SDG ({cols}) VALUES ({', '.join(values)});"
        inserts.append(sql)
    return inserts


def process_csv_files(csv_root="outputs/csv"):
    """Read current outputs, falling back to legacy general files per filename."""
    root = Path(csv_root)
    general_files = {p.name: p for p in root.glob("THE_*.csv")}
    general_files.update({p.name: p for p in (root / "general").glob("THE_*.csv")})
    sources = [(p, "general") for p in general_files.values()]
    sources += [(p, "subject") for p in (root / "subject").glob("THE_*.csv")]
    sources += [(p, "impact") for p in (root / "impact").glob("THE_*_impact_overall.csv")]
    sources += [(p, "sdg") for p in (root / "impact" / "sdg").glob("THE_*_impact_*.csv")]
    all_sql = ["-- Table Creation SQL", create_table_sql(), "\n-- Data Insert SQL\n"]
    for path, category in sorted(sources):
        print(f"Reading: {path}")
        match = re.fullmatch(r"THE_(\d{4})_(.+)\.csv", path.name)
        if not match:
            raise ValueError(f"Unexpected dataset filename: {path}")
        year, dataset = int(match[1]), match[2]
        # Preserve display ranks, leading zeros, and literal strings such as NA.
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        subject = None
        sdg_number = None
        if category == "sdg":
            sdg = re.fullmatch(r"impact_sdg([1-9]|1[0-7])_rankings", dataset)
            if not sdg:
                raise ValueError(f"Unexpected SDG filename: {path}")
            sdg_number = int(sdg[1])
        elif category == "subject":
            parsed = re.fullmatch(r"(.+)_(rankings|key_statistics)", dataset)
            if not parsed:
                raise ValueError(f"Unexpected subject filename: {path}")
            subject, dataset = parsed.groups()
        if category in {"general", "subject"} and dataset not in {"rankings", "key_statistics"}:
            raise ValueError(f"Unexpected dataset: {path}")
        try:
            if category == "impact":
                inserts = generate_impact_overall_insert(df, year)
            elif category == "sdg":
                inserts = generate_impact_sdg_insert(df, year, sdg_number)
            elif dataset == "rankings":
                inserts = generate_rankings_insert(df, year, subject)
            else:
                inserts = generate_key_statistics_insert(df, year, subject)
        except ValueError as error:
            raise ValueError(f"{path}: {error}") from error
        all_sql.extend(inserts)
        print(f"  → {len(inserts)} INSERTs")
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
    print("  - Table creation statements (Rankings, Key_Statistics, Subject_Rankings, Subject_Key_Statistics, Impact_Overall, Impact_SDG)")
    print("  - INSERT statements for Rankings table")
    print("  - INSERT statements for Key_Statistics table")
    print("  - INSERT statements for Subject_Rankings table")
    print("  - INSERT statements for Subject_Key_Statistics table")
    print("  - INSERT statements for Impact_Overall table")
    print("  - INSERT statements for Impact_SDG table")
    print("\n🔄 To use:")
    print("  sqlite3 your_database.db < outputs/the_rankings_insert.sql")

if __name__ == "__main__":
    main()
