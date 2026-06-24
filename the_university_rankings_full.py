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
import re
from html import unescape

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
    'location': 'Country',
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
    'location': 'Country',
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

IMPACT_BASE_URL = "https://www.timeshighereducation.com/json/ranking_tables/world_impact_rankings"

SDG_SLUGS = [
    "sdg1_rankings",
    "sdg2_rankings",
    "sdg3_rankings",
    "sdg4_rankings",
    "sdg5_rankings",
    "sdg6_rankings",
    "sdg7_rankings",
    "sdg8_rankings",
    "sdg9_rankings",
    "sdg10_rankings",
    "sdg11_rankings",
    "sdg12_rankings",
    "sdg13_rankings",
    "sdg14_rankings",
    "sdg15_rankings",
    "sdg16_rankings",
    "sdg17_rankings",
]

IMPACT_OVERALL_FIELDS = {
    'rank': 'Rank',
    'name': 'Name',
    'scores_overall': 'Overall',
    'sdg17_rankings_score': 'SDG17_Score',
    'location': 'Location',
    'stats_number_students': 'No. of FTE students',
    'stats_student_staff_ratio': 'No. of students per staff',
    'stats_pc_intl_students': 'International students',
    'stats_female_male_ratio': 'Female:Male ratio',
}

IMPACT_SDG_FIELDS = {
    'rank': 'Rank',
    'name': 'Name',
    'scores_overall': 'Overall',
    'location': 'Location',
    'stats_number_students': 'No. of FTE students',
    'stats_student_staff_ratio': 'No. of students per staff',
    'stats_pc_intl_students': 'International students',
    'stats_female_male_ratio': 'Female:Male ratio',
}

SDG_COLUMN_NAMES = {slug: f"SDG{slug.split('_')[0][3:]}_Score" for slug in SDG_SLUGS}
SDG_RANK_COLUMN_NAMES = {slug: f"SDG{slug.split('_')[0][3:]}_Rank" for slug in SDG_SLUGS}


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


def extract_country_from_location(location_value):
    """Extract country text from location HTML with safe fallbacks."""
    if location_value is None:
        return ""
    raw_text = str(location_value).strip()
    if not raw_text:
        return ""
    span_matches = re.findall(r"<span[^>]*>([^<]+)</span>", raw_text, flags=re.IGNORECASE)
    cleaned_spans = [unescape(item).strip() for item in span_matches if item and item.strip()]
    if cleaned_spans:
        return cleaned_spans[-1]
    plain_text = re.sub(r"<[^>]+>", " ", raw_text)
    plain_text = re.sub(r"\s+", " ", unescape(plain_text)).strip()
    if "," in plain_text:
        return plain_text.split(",")[-1].strip()
    return plain_text


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
            if json_field == 'location':
                filtered_university[db_field] = extract_country_from_location(value)
                continue

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


def filter_impact_overall_data(data, year):
    """Filter overall Impact Ratings data for DB fields."""
    if not data or "data" not in data:
        return None

    filtered_data = []
    for university in data["data"]:
        entry = {'year': year}
        for json_field, db_field in IMPACT_OVERALL_FIELDS.items():
            value = university.get(json_field, '')
            if json_field == 'rank' and isinstance(value, str) and value.startswith('='):
                entry['rank_prefix'] = '='
                entry[db_field] = value[1:]
            elif json_field.startswith('scores_') or json_field == 'stats_student_staff_ratio':
                value = str(value).replace(',', '') if value else ''
                entry[db_field] = value
            else:
                entry[db_field] = value
        if 'best_scores' in university:
            entry['best_scores'] = json.dumps(university['best_scores'], ensure_ascii=False)
        filtered_data.append(entry)
    return {"data": filtered_data}


def filter_impact_sdg_data(data, year, sdg_slug):
    """Filter individual SDG Impact Ratings data for DB fields."""
    if not data or "data" not in data:
        return None

    filtered_data = []
    sdg_score_key = sdg_slug
    sdg_rank_key = f"{sdg_slug}_rank"
    sdg_score_col = SDG_COLUMN_NAMES.get(sdg_slug, sdg_slug)
    sdg_rank_col = SDG_RANK_COLUMN_NAMES.get(sdg_slug, f"{sdg_slug}_rank")

    for university in data["data"]:
        entry = {'year': year}
        for json_field, db_field in IMPACT_SDG_FIELDS.items():
            value = university.get(json_field, '')
            if json_field == 'rank' and isinstance(value, str) and value.startswith('='):
                entry['rank_prefix'] = '='
                entry[db_field] = value[1:]
            elif json_field.startswith('scores_') or json_field == 'stats_student_staff_ratio':
                value = str(value).replace(',', '') if value else ''
                entry[db_field] = value
            else:
                entry[db_field] = value
        entry[sdg_score_col] = university.get(sdg_score_key, '')
        entry[sdg_rank_col] = university.get(sdg_rank_key, '')
        filtered_data.append(entry)
    return {"data": filtered_data}


