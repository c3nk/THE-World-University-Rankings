# THE World University Rankings Scraper

Scrapes **Times Higher Education – World University Rankings** pages for **2024, 2025, 2026**.

- Two CSVs per year:
  - `THE_Rankings_[YEAR].csv`
  - `THE_KeyStatistics_[YEAR].csv`
- Available data: **2024 (2671 rows), 2025 (2855 rows), 2026 (3118 rows)**
- ⚠️ **Current limitation**: THE site loads only ~35 universities initially
- ❓ **Tested methods**: URL parameters, dropdown selection - none bypass the limit
- Test mode: defaults to **first 35 rows** per tab (per year)
- Full extraction: limited by site behavior
- Adds a `Year` column to each CSV
- Uses **Selenium (headless)** + **BeautifulSoup** + **pandas**
- Auto-installs ChromeDriver via **webdriver-manager**
- Stealth mode with minimal browser fingerprinting

> ⚠️ This is for evaluation/testing. Respect website terms of use and robots.txt. Avoid overloading the site.

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Test run (first 500 rows each)
python the_scraper.py --headless --years 2024 2025 2026

# Full data extraction (all available rows)
python the_scraper.py --headless --full --years 2024 2025 2026

# Verbose mode with detailed progress
python the_scraper.py --headless --verbose --years 2024 --limit 100

# Output directory (default: output/)
ls output/
```

### Arguments

- `--years 2024 2025 2026` — which years to scrape.
- `--limit 500` — max rows per tab for custom limits.
- `--full` — extract complete datasets (uses actual row counts per year).
- `--outdir output` — where to save CSVs.
- `--headless` / `--no-headless` — headless Chrome on/off.
- `--timeout 30` — wait timeout per load.
- `--scroll-wait 300` — max scrolling seconds per tab (increased for full datasets).
- `--verbose` / `-v` — enable verbose output for detailed progress information.

### Anti-Detection Features

- **Default Selenium UA**: Uses Selenium's default user agent for compatibility
- **Human-like Behavior**: Respects timeouts and doesn't hammer the server
- **Headless Mode**: Runs invisibly but appears as normal browser to websites

### Notes

- If the "Key statistics" tab cannot be found or the structure changes, the script creates an empty CSV with just the `Year` header and prints a warning.
- Selectors are written to be resilient, but the website could change. Adjust `safe_click_tab_by_text` or `extract_table_html` as needed.
- For full runs after testing, just increase/remove `--limit` (or set it to a large value) and consider raising `--scroll-wait`.

### License

MIT (for this script). This does not grant rights over the data obtained from the target website.
