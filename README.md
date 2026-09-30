# THE World University Rankings Scraper

<p align="center">
  <img src="THE-World-University-Rankings.png" alt="THE World University Rankings Scraper" width="800">
</p>

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/c3nk/THE-World-University-Rankings?style=social)](https://github.com/c3nk/THE-World-University-Rankings/stargazers)

> 🎓 Python application that fetches Times Higher Education World University Rankings and Sustainability Impact Ratings via the official JSON API endpoints – fast, reliable, no browser automation required!

### 🌟 Key Features

- **Official JSON API Integration**: Connects to THE’s published ranking endpoints without browser automation
- **Year Selection**: Default ranges are 2011–2026 for world/subject rankings and 2019–2026 for impact rankings; availability depends on the source endpoint
- **Dual Output Format**: Clean CSV files + filtered JSON copies
- **Database Ready**: Optional SQL generation included
- **Three Data Types**: Rankings scores, Key statistics tables, and UN SDG Impact Ratings
- **Interactive CLI**: Prompts guide you to pull general, subject, or impact rankings for the desired year range

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/c3nk/THE-World-University-Rankings.git
cd THE-World-University-Rankings

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 🚀 Quick Start

```bash
# Fetch all years' data (2011-2026)
python the_university_rankings_full.py

# The script asks whether to pull general rankings, subject rankings, both, or
# Sustainability Impact Ratings (option 4), and for the year range to process.

# Check outputs
ls outputs/csv/
ls outputs/json/
```

### 📊 Output Structure

```
outputs/
├── csv/
│   ├── general/
│   │   ├── THE_2026_rankings.csv
│   │   ├── THE_2026_key_statistics.csv
│   │   └── ... (general rankings per year)
│   ├── subject/
│   │   ├── THE_2026_arts-and-humanities_rankings.csv
│   │   ├── THE_2026_arts-and-humanities_key_statistics.csv
│   │   └── ... (subject + year combinations)
│   └── impact/
│       ├── THE_2026_impact_overall.csv
│       └── sdg/
│           ├── THE_2026_impact_sdg1_rankings.csv
│           ├── THE_2026_impact_sdg2_rankings.csv
│           └── ... (17 SDGs per year)
├── json/
│   ├── general/
│   │   ├── THE_2026_rankings.json
│   │   ├── THE_2026_key_statistics.json
│   │   └── ... (general rankings per year)
│   ├── subject/
│   │   ├── THE_2026_arts-and-humanities_rankings.json
│   │   ├── THE_2026_arts-and-humanities_key_statistics.json
│   │   └── ... (subject + year combinations)
│   └── impact/
│       ├── THE_2026_impact_overall.json
│       └── sdg/
│           ├── THE_2026_impact_sdg1_rankings.json
│           ├── THE_2026_impact_sdg2_rankings.json
│           └── ... (17 SDGs per year)
├── THE_2026_impact_data.csv          # Consolidated overall + SDG scores/ranks
└── the_rankings_insert.sql           # (Optional) SQL script
```

### 🗄️ Database Schema

#### Rankings Table

| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Ranking year (2011-2026) |
| rank | TEXT | Display rank, including ranges and reporter labels |
| rank_prefix | TEXT | Rank prefix (e.g., '=' for ties) |
| name | TEXT | University name |
| country | TEXT | University country |
| overall | TEXT | Overall score (0-100) |
| teaching | TEXT | Teaching score |
| research_environment | TEXT | Research environment score |
| research_quality | TEXT | Research quality score |
| industry | TEXT | Industry income score |
| international_outlook | TEXT | International outlook score |

#### Key Statistics Table

| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Year |
| rank | TEXT | Rank |
| rank_prefix | TEXT | Rank prefix |
| name | TEXT | University name |
| country | TEXT | University country |
| fte_students | TEXT | Full-time equivalent students |
| students_per_staff | TEXT | Student-to-staff ratio |
| international_students | TEXT | % of international students |
| female_male_ratio | TEXT | Female to male ratio |

#### Impact Overall Table

| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Ranking year (2019-2026) |
| rank | TEXT | Overall impact rank |
| rank_prefix | TEXT | Rank prefix (e.g., '=' for ties) |
| name | TEXT | University name |
| overall | TEXT | Overall impact score |
| sdg17_score | TEXT | Score for SDG 17 (Partnerships) |
| location | TEXT | University country |
| fte_students | TEXT | Full-time equivalent students |
| students_per_staff | TEXT | Student-to-staff ratio |
| international_students | TEXT | % of international students |
| female_male_ratio | TEXT | Female to male ratio |

#### Impact SDG Table

Each row retains its SDG identity.

| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Ranking year (2019-2026) |
| sdg_number | INTEGER | Required SDG number, 1–17 |
| rank | TEXT | Rank within this SDG |
| rank_prefix | TEXT | Rank prefix |
| name | TEXT | University name |
| overall | TEXT | Overall impact score |
| sdg_score | TEXT | Score for this specific SDG |
| sdg_rank | TEXT | Rank for this specific SDG |
| location | TEXT | University country |
| fte_students | TEXT | Full-time equivalent students |
| students_per_staff | TEXT | Student-to-staff ratio |
| international_students | TEXT | % of international students |
| female_male_ratio | TEXT | Female to male ratio |

#### Subject Tables and Import Behavior

`Subject_Rankings` and `Subject_Key_Statistics` use the corresponding general
schemas plus a required `subject` slug. General data comes from
`outputs/csv/general/`, with a per-filename fallback to legacy files directly
under `outputs/csv/`; when both exist, the current file wins.

Ranks and scores are stored as TEXT to preserve ranges, ties, and source labels.
Each table also has an auto-incrementing `id` and a `created_at` timestamp.
CSV/JSON column names retain their display labels (`Name`, `Rank`, `Overall`,
`Country`); SQL uses the lowercase names shown above. The combined impact CSV
contains overall participants with their available SDG scores, ranks and tie
prefixes. Individual SDG files also include SDG-only participants. A year
with no overall impact response skips that consolidated file and still saves
the individual SDG files. The `Impact_Overall` SQL table stores SDG 17's score;
all per-SDG records are stored in `Impact_SDG`.

Generate and import into a **new SQLite database** when adopting this schema.
`CREATE TABLE IF NOT EXISTS` does not migrate existing tables. Old `Impact_SDG`
rows have no recoverable SDG identity; rebuild them from the individual CSVs.
Imports append records, so importing the same SQL twice duplicates rows.
Malformed CSVs stop generation instead of silently producing a partial export.

### 💡 Usage Examples

#### Basic Data Analysis

```python
import pandas as pd

# Load ranking data
df = pd.read_csv('outputs/csv/general/THE_2026_rankings.csv')

# Top 10 universities in 2026
df['numeric_rank'] = pd.to_numeric(df['Rank'], errors='coerce')
top_10 = df.nsmallest(10, 'numeric_rank')
print(top_10[['Rank', 'Name', 'Overall']])

# Find Turkish universities
turkish_unis = df[df['Country'].isin(['Turkey', 'Türkiye'])]
print(turkish_unis[['year', 'Rank', 'Name', 'Overall']])

# Oxford in the selected year (combine yearly files for a trend)
oxford = df[df['Name'].str.contains('Oxford', case=False, na=False)]
print(oxford[['year', 'Rank', 'Overall']])

# Load impact data
impact = pd.read_csv('outputs/csv/impact/THE_2026_impact_overall.csv')
impact['numeric_rank'] = pd.to_numeric(impact['Rank'], errors='coerce')
top_impact = impact.nsmallest(10, 'numeric_rank')
print(top_impact[['Rank', 'Name', 'Overall']])
```

#### Visualization Example

This optional example requires `pip install matplotlib`.

```python
import matplotlib.pyplot as plt

# Visualize top 20 universities
top_20 = df[df['year'] == 2026].nsmallest(20, 'numeric_rank')

plt.figure(figsize=(12, 8))
plt.barh(top_20['Name'], pd.to_numeric(top_20['Overall'], errors='coerce'))
plt.xlabel('Overall Score')
plt.title('Top 20 Universities - THE 2026')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
```

### 🔧 Advanced Usage: SQL Import

Converts all CSV outputs (general, subject, key stats, impact overall, impact SDG)
into a SQLite database.

```bash
# Generate SQL script
python db_insert_generator.py

# Import to SQLite
sqlite3 university_rankings.db < outputs/the_rankings_insert.sql

# Query example
sqlite3 university_rankings.db "SELECT name, overall FROM rankings WHERE year=2026 AND rank <> '' AND rank NOT GLOB '*[^0-9]*' ORDER BY CAST(rank AS INTEGER) LIMIT 10;"
```

### ⚙️ Technical Details

#### Data Processing Pipeline
1. **Fetch**: Direct HTTP GET requests to THE API (general, subject, and impact endpoints)
2. **Parse**: JSON response parsing with error handling
3. **Clean**: Preserve missing values and zero scores, separate tie prefixes from display ranks
4. **Export**: Dual format (CSV + JSON) with year-based naming and category folders (general / subject / impact)

#### Interactive CLI
- Prompts whether to retrieve general rankings, subject rankings, both, or Sustainability Impact Ratings
- Requests a year or year range (default 2011-2026 for rankings, 2019-2026 for impact)
- Offers optional filtering to a subset of subject slugs or SDG slugs while preserving slug-based filenames

#### Available Slugs

| Rankings | Subject Slugs (11) | SDG Slugs (17) |
|----------|-------------------|----------------|
| General | arts-and-humanities, business-and-economics, clinical-pre-clinical-health, computer-science, education, engineering, law, life-sciences, physical-sciences, psychology, social-sciences | sdg1_rankings – sdg17_rankings |

Each SDG slug maps to readable columns in the output: e.g. `sdg3_rankings` → `SDG3_Score`, `sdg3_rankings_rank` → `SDG3_Rank`.

### ⚠️ Important Notes

- **Data Source**: Official THE JSON API endpoints
- **Rate Limiting**: Built-in delays to respect API limits
- **Execution Time**: Depends on selected datasets, years, response times, and request delays
- **Update Frequency**: THE updates rankings annually in September

### 📈 Use Cases

- 🎓 Academic research on university performance trends
- 📊 Data visualization projects
- 🔍 Institutional benchmarking
- 🤖 Machine learning datasets
- 📱 University comparison applications

### 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: requests` | Run `pip install -r requirements.txt` |
| Connection timeout | Check your internet connection and retry |
| Empty CSV files | THE API might be down, try later |
| Invalid JSON | API structure may have changed, open an issue |
| Import error | Ensure you're using Python 3.9+ |
| `NotOpenSSLWarning` | Recreate the virtual environment using a Python build linked to OpenSSL 1.1.1+ rather than LibreSSL |

### Tests

Run the offline regression checks:

```bash
python -m unittest discover -s tests -v
```

### 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).

### 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### ⚖️ Legal Disclaimer

This scraper uses publicly available THE API endpoints for educational and research purposes. Please respect [Times Higher Education's Terms of Service](https://www.timeshighereducation.com/terms-and-conditions). Not for commercial redistribution.

### 🙏 Acknowledgments

- **Data Source**: [Times Higher Education World University Rankings](https://www.timeshighereducation.com/world-university-rankings)
- **Inspiration**: The need for accessible academic data
- **Contributors**: Thanks to all contributors!

### 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/c3nk/THE-World-University-Rankings/issues)
- **Author**: [@c3nk](https://github.com/c3nk)

### 📊 Project Statistics

![GitHub last commit](https://img.shields.io/github/last-commit/c3nk/THE-World-University-Rankings)
![GitHub repo size](https://img.shields.io/github/repo-size/c3nk/THE-World-University-Rankings)
![GitHub language count](https://img.shields.io/github/languages/count/c3nk/THE-World-University-Rankings)

---

## 🌟 Why This Scraper?

| Feature | This Project | Browser-based Scrapers |
|---------|--------------|------------------------|
| Speed | ⚡ Fast (1-5 min) | 🐌 Slow (30+ min) |
| Reliability | ✅ High | ⚠️ Fragile |
| Dependencies | 📦 Minimal (2 packages) | 🏗️ Heavy (10+ packages) |
| Maintenance | 🔧 Easy | 😰 Complex |
| Resource Usage | 💚 Low | 🔴 High |

---

<div align="center">

**[⭐ Star this repo](https://github.com/c3nk/THE-World-University-Rankings)** if you find it useful!

Made with ♥ in Istanbul

</div>