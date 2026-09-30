import contextlib
import io
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import db_insert_generator as db
import the_university_rankings_full as scraper


class RegressionTests(unittest.TestCase):
    def test_zero_scores_and_missing_values(self):
        raw = {'data': [{'rank': '1', 'name': 'Example', 'scores_overall': 0,
                         'scores_teaching': None, 'stats_student_staff_ratio': 0}]}
        rows = [scraper.filter_data_for_db(raw, 2026, scraper.RANKINGS_FIELDS),
                scraper.filter_impact_overall_data(raw, 2026),
                scraper.filter_impact_sdg_data(raw, 2026, 'sdg4_rankings')]
        for result in rows:
            self.assertEqual(result['data'][0]['Overall'], '0')
            self.assertEqual(result['data'][0]['rank_prefix'], '')
        self.assertEqual(rows[0]['data'][0]['Teaching'], '')
        self.assertEqual(rows[1]['data'][0]['No. of students per staff'], '0')

    def test_impact_without_ties_and_empty_response(self):
        original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                with patch.object(scraper, 'fetch_json', return_value={
                    'data': [{'rank': '1', 'name': 'Example', 'scores_overall': 0}]
                }), patch.object(scraper, '_fetch_all_sdg_scores', return_value={}), \
                     patch.object(scraper, 'process_impact_sdg'), \
                     patch.object(scraper.time, 'sleep'):
                    scraper.process_impact_year(2026, ['sdg4_rankings'])
                result = pd.read_csv('outputs/THE_2026_impact_data.csv', keep_default_na=False)
                self.assertEqual(result.iloc[0]['rank_prefix'], '')
                self.assertEqual(result.iloc[0]['Overall'], 0)
                with patch.object(scraper, 'fetch_json', return_value={'data': []}), \
                     patch.object(scraper, 'process_impact_sdg') as process_sdg:
                    scraper.process_impact_year(2025, ['sdg4_rankings'])
                self.assertFalse(Path('outputs/THE_2025_impact_data.csv').exists())
                process_sdg.assert_called_once_with(2025, 'sdg4_rankings')
            finally:
                os.chdir(original)

    def test_sql_round_trip_and_source_precedence(self):
        with tempfile.TemporaryDirectory(prefix='rankings_test_') as tmp:
            root = Path(tmp)
            def write(name, row):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                pd.DataFrame([row]).to_csv(path, index=False)
            rankings = {'Name': "University O'Brien", 'Rank': '201–250', 'Overall': '0',
                        'Teaching': '', 'Research Environment': '', 'Research Quality': '',
                        'Industry': '', 'International Outlook': '', 'Country': 'NA'}
            statistics = {'Name': rankings['Name'], 'Rank': '201–250', 'Country': 'NA',
                          'No. of FTE students': '', 'No. of students per staff': '',
                          'International students': '', 'Female:Male ratio': ''}
            impact = {'Name': rankings['Name'], 'Rank': '201–250', 'Overall': '0',
                      'SDG17_Score': '', 'Location': 'NA', 'No. of FTE students': '',
                      'No. of students per staff': '', 'International students': '',
                      'Female:Male ratio': ''}
            write('THE_2026_rankings.csv', dict(rankings, Name='Old copy'))
            write('THE_2025_rankings.csv', rankings)
            write('general/THE_2026_rankings.csv', rankings)
            write('general/THE_2026_key_statistics.csv', statistics)
            write('subject/THE_2026_computer-science_rankings.csv', rankings)
            write('subject/THE_2026_computer-science_key_statistics.csv', statistics)
            write('impact/THE_2026_impact_overall.csv', impact)
            for number in (4, 13):
                write(f'impact/sdg/THE_2026_impact_sdg{number}_rankings.csv',
                      dict(impact, **{f'SDG{number}_Score': str(number),
                                      f'SDG{number}_Rank': '001'}))
            with contextlib.redirect_stdout(io.StringIO()):
                sql = '\n'.join(db.process_csv_files(root))
            with sqlite3.connect(':memory:') as conn:
                conn.executescript(sql)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM Rankings').fetchone()[0], 2)
                self.assertEqual(conn.execute('SELECT name, overall, country, rank FROM Rankings WHERE year=2026').fetchone(),
                                 (rankings['Name'], '0', 'NA', '201–250'))
                for table in ('Subject_Rankings', 'Subject_Key_Statistics'):
                    self.assertEqual(conn.execute(f'SELECT subject FROM {table}').fetchone()[0], 'computer-science')
                self.assertEqual(conn.execute('SELECT sdg_number, sdg_score, sdg_rank FROM Impact_SDG ORDER BY sdg_number').fetchall(),
                                 [(4, '4', '001'), (13, '13', '001')])

    def test_invalid_sdg_is_rejected(self):
        for number in (0, 18):
            with self.assertRaises(ValueError):
                db.generate_impact_sdg_insert(pd.DataFrame(), 2026, number)
        with self.assertRaises(ValueError):
            db.generate_impact_sdg_insert(pd.DataFrame({'SDG13_Score': ['4']}), 2026, 4)

    def test_missing_columns_and_blank_names_stop_generation(self):
        with self.assertRaises(ValueError):
            db.generate_rankings_insert(pd.DataFrame({'Name': ['Example']}), 2026)
        blank = {column: '' for column in db.RANKINGS_COLUMNS}
        with self.assertRaises(ValueError):
            db.generate_rankings_insert(pd.DataFrame([blank]), 2026)
        with tempfile.TemporaryDirectory() as tmp:
            pd.DataFrame([blank]).to_csv(Path(tmp) / 'THE_2026_rankings.csv', index=False)
            with self.assertRaises(ValueError) as caught:
                db.process_csv_files(tmp)
            self.assertIn('THE_2026_rankings.csv', str(caught.exception))
            self.assertIn('university name is required', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
