# THE World University Rankings Scraper

<p align="center">
  <img src="THE-World-University-Rankings.png" alt="THE World University Rankings Scraper" width="800">
</p>

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/c3nk/THE-World-University-Rankings?style=social)](https://github.com/c3nk/THE-World-University-Rankings/stargazers)

> 🎓 Python application that fetches Times Higher Education World University Rankings via the official JSON API endpoints – fast, reliable, no browser automation required!

[🇬🇧 English](#english)

### 🌟 Key Features

- **Official JSON API Integration**: Connects to THE’s published ranking endpoints without browser automation
- **Complete Dataset**: 16 years of data (2011-2026), ~44,000 total records
- **Dual Output Format**: Clean CSV files + Full JSON backups
- **Database Ready**: Optional SQL generation included
- **Two Data Types**: Rankings scores and Key statistics tables
- **Interactive CLI**: Prompts guide you to pull general or subject rankings for the desired year range

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

# The script asks whether to pull general rankings, subject rankings, or both, and for the year range to process.

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
│   └── subject/
│       ├── THE_2026_arts-and-humanities_rankings.csv
│       ├── THE_2026_arts-and-humanities_key_statistics.csv
│       └── ... (subject + year combinations)
├── json/
│   ├── general/
│   │   ├── THE_2026_rankings.json
│   │   ├── THE_2026_key_statistics.json
│   │   └── ... (general rankings per year)
│   └── subject/
│       ├── THE_2026_arts-and-humanities_rankings.json
│       ├── THE_2026_arts-and-humanities_key_statistics.json
│       └── ... (subject + year combinations)
└── the_rankings_insert.sql           # (Optional) SQL script
```

### 🗄️ Database Schema

#### Rankings Table

| Column | Type | Description |
|--------|------|-------------|
| year | INT | Ranking year (2011-2026) |
| rank | INT | University rank (numeric) |
| rank_prefix | VARCHAR | Rank prefix (e.g., '=' for ties) |
| name | VARCHAR | University name |
| overall | FLOAT | Overall score (0-100) |
| teaching | FLOAT | Teaching score |
| research_environment | FLOAT | Research environment score |
| research_quality | FLOAT | Research quality score |
| industry | FLOAT | Industry income score |
| international_outlook | FLOAT | International outlook score |

#### Key Statistics Table

| Column | Type | Description |
|--------|------|-------------|
| year | INT | Year |
| rank | INT | Rank |
| rank_prefix | VARCHAR | Rank prefix |
| name | VARCHAR | University name |
| fte_students | INT | Full-time equivalent students |
| students_per_staff | FLOAT | Student-to-staff ratio |
| international_students | VARCHAR | % of international students |
| female_male_ratio | VARCHAR | Female to male ratio |

### 💡 Usage Examples

#### Basic Data Analysis

```python
import pandas as pd

# Load ranking data
df = pd.read_csv('outputs/csv/THE_2026_rankings.csv')

# Top 10 universities in 2026
top_10 = df[df['year'] == 2026].nsmallest(10, 'rank')
print(top_10[['rank', 'name', 'overall']])

# Find Turkish universities
turkish_unis = df[df['name'].str.contains('Turkey|Turkish', case=False)]
print(turkish_unis[['year', 'rank', 'name', 'overall']])

# Trend analysis: Oxford over years
oxford = df[df['name'].str.contains('Oxford', case=False)]
print(oxford[['year', 'rank', 'overall']])
```

#### Visualization Example

```python
import matplotlib.pyplot as plt

# Visualize top 20 universities
top_20 = df[df['year'] == 2026].nsmallest(20, 'rank')

plt.figure(figsize=(12, 8))
plt.barh(top_20['name'], top_20['overall'])
plt.xlabel('Overall Score')
plt.title('Top 20 Universities - THE 2026')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
```

### 🔧 Advanced Usage: SQL Import

```bash
# Generate SQL script (if you have an optional script)
python db_insert_generator.py

# Import to SQLite
sqlite3 university_rankings.db < outputs/the_rankings_insert.sql

# Query example
sqlite3 university_rankings.db "SELECT name, overall FROM rankings WHERE year=2026 ORDER BY rank LIMIT 10;"
```

### ⚙️ Technical Details

#### Data Processing Pipeline
1. **Fetch**: Direct HTTP GET requests to THE API (annual and subject endpoints)
2. **Parse**: JSON response parsing with error handling
3. **Clean**: Remove null values, standardize rank formats
4. **Export**: Dual format (CSV + JSON) with year-based naming and category folders (general vs subject)

#### Interactive CLI
- Prompts whether to retrieve general rankings, subject rankings, or both
- Requests a year or year range (default 2011-2026)
- Offers optional filtering to a subset of subject slugs while preserving slug-based filenames

### ⚠️ Important Notes

- **Data Source**: Official THE JSON API endpoints
- **Rate Limiting**: Built-in delays to respect API limits
- **Execution Time**: Each year takes 30 seconds to 1 minute
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
| Import error | Ensure you're using Python 3.7+ |

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
![GitHub repo boyutu](https://img.shields.io/github/repo-size/c3nk/THE-World-University-Rankings)
![GitHub language count](https://img.shields.io/github/languages/count/c3nk/THE-World-University-Rankings)

### 🌟 Key Features

- **Official JSON API Integration**: Connects to THE’s published ranking endpoints without browser automation
- **Complete Dataset**: 16 years of data (2011-2026), ~44,000 total records
- **Dual Output Format**: Clean CSV files + Full JSON backups
- **Database Ready**: Optional SQL generation included
- **Two Data Types**: Rankings scores and Key statistics tables
- **Interactive CLI**: Guides you through pulling general or subject rankings for the desired year range

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

# The script prompts whether to pull general rankings, subject rankings, or both, and for the year range to process.

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
│   └── subject/
│       ├── THE_2026_arts-and-humanities_rankings.csv
│       ├── THE_2026_arts-and-humanities_key_statistics.csv
│       └── ... (subject + year combinations)
├── json/
│   ├── general/
│   │   ├── THE_2026_rankings.json
│   │   ├── THE_2026_key_statistics.json
│   │   └── ... (general rankings per year)
│   └── subject/
│       ├── THE_2026_arts-and-humanities_rankings.json
│       ├── THE_2026_arts-and-humanities_key_statistics.json
│       └── ... (subject + year combinations)
└── the_rankings_insert.sql           # (Optional) SQL script
```

### 🗄️ Database Schema

#### Rankings Table

| Column | Type | Description |
|--------|------|-------------|
| year | INT | Ranking year (2011-2026) |
| rank | INT | University rank (numeric) |
| rank_prefix | VARCHAR | Rank prefix (e.g., '=' for ties) |
| name | VARCHAR | University name |
| overall | FLOAT | Overall score (0-100) |
| teaching | FLOAT | Teaching score |
| research_environment | FLOAT | Research environment score |
| research_quality | FLOAT | Research quality score |
| industry | FLOAT | Industry income score |
| international_outlook | FLOAT | International outlook score |

#### Key Statistics Table

| Column | Type | Description |
|--------|------|-------------|
| year | INT | Year |
| rank | INT | Rank |
| rank_prefix | VARCHAR | Rank prefix |
| name | VARCHAR | University name |
| fte_students | INT | Full-time equivalent students |
| students_per_staff | FLOAT | Student-to-staff ratio |
| international_students | VARCHAR | % of international students |
| female_male_ratio | VARCHAR | Female to male ratio |

### 💡 Usage Examples

#### Basic Data Analysis

```python
import pandas as pd

# Load ranking data
df = pd.read_csv('outputs/csv/THE_2026_rankings.csv')

# Top 10 universities in 2026
top_10 = df[df['year'] == 2026].nsmallest(10, 'rank')
print(top_10[['rank', 'name', 'overall']])

# Find Turkish universities
turkish_unis = df[df['name'].str.contains('Turkey|Turkish', case=False)]
print(turkish_unis[['year', 'rank', 'name', 'overall']])

# Trend analysis: Oxford over years
oxford = df[df['name'].str.contains('Oxford', case=False)]
print(oxford[['year', 'rank', 'overall']])
```

#### Visualization Example

```python
import matplotlib.pyplot as plt

# Visualize top 20 universities
top_20 = df[df['year'] == 2026].nsmallest(20, 'rank')

plt.figure(figsize=(12, 8))
plt.barh(top_20['name'], top_20['overall'])
plt.xlabel('Overall Score')
plt.title('Top 20 Universities - THE 2026')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
```

### 🔧 Advanced Usage: SQL Import

```bash
# Generate SQL script (if you have an optional script)
python db_insert_generator.py

# Import to SQLite
sqlite3 university_rankings.db < outputs/the_rankings_insert.sql

# Query example
sqlite3 university_rankings.db "SELECT name, overall FROM rankings WHERE year=2026 ORDER BY rank LIMIT 10;"
```

### ⚙️ Technical Details

#### Data Processing Pipeline
1. **Fetch**: Direct HTTP GET requests to THE API (annual and subject endpoints)
2. **Parse**: JSON response parsing with error handling
3. **Clean**: Remove null values, standardize rank formats
4. **Export**: Dual format (CSV + JSON) with year-based naming and category folders (general vs subject)

#### Interactive CLI
- Prompts whether to pull general rankings, subject rankings, or both
- Asks for a year or year range (default 2011-2026)
- Allows optional filtering to a subset of subject slugs while keeping slug-based filenames

### ⚠️ Important Notes

- **Data Source**: Official THE JSON API endpoints
- **Rate Limiting**: Built-in delays to respect API limits
- **Execution Time**: Each year takes 30 seconds to 1 minute
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
| Import error | Ensure you're using Python 3.7+ |

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