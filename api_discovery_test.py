#!/usr/bin/env python3
"""
THE World University Rankings API Discovery Tool
Advanced API endpoint detection and testing for bypassing scraping limitations

This tool attempts to find THE's internal APIs that serve university ranking data
directly, which would allow us to bypass the 35-university limit.
"""

import requests
import json
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import sys

class THEAPIDiscovery:
    """Advanced API discovery tool for THE World University Rankings"""

    def __init__(self):
        self.base_url = "https://www.timeshighereducation.com"
        self.session = requests.Session()

        # Realistic browser headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })

        self.discovered_endpoints = []
        self.working_apis = []

    def test_endpoint(self, url: str, method: str = 'GET', **kwargs) -> Tuple[bool, Any]:
        """Test a single endpoint and return success status and data"""
        try:
            print(f"🔍 Testing: {method} {url}")

            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, timeout=10, **kwargs)
            else:
                return False, None

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()

                if 'json' in content_type:
                    try:
                        data = response.json()
                        data_str = json.dumps(data, indent=2)[:500]
                        print(f"   ✅ JSON Response ({len(data_str)} chars)")
                        print(f"   📊 Preview: {data_str[:200]}...")

                        # Check for ranking-related data
                        if self._is_ranking_data(data):
                            print(f"   🎯 RANKING DATA DETECTED!")
                            return True, data

                        return True, data

                    except json.JSONDecodeError:
                        print(f"   ⚠️  Valid response but not JSON")
                        return False, response.text[:200]

                elif 'html' in content_type:
                    print(f"   📄 HTML Response")
                    return False, None
                else:
                    print(f"   ❓ Other content type: {content_type}")
                    return False, response.text[:200]
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return False, None

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return False, None

    def _is_ranking_data(self, data: Any) -> bool:
        """Check if the data contains university ranking information"""
        if not isinstance(data, (dict, list)):
            return False

        data_str = json.dumps(data).lower()

        # Keywords that indicate ranking data
        ranking_keywords = [
            'university', 'college', 'rank', 'ranking', 'score',
            'country', 'teaching', 'research', 'citations',
            'industry income', 'international outlook'
        ]

        matches = sum(1 for keyword in ranking_keywords if keyword in data_str)
        return matches >= 3  # At least 3 matching keywords

    def discover_rest_apis(self) -> List[Tuple[str, Any]]:
        """Test common REST API patterns"""
        print("\n" + "="*60)
        print("🔍 PHASE 1: Testing REST API Endpoints")
        print("="*60)

        # Common API patterns based on typical university ranking sites
        api_patterns = [
            # Direct rankings
            "/api/rankings/world-university-rankings/{year}",
            "/api/world-university-rankings/{year}",
            "/api/rankings/{year}",
            "/api/rankings/world-university-rankings",
            "/api/world-university-rankings",

            # Data endpoints
            "/api/data/rankings/{year}",
            "/api/data/world-university-rankings/{year}",
            "/api/v1/rankings/{year}",
            "/api/v2/rankings/{year}",

            # Alternative structures
            "/api/universities/rankings/{year}",
            "/api/institutions/rankings/{year}",
            "/api/ranking-data/{year}",

            # Legacy endpoints
            "/services/rankings/{year}",
            "/data/rankings/{year}",
        ]

        working_apis = []

        for pattern in api_patterns:
            for year in [2024, 2023]:  # Test recent years
                endpoint = pattern.format(year=year)
                full_url = urljoin(self.base_url, endpoint)

                success, data = self.test_endpoint(full_url)
                if success and self._is_ranking_data(data):
                    working_apis.append((full_url, data))

                time.sleep(0.5)  # Be respectful

        return working_apis

    def discover_graphql_apis(self) -> List[Tuple[str, Any]]:
        """Test GraphQL endpoints with ranking queries"""
        print("\n" + "="*60)
        print("🔍 PHASE 2: Testing GraphQL Endpoints")
        print("="*60)

        graphql_endpoints = [
            "/api/graphql",
            "/graphql",
            "/api/v1/graphql",
            "/api/graph",
        ]

        # Common GraphQL queries for university rankings
        queries = [
            """
            query GetRankings($year: Int!) {
                rankings(year: $year) {
                    edges {
                        node {
                            rank
                            name
                            country
                            scores {
                                overall
                                teaching
                                research
                                citations
                                industryIncome
                                internationalOutlook
                            }
                        }
                    }
                }
            }
            """,
            """
            query GetUniversities($year: Int!) {
                universities(year: $year) {
                    rank
                    name
                    country
                    overallScore
                }
            }
            """,
            """
            query RankingsQuery {
                worldUniversityRankings {
                    universities {
                        rank
                        name
                        scores
                    }
                }
            }
            """
        ]

        working_apis = []

        for endpoint in graphql_endpoints:
            full_url = urljoin(self.base_url, endpoint)

            for query in queries:
                payload = {
                    "query": query.strip(),
                    "variables": {"year": 2024}
                }

                headers = self.session.headers.copy()
                headers['Content-Type'] = 'application/json'

                success, data = self.test_endpoint(
                    full_url,
                    method='POST',
                    json=payload,
                    headers=headers
                )

                if success and self._is_ranking_data(data):
                    working_apis.append((full_url, data))

                time.sleep(0.5)

        return working_apis

    def analyze_page_source(self) -> List[str]:
        """Analyze the main page source for API endpoint hints"""
        print("\n" + "="*60)
        print("🔍 PHASE 3: Analyzing Page Source for API Hints")
        print("="*60)

        try:
            response = self.session.get(
                f"{self.base_url}/world-university-rankings/2024/world-ranking",
                timeout=15
            )

            if response.status_code != 200:
                print("❌ Could not load main page")
                return []

            page_content = response.text

            # Look for API endpoints in JavaScript
            api_patterns = [
                r'["\']([^"\']*api[^"\']*)["\']',
                r'["\']([^"\']*graphql[^"\']*)["\']',
                r'["\']([^"\']*rankings[^"\']*data[^"\']*)["\']',
                r'fetch\(["\']([^"\']*)["\']',
                r'axios\.\w+\(["\']([^"\']*)["\']',
            ]

            potential_endpoints = []

            for pattern in api_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    if 'api' in match.lower() or 'graphql' in match.lower():
                        full_url = urljoin(self.base_url, match)
                        if full_url not in potential_endpoints:
                            potential_endpoints.append(full_url)

            print(f"📋 Found {len(potential_endpoints)} potential API endpoints in page source")

            # Test the most promising ones
            tested_endpoints = []
            for endpoint in potential_endpoints[:10]:  # Test first 10
                if any(keyword in endpoint.lower() for keyword in ['ranking', 'university', 'api']):
                    success, data = self.test_endpoint(endpoint)
                    if success:
                        tested_endpoints.append(endpoint)
                        if self._is_ranking_data(data):
                            return [endpoint]  # Return immediately if we find ranking data

                time.sleep(0.3)

            return tested_endpoints

        except Exception as e:
            print(f"❌ Page source analysis failed: {e}")
            return []

    def run_full_discovery(self) -> Dict[str, Any]:
        """Run complete API discovery process"""
        print("🚀 THE World University Rankings API Discovery Tool")
        print("🔍 Searching for APIs that bypass the 35-university limit...")
        print("="*80)

        results = {
            'rest_apis': [],
            'graphql_apis': [],
            'page_source_apis': [],
            'summary': {}
        }

        # Phase 1: REST APIs
        results['rest_apis'] = self.discover_rest_apis()

        # Phase 2: GraphQL APIs
        results['graphql_apis'] = self.discover_graphql_apis()

        # Phase 3: Page Source Analysis
        results['page_source_apis'] = self.analyze_page_source()

        # Summary
        all_working_apis = results['rest_apis'] + results['graphql_apis'] + [(url, None) for url in results['page_source_apis']]

        results['summary'] = {
            'total_endpoints_tested': len(all_working_apis),
            'working_apis_found': len([api for api in all_working_apis if api[1] is not None]),
            'ranking_data_found': any(self._is_ranking_data(api[1]) for api in all_working_apis if api[1] is not None)
        }

        return results

    def print_results(self, results: Dict[str, Any]):
        """Print discovery results in a nice format"""
        print("\n" + "="*80)
        print("📊 DISCOVERY RESULTS")
        print("="*80)

        summary = results['summary']
        print(f"🔢 Total endpoints tested: {summary['total_endpoints_tested']}")
        print(f"✅ Working APIs found: {summary['working_apis_found']}")
        print(f"🎯 Ranking data found: {'YES' if summary['ranking_data_found'] else 'NO'}")

        if results['rest_apis']:
            print(f"\n📡 REST APIs ({len(results['rest_apis'])}):")
            for url, data in results['rest_apis']:
                print(f"   ✅ {url}")
                if data and isinstance(data, (list, dict)):
                    if isinstance(data, list):
                        print(f"      📊 Contains {len(data)} items")
                    else:
                        print(f"      📊 Keys: {list(data.keys())[:5]}...")

        if results['graphql_apis']:
            print(f"\n🔗 GraphQL APIs ({len(results['graphql_apis'])}):")
            for url, data in results['graphql_apis']:
                print(f"   ✅ {url}")

        if results['page_source_apis']:
            print(f"\n📄 Page Source APIs ({len(results['page_source_apis'])}):")
            for url in results['page_source_apis']:
                print(f"   ✅ {url}")

        if summary['ranking_data_found']:
            print(f"\n🎉 SUCCESS! Ranking APIs found. You can now bypass the 35-university limit!")
            print(f"💡 Use these APIs in your scraper for complete data access.")
        else:
            print(f"\n❌ No ranking APIs found. The site may not expose public APIs.")
            print(f"💡 Try manual DevTools inspection while scrolling on the site.")

def main():
    """Main function"""
    try:
        discovery = THEAPIDiscovery()
        results = discovery.run_full_discovery()
        discovery.print_results(results)

        print(f"\n💡 Next Steps:")
        print(f"   1. If APIs found, integrate them into your scraper")
        print(f"   2. Test with different years and parameters")
        print(f"   3. Check rate limits and authentication requirements")
        print(f"   4. Consider using Selenium for JavaScript-heavy endpoints")

    except KeyboardInterrupt:
        print(f"\n⚠️  Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Discovery failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
