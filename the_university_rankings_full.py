#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE World University Rankings Scraper (2011–2026)
Fetches both 'Rankings' and 'Key statistics' tables from official THE JSON endpoints.
Saves filtered results in both CSV and JSON formats for database insertion.
"""

import requests
import pandas as pd
import os
import time
import json

BASE_URL = "https://www.timeshighereducation.com/json/ranking_tables/world_university_rankings"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

# Database field mappings
RANKINGS_FIELDS = {
    'rank': 'Rank',
    'name': 'Name',
    'scores_overall': 'Overall',
    'scores_teaching': 'Teaching',
    'scores_research': 'Research Environment',
    'scores_citations': 'Research Quality',
    'scores_industry_income': 'Industry',
    'scores_international_outlook': 'International Outlook'
}

KEY_STATISTICS_FIELDS = {
    'rank': 'Rank',
    'name': 'Name',
    'stats_number_students': 'No. of FTE students',
    'stats_student_staff_ratio': 'No. of students per staff',
    'stats_pc_intl_students': 'International students',
    'stats_female_male_ratio': 'Female:Male ratio'
}


def fetch_json(url):
    """Safely fetch JSON and return dict or None."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            return r.json()
        print(f"[WARN] {r.status_code} for {url}")
    except Exception as e:
        print(f"[ERROR] Fetch failed for {url}: {e}")
    return None


def filter_data_for_db(data, year, field_mapping):
    """Filter JSON data to only include fields needed for database insertion."""
    if not data or "data" not in data:
        return None

    filtered_data = []

    for university in data["data"]:
        filtered_university = {'year': year}  # Add year field

        # Map and filter fields
        for json_field, db_field in field_mapping.items():
            value = university.get(json_field, '')

            # Special handling for rank field
            if json_field == 'rank' and isinstance(value, str) and value.startswith('='):
                # Separate rank prefix and numeric value
                filtered_university['rank_prefix'] = '='
                filtered_university[db_field] = value[1:]  # Remove '=' prefix
            else:
                # Clean up numeric values
                if json_field.startswith('scores_') or json_field == 'stats_student_staff_ratio':
                    # Remove commas and handle empty values
                    value = str(value).replace(',', '') if value else ''
                filtered_university[db_field] = value

        filtered_data.append(filtered_university)

    return {"data": filtered_data}


def save_outputs(year, data, name):
    """Save both CSV and JSON versions for a given dataset."""
    if not data or "data" not in data:
        print(f"[WARN] No data for {year} {name}.")
        return

    os.makedirs("outputs/json", exist_ok=True)
    os.makedirs("outputs/csv", exist_ok=True)

    # JSON output
    json_path = f"outputs/json/THE_{year}_{name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # CSV output
    csv_path = f"outputs/csv/THE_{year}_{name}.csv"
    df = pd.DataFrame(data["data"])
    df.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"[DONE] {year} {name}: {len(df)} rows → {csv_path}")


def process_year(year):
    """Fetch and save both tables for a single year."""
    print(f"\n=== YEAR {year} ===")

    # Rankings
    rankings_url = f"{BASE_URL}/{year}"
    rankings_data = fetch_json(rankings_url)
    if rankings_data:
        filtered_rankings = filter_data_for_db(rankings_data, year, RANKINGS_FIELDS)
        save_outputs(year, filtered_rankings, "rankings")
    time.sleep(1)

    # Key statistics
    key_stats_url = f"{BASE_URL}/{year}/key_statistics"
    key_stats_data = fetch_json(key_stats_url)
    if key_stats_data:
        filtered_key_stats = filter_data_for_db(key_stats_data, year, KEY_STATISTICS_FIELDS)
        save_outputs(year, filtered_key_stats, "key_statistics")
    time.sleep(1)


def main():
    os.makedirs("outputs", exist_ok=True)

    for year in range(2011, 2027):
        process_year(year)

    print("\n✅ All years completed successfully!")
    print("📂 JSON files: ./outputs/json")
    print("📂 CSV files:  ./outputs/csv")

if __name__ == "__main__":
    main()
