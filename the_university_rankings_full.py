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
from typing import Iterable, Optional

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

SUBJECT_SLUGS = [
    "arts-and-humanities",
    "business-and-economics",
    "computer-science",
    "education",
    "engineering",
    "law",
    "life-sciences",
    "clinical-pre-clinical-health",
    "physical-sciences",
    "psychology",
    "social-sciences",
]

SUBJECT_DISPLAY_NAMES = {
    "arts-and-humanities": "Arts and Humanities",
    "business-and-economics": "Business and Economics",
    "computer-science": "Computer Science",
    "education": "Education Studies",
    "engineering": "Engineering",
    "law": "Law",
    "life-sciences": "Life Sciences",
    "clinical-pre-clinical-health": "Medical and Health",
    "physical-sciences": "Physical Sciences",
    "psychology": "Psychology",
    "social-sciences": "Social Sciences",
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


def get_subject_display_name(subject_slug: str) -> str:
    """Return a human-readable label for a subject slug."""
    return SUBJECT_DISPLAY_NAMES.get(subject_slug, subject_slug.replace('-', ' ').title())


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


def save_outputs(year, data, name, category: str = "general"):
    """Save both CSV and JSON versions for a given dataset."""
    if not data or "data" not in data:
        print(f"[WARN] No data for {year} {name}.")
        return

    json_dir = os.path.join("outputs", "json", category)
    csv_dir = os.path.join("outputs", "csv", category)
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)

    # JSON output
    json_path = os.path.join(json_dir, f"THE_{year}_{name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # CSV output
    csv_path = os.path.join(csv_dir, f"THE_{year}_{name}.csv")
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
        save_outputs(year, filtered_rankings, "rankings", category="general")
    time.sleep(1)

    # Key statistics
    key_stats_url = f"{BASE_URL}/{year}/key_statistics"
    key_stats_data = fetch_json(key_stats_url)
    if key_stats_data:
        filtered_key_stats = filter_data_for_db(key_stats_data, year, KEY_STATISTICS_FIELDS)
        save_outputs(year, filtered_key_stats, "key_statistics", category="general")
    time.sleep(1)


def _build_subject_url(year: int, subject_slug: str, suffix: Optional[str] = None) -> str:
    """Construct subject-specific THE API endpoint."""
    subject_base = f"{BASE_URL}/{year}/subject-ranking/{subject_slug}"
    if suffix:
        return f"{subject_base}/{suffix}"
    return subject_base


def process_subject(year: int, subject_slug: str) -> None:
    """Fetch rankings and key statistics for a subject in a given year."""
    print(f"\n=== SUBJECT {year} – {subject_slug} ===")

    rankings_url = _build_subject_url(year, subject_slug)
    rankings_data = fetch_json(rankings_url)
    if rankings_data:
        filtered_rankings = filter_data_for_db(rankings_data, year, RANKINGS_FIELDS)
        save_outputs(year, filtered_rankings, f"{subject_slug}_rankings", category="subject")
    time.sleep(1)

    key_stats_url = _build_subject_url(year, subject_slug, "key_statistics")
    key_stats_data = fetch_json(key_stats_url)
    if key_stats_data:
        filtered_key_stats = filter_data_for_db(key_stats_data, year, KEY_STATISTICS_FIELDS)
        save_outputs(year, filtered_key_stats, f"{subject_slug}_key_statistics", category="subject")
    time.sleep(1)


def process_subjects_for_year(year: int, subject_slugs: Optional[Iterable[str]] = None) -> None:
    """Batch processor for several subject slugs."""
    slugs = list(subject_slugs or SUBJECT_SLUGS)
    for slug in slugs:
        process_subject(year, slug)


def ask_years_range() -> list[int]:
    """Prompt for a year or range of years to process."""
    default = "2011-2026"
    while True:
        response = input(
            f"Enter the year or range to process (e.g. {default}) [blank = full range]: "
        ).strip()
        if not response:
            return list(range(2011, 2027))
        if "-" in response:
            start_str, end_str = response.split("-", 1)
        else:
            start_str = end_str = response
        try:
            start_year = int(start_str)
            end_year = int(end_str)
        except ValueError:
            print("Year must be a valid number. Please try again.")
            continue
        if start_year > end_year:
            print("Start year cannot be greater than end year.")
            continue
        return list(range(start_year, end_year + 1))


def ask_data_mode() -> str:
    """Prompt user for general/subject/both processing mode."""
    options = {"1": "general", "2": "subject", "3": "both"}
    while True:
        print("\nWhich dataset do you want to fetch?")
        print("  1) General Rankings/Key Statistics")
        print("  2) Subject Rankings/Key Statistics")
        print("  3) Both (default)")
        choice = input("Selection [1-3]: ").strip() or "3"
        if choice in options:
            return options[choice]
        print("Invalid selection; please enter 1, 2, or 3.")


def ask_subject_slugs() -> list[str]:
    """Prompt for specific subject slugs or return the full list."""
    display_list = ", ".join(
        f"{slug} ({get_subject_display_name(slug)})" for slug in SUBJECT_SLUGS
    )
    print(f"\nSupported subject slugs: {display_list}")
    while True:
        response = input(
            "Enter comma-separated slugs to process or leave blank for all subjects: "
        ).strip()
        if not response:
            return SUBJECT_SLUGS
        slugs = [slug.strip() for slug in response.split(",") if slug.strip()]
        invalid = [slug for slug in slugs if slug not in SUBJECT_SLUGS]
        if invalid:
            print(f"Invalid slug(s): {', '.join(invalid)}. Please try again.")
            continue
        return slugs


def run_interactive() -> None:
    """Run the scraper based on interactive user input."""
    mode = ask_data_mode()
    years = ask_years_range()
    performed_general = False
    performed_subject = False

    if mode in {"general", "both"}:
        performed_general = True
        for year in years:
            process_year(year)

    if mode in {"subject", "both"}:
        subject_slugs = ask_subject_slugs()
        performed_subject = True
        for year in years:
            process_subjects_for_year(year, subject_slugs)

    print("\n✅ Processing complete.")
    if performed_general and performed_subject:
        print("• General and subject data downloaded.")
    elif performed_general:
        print("• Only general data downloaded.")
    elif performed_subject:
        print("• Only subject data downloaded.")


def main():
    os.makedirs("outputs", exist_ok=True)
    run_interactive()

if __name__ == "__main__":
    main()
