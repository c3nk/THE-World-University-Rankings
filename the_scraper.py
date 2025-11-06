#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THE World University Rankings Scraper - Network Monitoring Edition
Yaklaşım: AJAX isteklerini dinle ve API endpoint'lerinden direkt veri çek
"""
import sys
import time
import argparse
import traceback
import pathlib
import json
import re
import select
import threading
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
import requests


YEAR_LIMITS = {
    2024: 2671,
    2025: 2855,
    2026: 2191
}


def setup_driver_with_logging(headless: bool = True, timeout: int = 30) -> webdriver.Chrome:
    """Network logging aktif driver kurulumu"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Anti-bot
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # KRITIK: Performance logging'i aktif et
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
    
    from selenium.webdriver.chrome.service import Service
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    driver.set_page_load_timeout(timeout)
    
    # Anti-detection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    # Network interception'ı aktif et
    driver.execute_cdp_cmd('Network.enable', {})
    
    return driver


def extract_ajax_requests(driver: webdriver.Chrome, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Performance loglarından AJAX/XHR isteklerini çıkar
    """
    if verbose:
        print("\n[NETWORK] Analyzing network activity...")
    
    ajax_requests = []
    
    try:
        # Performance loglarını al
        logs = driver.get_log('performance')
        
        if verbose:
            print(f"[NETWORK] Found {len(logs)} performance log entries")
        
        for entry in logs:
            try:
                log_entry = json.loads(entry['message'])
                message = log_entry.get('message', {})
                method = message.get('method', '')
                
                # Network response'larını bul
                if method == 'Network.responseReceived':
                    params = message.get('params', {})
                    response = params.get('response', {})
                    request_id = params.get('requestId', '')
                    
                    url = response.get('url', '')
                    mime_type = response.get('mimeType', '')
                    status = response.get('status', 0)
                    
                    # Tracking/analytics URL'lerini filtrele (GENİŞLETİLMİŞ)
                    is_tracking = any(x in url.lower() for x in [
                        'facebook.com/tr', 'google-analytics', 'gtag', 
                        'doubleclick.net/ddm', 'doubleclick.net/activity',
                        'fls.doubleclick.net',  # Floodlight tracking
                        'googletagmanager', 'analytics.', '/pixel', '/track', '/beacon',
                        'cookiebot', 'hotjar', 'mixpanel', 'segment.io',
                        'linkedin.com/px', 'linkedin.com/collect',  # LinkedIn pixel
                        't.co/i/adsct',  # Twitter pixel
                        'safeframe.googlesyndication',  # SafeFrame container
                        'recaptcha',  # reCAPTCHA
                        'tagdeliver.com', 'criteo.com/sid',  # Ad tracking
                        'rudderstack.com', 'clue6load.com',  # Analytics
                        'ctnsnet.com', 'rubiconproject.com',  # Ad networks
                        'smartadserver.com',  # Ad server
                        'data:image/',  # Base64 images
                        'pubads_impl.js', 'activeview', 'window_focus',  # Google ad scripts
                        'abg_lite', 'reach_worklet',  # Ad scripts
                        '/dict/', 'currency-file',  # Dictionary/config files
                        'openx.net/esp'  # OpenX tracking
                    ])
                    
                    # JavaScript/CSS dosyalarını atla (data içermez)
                    is_static_asset = any(url.endswith(ext) for ext in ['.js', '.css', '.svg', '.png', '.jpg', '.gif'])
                    
                    # İlgili istekleri filtrele - tracking/static hariç
                    if status == 200 and not is_tracking and not is_static_asset and any(keyword in url.lower() for keyword in [
                        '/ranking', '/data', '.json', '/api/', '/ajax',
                        '/university', '/datatable', '/load',
                        'world-ranking'  # THE ranking endpoint'i
                    ]):
                        ajax_requests.append({
                            'url': url,
                            'mime_type': mime_type,
                            'request_id': request_id,
                            'status': status
                        })
                        
                        if verbose:
                            # URL'i kısalt (tracking spam'i önlemek için)
                            short_url = url[:120] + "..." if len(url) > 120 else url
                            print(f"[FOUND] {short_url}")
                            print(f"        Type: {mime_type}, Status: {status}")
            
            except json.JSONDecodeError:
                continue
            except Exception as e:
                if verbose:
                    print(f"[DEBUG] Log parsing error: {e}")
                continue
        
        if verbose:
            print(f"\n[NETWORK] Total interesting requests found: {len(ajax_requests)}")
        
    except Exception as e:
        print(f"[ERROR] Could not extract AJAX requests: {e}")
        if verbose:
            traceback.print_exc()
    
    return ajax_requests


def get_response_body(driver: webdriver.Chrome, request_id: str, verbose: bool = False) -> Optional[str]:
    """
    Request ID'ye göre response body'yi al
    """
    try:
        response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
        body = response_body.get('body', '')
        
        # Base64 encoded mı kontrol et
        if response_body.get('base64Encoded', False):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        return body
    except Exception as e:
        if verbose:
            print(f"[DEBUG] Could not get response body for {request_id}: {e}")
        return None


def parse_datatable_json(json_data: str, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    DataTables JSON formatından DataFrame oluştur
    DataTables genelde şu formatta döner:
    {
        "data": [...],
        "recordsTotal": N,
        "recordsFiltered": N
    }
    """
    try:
        data = json.loads(json_data)
        
        if verbose:
            print(f"[JSON] Keys in response: {list(data.keys())}")
        
        # DataTables format
        if 'data' in data and isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
            if verbose:
                print(f"[JSON] Parsed DataTables format: {len(df)} rows")
            return df
        
        # Direkt array format
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            if verbose:
                print(f"[JSON] Parsed array format: {len(df)} rows")
            return df
        
        # Diğer formatlar
        else:
            if verbose:
                print(f"[JSON] Unknown format, trying to extract data...")
            # İçerideki listeleri bul
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    df = pd.DataFrame(value)
                    if verbose:
                        print(f"[JSON] Found data under key '{key}': {len(df)} rows")
                    return df
    
    except json.JSONDecodeError as e:
        if verbose:
            print(f"[ERROR] JSON parse error: {e}")
    except Exception as e:
        if verbose:
            print(f"[ERROR] DataFrame creation error: {e}")
    
    return None


def is_doubleclick_data(url: str, body: str, verbose: bool = False) -> bool:
    """
    DoubleClick/AdSense response'unun ranking verisi içerip içermediğini kontrol et
    Tracking pixel'leri hariç tut
    """
    if not body:
        return False
    
    # Tracking/pixel URL'leri değil mi?
    is_tracking = any(x in url.lower() for x in ['/ddm', '/pixel', '/tr?', '/track', 'facebook.com/tr'])
    if is_tracking:
        return False
    
    # DoubleClick/AdSense ad delivery URL'i mi?
    is_ad_delivery = any(x in url.lower() for x in [
        'doubleclick.net/gampad', 
        'googlesyndication.com',
        'googleads.com',
        'pagead'
    ])
    
    if not is_ad_delivery:
        return False
    
    # Body çok küçükse (tracking pixel gibi) atla
    if len(body) < 500:
        return False
    
    # İçerikte üniversite/ranking verisi var mı?
    has_ranking_data = any(keyword in body.lower() for keyword in [
        'university', 'ranking', 'institution', 'score',
        'oxford', 'cambridge', 'harvard', 'stanford',  # Bilinen üniversiteler
        'rank', 'country', 'citation'
    ])
    
    if verbose and is_ad_delivery and has_ranking_data:
        print(f"[DOUBLECLICK] Found ranking data in ad service response!")
    
    return has_ranking_data


def extract_data_from_doubleclick(body: str, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    DoubleClick/AdSense response'undan ranking verisini çıkar
    """
    if verbose:
        print("[DOUBLECLICK] Attempting to extract ranking data from ad response...")
    
    try:
        # JSON olarak parse etmeyi dene
        if body.strip().startswith('{') or body.strip().startswith('['):
            df = parse_datatable_json(body, verbose)
            if df is not None:
                return df
        
        # JSONP formatı olabilir (callback(...))
        jsonp_match = re.search(r'[\w\.]+\s*\(\s*({.*})\s*\)', body, re.DOTALL)
        if jsonp_match:
            json_str = jsonp_match.group(1)
            df = parse_datatable_json(json_str, verbose)
            if df is not None:
                if verbose:
                    print("[DOUBLECLICK] Successfully parsed JSONP format")
                return df
        
        # Embedded JSON (script tag içinde olabilir)
        json_matches = re.findall(r'({[\s\S]*?})', body)
        for json_str in json_matches:
            try:
                df = parse_datatable_json(json_str, verbose)
                if df is not None and len(df) > 10:
                    if verbose:
                        print("[DOUBLECLICK] Found embedded JSON with data")
                    return df
            except:
                continue
    
    except Exception as e:
        if verbose:
            print(f"[DOUBLECLICK] Extraction failed: {e}")
    
    return None
    """
    DataTables JSON formatından DataFrame oluştur
    DataTables genelde şu formatta döner:
    {
        "data": [...],
        "recordsTotal": N,
        "recordsFiltered": N
    }
    """
    try:
        data = json.loads(json_data)
        
        if verbose:
            print(f"[JSON] Keys in response: {list(data.keys())}")
        
        # DataTables format
        if 'data' in data and isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
            if verbose:
                print(f"[JSON] Parsed DataTables format: {len(df)} rows")
            return df
        
        # Direkt array format
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            if verbose:
                print(f"[JSON] Parsed array format: {len(df)} rows")
            return df
        
        # Diğer formatlar
        else:
            if verbose:
                print(f"[JSON] Unknown format, trying to extract data...")
            # İçerideki listeleri bul
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    df = pd.DataFrame(value)
                    if verbose:
                        print(f"[JSON] Found data under key '{key}': {len(df)} rows")
                    return df
    
    except json.JSONDecodeError as e:
        if verbose:
            print(f"[ERROR] JSON parse error: {e}")
    except Exception as e:
        if verbose:
            print(f"[ERROR] DataFrame creation error: {e}")
    
    return None


def input_ready():
    """Non-blocking input check"""
    try:
        import msvcrt  # Windows
        return msvcrt.kbhit()
    except ImportError:
        try:
            # Unix/Linux/Mac
            i, o, e = select.select([sys.stdin], [], [], 0.1)
            return len(i) > 0
        except:
            return False


def interactive_scroll_mode(driver: webdriver.Chrome, year: int, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Interaktif scroll modu - kullanıcı scroll ederken sürekli veri topla
    """
    print("\n" + "="*80)
    print("🎯 İNTERAKTİF SCROLL MODU AKTİF!")
    print("="*80)
    print("📋 YAPILACAKLAR:")
    print("   1. Tarayıcı açıldı - üniversite listesini görün")
    print("   2. Yavaş yavaş aşağı scroll edin")
    print("   3. Yeni üniversiteler yüklenir")
    print("   4. Tüm istediğiniz veri yüklendiğinde ENTER'a basın")
    print("   5. Terminal'e geri dönün ve ENTER'a basın")
    print("="*80)

    collected_data = []
    last_row_count = 0
    start_time = time.time()

    try:
        while True:
            # DOM'dan mevcut veriyi çıkar
            current_data = extract_from_current_dom(driver, verbose)

            if current_data is not None:
                current_rows = len(current_data)

                if current_rows > last_row_count:
                    new_rows = current_rows - last_row_count
                    elapsed = time.time() - start_time
                    print(f"📊 {elapsed:.1f}s - Yeni veri tespit edildi: +{new_rows} üniversite (toplam: {current_rows})")
                else:
                    # Veri sayısı değişmedi
                    elapsed = time.time() - start_time
                    if int(elapsed) % 10 == 0 and int(elapsed) > 0:  # Her 10 saniyede bir
                        print(f"⏳ {elapsed:.1f}s - Veri sayısı değişmedi ({current_rows} üniversite)")
                last_row_count = current_rows
                collected_data = current_data

            # Kısa bekleme
            time.sleep(2)

            # ENTER tuşu kontrolü
            if input_ready():
                print("\n[STOP] Kullanıcı durdurma sinyali alındı!")
                break

    except KeyboardInterrupt:
        print("\n[STOP] Keyboard interrupt - durduruluyor...")

    if collected_data is not None and len(collected_data) > 0:
        print(f"\n[SUCCESS] Toplam {len(collected_data)} üniversite verisi toplandı!")
        return collected_data
    else:
        print("\n[WARNING] Veri toplanamadı")
        return None


def extract_from_current_dom(driver: webdriver.Chrome, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Mevcut DOM'dan üniversite verilerini çıkar
    """
    try:
        # HTML tablosundan veri çıkar
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = soup.select_one("table#datatable-1, table.dataTable, table")
        if not table:
            if verbose:
                print("        [DOM] Table bulunamadı")
            return None

        # Headers
        headers = []
        thead = table.find("thead")
        if thead:
            headers = [th.get_text(strip=True) for th in thead.select("th")]

        # Rows
        rows = []
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.select("tr"):
                cells = tr.select("td")
                if cells:
                    row = [td.get_text(" ", strip=True) for td in cells]
                    rows.append(row)

        if rows:
            df = pd.DataFrame(rows, columns=headers if headers else None)
            return df

    except Exception as e:
        if verbose:
            print(f"        [DOM] Extraction error: {e}")

    return None


def monitor_and_capture(driver: webdriver.Chrome, url: str, wait_time: int = 10, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Sayfayı yükle ve network aktivitesini kaydet
    """
    if verbose:
        print(f"\n[MONITOR] Loading page: {url}")
    
    # Logları temizle
    driver.get_log('performance')
    
    # Sayfayı yükle
    driver.get(url)
    
    # Sayfa yüklensin diye bekle
    if verbose:
        print(f"[MONITOR] Waiting {wait_time}s for page to load and AJAX to complete...")
    time.sleep(wait_time)
    
    # Sayfayı scroll et (lazy loading tetikleyebilir)
    if verbose:
        print("[MONITOR] Scrolling to trigger any lazy loading...")
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Dropdown'dan "All" seç (varsa)
    try:
        from selenium.webdriver.support.ui import Select
        dropdown = driver.find_element(By.NAME, "datatable-1_length")
        select = Select(dropdown)
        for option in select.options:
            if 'all' in option.text.lower():
                if verbose:
                    print("[MONITOR] Selecting 'All' from dropdown...")
                select.select_by_visible_text(option.text)
                time.sleep(5)
                break
    except Exception as e:
        if verbose:
            print(f"[MONITOR] No dropdown found or selection failed: {e}")
    
    # AJAX isteklerini çıkar
    ajax_requests = extract_ajax_requests(driver, verbose)
    
    return ajax_requests


def fetch_data_from_api(url: str, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Tespit edilen API endpoint'inden direkt veri çek
    """
    if verbose:
        print(f"\n[API] Fetching data from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            if verbose:
                print(f"[API] Response size: {len(response.text)} bytes")
            
            df = parse_datatable_json(response.text, verbose)
            
            if df is not None and len(df) > 0:
                if verbose:
                    print(f"[API] Success! Got {len(df)} rows")
                return df
        else:
            if verbose:
                print(f"[API] Failed with status {response.status_code}")
    
    except Exception as e:
        if verbose:
            print(f"[API] Request failed: {e}")
    
    return None


def inspect_page_sources(driver: webdriver.Chrome, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Sayfadaki tüm potansiyel veri kaynaklarını incele
    """
    if verbose:
        print("\n[INSPECT] Analyzing page for data sources...")
    
    try:
        # 1. Script tag'lerinde embedded JSON var mı?
        scripts = driver.find_elements(By.TAG_NAME, "script")
        if verbose:
            print(f"[INSPECT] Found {len(scripts)} script tags")
        
        for idx, script in enumerate(scripts):
            try:
                script_content = script.get_attribute('innerHTML')
                if not script_content or len(script_content) < 500:
                    continue
                
                # JSON data içeriyor mu?
                if any(keyword in script_content.lower() for keyword in ['university', 'ranking', 'rank', 'score']):
                    if verbose:
                        print(f"[INSPECT] Script #{idx} might contain ranking data")
                    
                    # Next.js __NEXT_DATA__ var mı?
                    if '__NEXT_DATA__' in script_content or 'window.__NEXT_DATA__' in script_content:
                        if verbose:
                            print(f"[NEXT_DATA] Found Next.js data in script #{idx}")
                        
                        # JSON'u çıkar
                        json_match = re.search(r'__NEXT_DATA__\s*=\s*({.+?})\s*(?:</script|;)', script_content, re.DOTALL)
                        if json_match:
                            try:
                                next_data = json.loads(json_match.group(1))
                                if verbose:
                                    print(f"[NEXT_DATA] Parsed Next.js data")
                                
                                # props.pageProps içinde veri ara
                                page_props = next_data.get('props', {}).get('pageProps', {})
                                
                                # Muhtemel data key'leri
                                for key in ['rankings', 'universities', 'data', 'results', 'institutions']:
                                    if key in page_props and isinstance(page_props[key], list):
                                        df = pd.DataFrame(page_props[key])
                                        if len(df) > 50:
                                            print(f"[NEXT_DATA SUCCESS] Found {len(df)} rows in pageProps.{key}")
                                            return df
                                
                                # Nested data ara
                                for key, value in page_props.items():
                                    if isinstance(value, dict):
                                        for subkey, subvalue in value.items():
                                            if isinstance(subvalue, list) and len(subvalue) > 50:
                                                df = pd.DataFrame(subvalue)
                                                print(f"[NEXT_DATA SUCCESS] Found {len(df)} rows in pageProps.{key}.{subkey}")
                                                return df
                            except json.JSONDecodeError:
                                if verbose:
                                    print(f"[NEXT_DATA] Failed to parse JSON")
                    
                    # Diğer embedded JSON'lar
                    else:
                        json_patterns = [
                            r'var\s+rankingData\s*=\s*({.+?});',
                            r'var\s+universities\s*=\s*(\[.+?\]);',
                            r'window\.rankingData\s*=\s*({.+?});',
                            r'DATA\s*=\s*({.+?});',
                        ]
                        
                        for pattern in json_patterns:
                            match = re.search(pattern, script_content, re.DOTALL)
                            if match:
                                try:
                                    data = json.loads(match.group(1))
                                    if isinstance(data, list):
                                        df = pd.DataFrame(data)
                                    elif isinstance(data, dict):
                                        for key, value in data.items():
                                            if isinstance(value, list) and len(value) > 50:
                                                df = pd.DataFrame(value)
                                                break
                                    
                                    if df is not None and len(df) > 50:
                                        print(f"[SCRIPT SUCCESS] Found {len(df)} rows in embedded script")
                                        return df
                                except:
                                    continue
                                    
            except Exception as e:
                if verbose:
                    print(f"[INSPECT] Script #{idx} error: {e}")
                continue
        
        # 2. HTML Table fallback
        if verbose:
            print("[INSPECT] Checking HTML tables...")
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        tables = soup.find_all("table")
        for table in tables:
            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
                if len(rows) > 50:
                    if verbose:
                        print(f"[TABLE] Found table with {len(rows)} rows")
                    
                    # Headers
                    headers = []
                    thead = table.find("thead")
                    if thead:
                        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
                    
                    # Data
                    data = []
                    for tr in rows:
                        cells = tr.find_all(["td", "th"])
                        if cells:
                            row = [cell.get_text(" ", strip=True) for cell in cells]
                            data.append(row)
                    
                    if data:
                        df = pd.DataFrame(data, columns=headers if headers else None)
                        print(f"[TABLE SUCCESS] Extracted {len(df)} rows from HTML table")
                        return df
    
    except Exception as e:
        if verbose:
            print(f"[INSPECT] Page inspection failed: {e}")
            traceback.print_exc()
    
    return None


def try_api_patterns(driver: webdriver.Chrome, year: int, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Bilinen API pattern'lerini dene
    """
    if verbose:
        print("\n[API_PATTERNS] Trying known API endpoints...")
    
    # THE'nin muhtemel API endpoint pattern'leri
    api_patterns = [
        f"https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_{year}_0__a4e9ad63b4b1c96ce07cc370bc9e1f54.json",
        f"https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_{year}.json",
        f"https://www.timeshighereducation.com/api/rankings/{year}/world",
        f"https://www.timeshighereducation.com/api/v1/rankings/{year}",
        f"https://www.timeshighereducation.com/_next/data/rankings/{year}.json",
    ]
    
    for api_url in api_patterns:
        if verbose:
            print(f"[API_PATTERNS] Trying: {api_url}")
        
        try:
            response = requests.get(api_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json'
            })
            
            if response.status_code == 200:
                df = parse_datatable_json(response.text, verbose)
                if df is not None and len(df) > 50:
                    print(f"[API_PATTERNS SUCCESS] Found {len(df)} rows at: {api_url}")
                    return df
        except Exception as e:
            if verbose:
                print(f"[API_PATTERNS] Failed: {e}")
    
    return None


def scrape_with_network_monitoring(driver: webdriver.Chrome, year: int, verbose: bool = False) -> Tuple[Optional[pd.DataFrame], List[str]]:
    """
    Network monitoring ile veri çek
    Returns: (DataFrame, list of API endpoints found)
    """
    url = f"https://www.timeshighereducation.com/world-university-rankings/{year}/world-ranking"
    
    print(f"\n{'='*60}")
    print(f"[SCRAPING] Year {year}")
    print(f"{'='*60}")
    
    # 1. Sayfayı izle ve AJAX isteklerini yakala
    ajax_requests = monitor_and_capture(driver, url, wait_time=10, verbose=verbose)
    
    if not ajax_requests:
        print("[WARNING] No AJAX requests found!")
        return None, []
    
    # 2. Yakalanan isteklerden response body'leri al
    all_dataframes = []
    api_endpoints = []
    doubleclick_found = False
    
    for idx, req in enumerate(ajax_requests):
        if verbose:
            print(f"\n[REQUEST {idx+1}/{len(ajax_requests)}] Processing: {req['url'][:100]}...")
        
        request_id = req.get('request_id')
        url_endpoint = req['url']
        
        # Response body'yi al
        body = get_response_body(driver, request_id, verbose)
        
        if body:
            # Çok küçük response'ları atla (tracking/pixel)
            if len(body) < 100:
                if verbose:
                    print(f"        [SKIP] Too small ({len(body)} bytes)")
                continue
            
            # JavaScript bundle'ları kontrol et (içinde embedded data olabilir)
            if 'javascript' in req.get('mime_type', '').lower() or url_endpoint.endswith('.js'):
                if verbose:
                    print(f"        [CHECK] Checking JS bundle for embedded data...")
                
                # JS içinde JSON data var mı?
                if 'university' in body.lower() and 'rank' in body.lower():
                    if verbose:
                        print(f"        [JS] Found potential ranking data in JS bundle!")
                    # JSON extraction dene
                    json_matches = re.findall(r'(\[{.*?}\])', body, re.DOTALL)
                    for match in json_matches[:5]:  # İlk 5 match'i dene
                        try:
                            df = parse_datatable_json(match, verbose)
                            if df is not None and len(df) > 50:
                                print(f"[JS SUCCESS] Extracted {len(df)} rows from JS bundle!")
                                all_dataframes.append(df)
                                api_endpoints.append(f"[JS_BUNDLE] {url_endpoint}")
                                break
                        except:
                            continue
                continue
            
            # DoubleClick kontrolü
            if is_doubleclick_data(url_endpoint, body, verbose):
                doubleclick_found = True
                df = extract_data_from_doubleclick(body, verbose)
                
                if df is not None and len(df) > 10:
                    print(f"[DOUBLECLICK SUCCESS] Extracted {len(df)} rows from ad service!")
                    all_dataframes.append(df)
                    api_endpoints.append(f"[DOUBLECLICK] {url_endpoint}")
                    continue
            
            # Normal JSON parse
            df = parse_datatable_json(body, verbose)
            
            if df is not None and len(df) > 10:  # En az 10 satır olmalı
                print(f"[SUCCESS] Found data in request #{idx+1}: {len(df)} rows")
                all_dataframes.append(df)
                api_endpoints.append(url_endpoint)
    
    # 3. En büyük DataFrame'i seç
    if all_dataframes:
        best_df = max(all_dataframes, key=len)
        source = "[DOUBLECLICK]" if doubleclick_found else "[AJAX]"
        print(f"\n[RESULT] Best dataset from {source}: {len(best_df)} rows")
        
        # Eğer veri yetersizse (< %50), diğer yöntemleri dene
        expected_rows = YEAR_LIMITS.get(year, 1000)
        if len(best_df) < expected_rows * 0.5:
            print(f"[WARNING] Data insufficient ({len(best_df)} < {expected_rows*0.5}), trying alternative methods...")
            
            # Yöntem 1: Sayfa kaynaklarını incele
            page_df = inspect_page_sources(driver, verbose)
            if page_df is not None and len(page_df) > len(best_df):
                print(f"[PAGE_SOURCE SUCCESS] Found better data: {len(page_df)} rows")
                best_df = page_df
            
            # Yöntem 2: API pattern'lerini dene
            if len(best_df) < expected_rows * 0.5:
                api_df = try_api_patterns(driver, year, verbose)
                if api_df is not None and len(api_df) > len(best_df):
                    print(f"[API_PATTERN SUCCESS] Found better data: {len(api_df)} rows")
                    best_df = api_df
        
        return best_df, api_endpoints
    
    # Veri bulunamadıysa, alternatif yöntemleri dene
    print(f"[WARNING] No data from AJAX, trying alternative methods...")
    
    # Sayfa kaynaklarını incele
    page_df = inspect_page_sources(driver, verbose)
    if page_df is not None and len(page_df) > 50:
        return page_df, []
    
    # API pattern'lerini dene
    api_df = try_api_patterns(driver, year, verbose)
    if api_df is not None and len(api_df) > 50:
        return api_df, []
    
    return None, api_endpoints


def fallback_html_scraping(driver: webdriver.Chrome, verbose: bool = False) -> Optional[pd.DataFrame]:
    """
    Network monitoring başarısız olursa HTML'den çek
    """
    if verbose:
        print("\n[FALLBACK] Trying HTML table extraction...")
    
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        table = soup.select_one("table#datatable-1, table.dataTable, table")
        
        if table:
            # Headers
            headers = []
            thead = table.find("thead")
            if thead:
                headers = [th.get_text(strip=True) for th in thead.select("th")]
            
            # Rows
            rows = []
            tbody = table.find("tbody")
            if tbody:
                for tr in tbody.select("tr"):
                    cells = tr.select("td")
                    if cells:
                        row = [td.get_text(" ", strip=True) for td in cells]
                        rows.append(row)
            
            if rows:
                df = pd.DataFrame(rows, columns=headers if headers else None)
                if verbose:
                    print(f"[FALLBACK] Extracted {len(df)} rows from HTML")
                return df
    
    except Exception as e:
        if verbose:
            print(f"[FALLBACK] HTML extraction failed: {e}")
    
    return None


def save_api_endpoints(endpoints: List[str], output_dir: pathlib.Path, year: int):
    """API endpoint'lerini kaydet (gelecek kullanım için)"""
    if endpoints:
        endpoint_file = output_dir / f"api_endpoints_{year}.txt"
        with open(endpoint_file, 'w') as f:
            for ep in endpoints:
                f.write(ep + '\n')
        print(f"[SAVED] API endpoints to: {endpoint_file}")


def scrape_year(driver: webdriver.Chrome, year: int, limit: Optional[int], verbose: bool = False, interactive_scroll: bool = False) -> Tuple[pd.DataFrame, List[str]]:
    """
    Ana scraping fonksiyonu
    """
    # Interaktif scroll modu aktif mi?
    if interactive_scroll:
        print(f"\n[INTERACTIVE] Starting interactive scroll mode for year {year}")
        url = f"https://www.timeshighereducation.com/world-university-rankings/{year}/world-ranking"
        driver.get(url)
        time.sleep(5)  # Sayfa yüklenmesi için bekle

        df = interactive_scroll_mode(driver, year, verbose)
        api_endpoints = ["[INTERACTIVE_SCROLL]"]

        if df is None:
            print("[WARNING] Interactive scroll failed, trying network monitoring...")
            df, api_endpoints = scrape_with_network_monitoring(driver, year, verbose)

    else:
        # Normal network monitoring
        df, api_endpoints = scrape_with_network_monitoring(driver, year, verbose)

    # Başarısız olursa fallback
    if df is None or len(df) < 50:
        print("[WARNING] Network monitoring didn't get enough data, trying fallback...")
        df = fallback_html_scraping(driver, verbose)
    
    # Hala veri yoksa hata
    if df is None or len(df) == 0:
        raise Exception(f"Could not extract data for year {year}")
    
    # DataFrame'i düzenle
    if limit and len(df) > limit:
        df = df.iloc[:limit].copy()
    
    # Year kolonu ekle
    if 'Year' not in df.columns:
        df.insert(0, 'Year', year)
    
    print(f"\n[FINAL] Year {year}: {len(df)} rows extracted")
    
    return df, api_endpoints


def main():
    parser = argparse.ArgumentParser(description="THE Rankings Scraper - Network Monitoring Edition")
    parser.add_argument("--years", nargs="+", type=int, default=[2026], help="Years to scrape")
    parser.add_argument("--limit", type=int, default=None, help="Max rows per table (None = all)")
    parser.add_argument("--outdir", type=str, default="output", help="Output directory")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--no-headless", action="store_true", help="Disable headless mode (for debugging)")
    parser.add_argument("--wait-time", type=int, default=10, help="Wait time for AJAX requests (seconds)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--save-endpoints", action="store_true", help="Save discovered API endpoints")
    parser.add_argument("--interactive-scroll", action="store_true", help="Enable interactive scroll mode for user-controlled data collection")

    args = parser.parse_args()

    # Interactive scroll için headless'i otomatik kapat
    headless = (args.headless and not args.no_headless) and not args.interactive_scroll

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("THE World University Rankings Scraper")
    print("Network Monitoring Edition (with DoubleClick support)")
    print(f"{'='*60}")
    print(f"Years: {args.years}")
    print(f"Limit: {args.limit if args.limit else 'All'}")
    print(f"Headless: {headless}")
    print(f"Wait time: {args.wait_time}s")
    print(f"Verbose: {args.verbose}")
    print(f"Interactive Scroll: {args.interactive_scroll}")
    print(f"{'='*60}\n")

    driver = setup_driver_with_logging(headless=headless)

    overall_counts = []
    all_endpoints = {}
    
    try:
        for year in args.years:
            try:
                df, endpoints = scrape_year(driver, year, args.limit, args.verbose, args.interactive_scroll)

                # CSV'ye kaydet
                csv_path = outdir / f"THE_Rankings_{year}.csv"
                df.to_csv(csv_path, index=False, encoding="utf-8")
                print(f"✓ Saved: {csv_path} ({len(df)} rows)")
                
                overall_counts.append((year, len(df)))
                all_endpoints[year] = endpoints
                
                # API endpoint'lerini kaydet
                if args.save_endpoints and endpoints:
                    save_api_endpoints(endpoints, outdir, year)
                
            except Exception as e:
                print(f"✗ Year {year} FAILED: {e}")
                if args.verbose:
                    traceback.print_exc()

    finally:
        driver.quit()

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for y, rc in overall_counts:
        expected = YEAR_LIMITS.get(y, "?")
        status = "✓" if rc >= expected * 0.9 else "⚠"  # 90%+ başarılı kabul
        print(f"{status} {y}: {rc:4d} rows (expected: {expected})")
    print(f"{'='*60}")
    
    # API endpoint'leri özeti
    if any(all_endpoints.values()):
        print("\nDISCOVERED API ENDPOINTS:")
        for year, endpoints in all_endpoints.items():
            if endpoints:
                print(f"\n{year}:")
                for ep in endpoints[:3]:  # İlk 3'ünü göster
                    print(f"  - {ep[:100]}...")
    
    print()


if __name__ == "__main__":
    main()