def _fetch_all_sdg_scores(year: int, sdg_slugs: list) -> dict:
    """Fetch all SDG datasets and return a lookup: {university_name: {col: val, ...}}."""
    lookup = {}
    for slug in sdg_slugs:
        url = f"https://www.timeshighereducation.com/json/ranking_tables/{slug}/{year}"
        raw = fetch_json(url)
        time.sleep(1)
        if not raw or "data" not in raw:
            continue
        score_col = SDG_COLUMN_NAMES.get(slug, slug)
        rank_col = SDG_RANK_COLUMN_NAMES.get(slug, f"{slug}_rank")
        score_key = slug
        rank_key = f"{slug}_rank"
        for uni in raw["data"]:
            name = uni.get("name", "")
            if not name:
                continue
            if name not in lookup:
                lookup[name] = {}
            lookup[name][score_col] = uni.get(score_key, "")
            lookup[name][rank_col] = uni.get(rank_key, "")
    return lookup


def process_impact_year(year, sdg_slugs=None):
    """Fetch overall Impact Ratings and merge all SDG scores into a single wide CSV."""
    print(f"\n=== IMPACT OVERALL {year} ===")
    url = f"{IMPACT_BASE_URL}/{year}"
    data = fetch_json(url)
    if not data:
        return
    filtered = filter_impact_overall_data(data, year)
    time.sleep(1)

    # Fetch per-SDG data and merge into overall rows
    slugs = list(sdg_slugs or SDG_SLUGS)
    sdg_lookup = _fetch_all_sdg_scores(year, slugs)
    for entry in filtered["data"]:
        name = entry.get("Name", "")
        sdg_data = sdg_lookup.get(name, {})
        entry.update(sdg_data)

    save_outputs(year, filtered, "impact_overall", category="impact")

    # Also save individual SDG files
    for slug in slugs:
        process_impact_sdg(year, slug)


def process_impact_sdg(year: int, sdg_slug: str) -> None:
    """Fetch and save an individual SDG ranking for a year."""
    print(f"\n=== IMPACT SDG {year} – {sdg_slug} ===")
    url = f"https://www.timeshighereducation.com/json/ranking_tables/{sdg_slug}/{year}"
    data = fetch_json(url)
    if data:
        filtered = filter_impact_sdg_data(data, year, sdg_slug)
        save_outputs(year, filtered, f"impact_{sdg_slug}", category="impact/sdg")
    time.sleep(1)


def process_impact_sdgs_for_year(year: int, sdg_slugs: Optional[Iterable[str]] = None) -> None:
    """Batch process multiple SDGs for a year."""
    slugs = list(sdg_slugs or SDG_SLUGS)
    for slug in slugs:
        process_impact_sdg(year, slug)


def ask_years_range(default_range: str = "2011-2026") -> list[int]:
    """Prompt for a year or range of years to process."""
    parts = default_range.split("-")
    default_start = int(parts[0])
    default_end = int(parts[1])
    while True:
        response = input(
            f"Enter the year or range to process (e.g. {default_range}) [blank = full range]: "
        ).strip()
        if not response:
            return list(range(default_start, default_end + 1))
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
    """Prompt user for general/subject/impact/both processing mode."""
    options = {"1": "general", "2": "subject", "3": "both", "4": "impact"}
    while True:
        print("\nWhich dataset do you want to fetch?")
        print("  1) General Rankings/Key Statistics")
        print("  2) Subject Rankings/Key Statistics")
        print("  3) Both General + Subject (default)")
        print("  4) Sustainability Impact Ratings (SDGs)")
        choice = input("Selection [1-4]: ").strip() or "3"
        if choice in options:
            return options[choice]
        print("Invalid selection; please enter 1, 2, 3, or 4.")


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


def ask_sdg_slugs() -> list[str]:
    """Prompt for specific SDG slugs or return the full list."""
    display_list = ", ".join(SDG_SLUGS)
    print(f"\nSupported SDG slugs: {display_list}")
    while True:
        response = input(
            "Enter comma-separated slugs to process or leave blank for all SDGs: "
        ).strip()
        if not response:
            return SDG_SLUGS
        slugs = [slug.strip() for slug in response.split(",") if slug.strip()]
        invalid = [slug for slug in slugs if slug not in SDG_SLUGS]
        if invalid:
            print(f"Invalid slug(s): {', '.join(invalid)}. Please try again.")
            continue
        return slugs


def run_interactive() -> None:
    """Run the scraper based on interactive user input."""
    mode = ask_data_mode()
    performed_general = False
    performed_subject = False
    performed_impact = False

    if mode == "impact":
        years = ask_years_range(default_range="2019-2026")
        sdg_slugs = ask_sdg_slugs()
        performed_impact = True
        for year in years:
            process_impact_year(year, sdg_slugs)
    else:
        years = ask_years_range()
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
    parts = []
    if performed_general:
        parts.append("General")
    if performed_subject:
        parts.append("Subject")
    if performed_impact:
        parts.append("Impact Ratings")
    if parts:
        print(f"• {' and '.join(parts)} data downloaded.")


def main():
    os.makedirs("outputs", exist_ok=True)
    run_interactive()

if __name__ == "__main__":
    main()
