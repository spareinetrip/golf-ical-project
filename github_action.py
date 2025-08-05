#!/usr/bin/env python3
"""
Golf iCal Feed Generator for GitHub Actions
==========================================

Dit script automatiseert het ophalen van golfreservaties van i-Golf.be
en genereert een iCal bestand dat wordt opgeslagen in de repository.

Gebruikt door GitHub Actions om dagelijks de golfreservaties bij te werken.
"""

import os
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from ics import Calendar, Event

# Configuraties
I_GOLF_URL = "https://www.i-golf.be"
USERNAME = os.environ.get('I_GOLF_USERNAME', '714410')
PASSWORD = os.environ.get('I_GOLF_PASSWORD', 'Julien')

class IGolfScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup headless Chrome driver for GitHub Actions"""
        print("=== CHROME DRIVER SETUP START ===")
        
        # Debug environment
        print(f"Environment variables:")
        print(f"  CHROME_BIN: {os.environ.get('CHROME_BIN', 'Not set')}")
        print(f"  CHROMEDRIVER_PATH: {os.environ.get('CHROMEDRIVER_PATH', 'Not set')}")
        print(f"  PATH: {os.environ.get('PATH', 'Not set')}")
        
        # Check Chrome binary
        chrome_bin = os.environ.get('CHROME_BIN')
        if chrome_bin:
            print(f"Chrome binary path: {chrome_bin}")
            print(f"Chrome binary exists: {os.path.exists(chrome_bin)}")
            if os.path.exists(chrome_bin):
                try:
                    import subprocess
                    result = subprocess.run([chrome_bin, '--version'], capture_output=True, text=True)
                    print(f"Chrome version: {result.stdout.strip()}")
                except Exception as e:
                    print(f"Error getting Chrome version: {e}")
        
        # Check ChromeDriver
        chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
        if not chromedriver_path:
            # Try to find ChromeDriver in PATH
            import subprocess
            try:
                result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
                chromedriver_path = result.stdout.strip()
            except:
                chromedriver_path = '/usr/local/bin/chromedriver'
        
        print(f"ChromeDriver path: {chromedriver_path}")
        print(f"ChromeDriver exists: {os.path.exists(chromedriver_path) if chromedriver_path else False}")
        
        if chromedriver_path and os.path.exists(chromedriver_path):
            try:
                import subprocess
                result = subprocess.run([chromedriver_path, '--version'], capture_output=True, text=True)
                print(f"ChromeDriver version: {result.stdout.strip()}")
            except Exception as e:
                print(f"Error getting ChromeDriver version: {e}")
        else:
            print("ChromeDriver not found, will try to use system ChromeDriver")
            chromedriver_path = 'chromedriver'  # Use PATH
        
        # Setup Chrome options
        print("Setting up Chrome options...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # GitHub Actions specific options for stability
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        # options.add_argument('--disable-javascript')  # We need JS for the website
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # Remove problematic options
        # options.add_argument('--remote-debugging-port=9222')  # Can cause connection issues
        # options.add_argument('--single-process')  # Can cause stability issues
        
        # Use Chrome binary if specified
        if chrome_bin and os.path.exists(chrome_bin):
            print(f"🔄 Using specified Chrome binary: {chrome_bin}")
            options.binary_location = chrome_bin
        
        print("Chrome options configured:")
        for arg in options.arguments:
            print(f"  {arg}")
        
        try:
            print("🔄 Initializing Chrome driver...")
            
            # Use Service only if we have a specific path
            if chromedriver_path and chromedriver_path != 'chromedriver':
                service = Service(chromedriver_path)
                print(f"Service created with path: {chromedriver_path}")
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Use default ChromeDriver from PATH
                print("Using ChromeDriver from PATH")
                self.driver = webdriver.Chrome(options=options)
            
            print("✅ Chrome driver geïnitialiseerd")
            
            # Test the driver
            print("Testing driver...")
            self.driver.get("https://www.google.com")
            print(f"Page title: {self.driver.title}")
            print("✅ Driver test successful")
            
        except Exception as e:
            print(f"❌ Fout bij Chrome driver setup: {e}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            raise
            
        except Exception as e:
            print(f"❌ Fout bij Chrome driver setup: {e}")
            raise
    
    def login(self):
        """Log in op i-Golf.be"""
        try:
            print("🔐 Bezig met inloggen op i-Golf.be...")
            
            # Navigate to the page
            self.driver.get(I_GOLF_URL)
            print(f"📍 Navigated to: {self.driver.current_url}")
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if we're already logged in
            current_url = self.driver.current_url
            if "LOGIN" not in current_url.upper():
                print("✅ Already logged in")
                return True
            
            # Look for login fields with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"🔍 Login attempt {attempt + 1}/{max_retries}")
                    
                    # Wait for login fields
                    username_field = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.NAME, "P101_USERNAME"))
                    )
                    password_field = self.driver.find_element(By.NAME, "P101_PASSWORD")
                    
                    print("✅ Login fields found")
                    
                    # Clear and fill credentials
                    username_field.clear()
                    username_field.send_keys(USERNAME)
                    password_field.clear()
                    password_field.send_keys(PASSWORD)
                    
                    # Submit
                    password_field.send_keys(Keys.RETURN)
                    
                    print("✅ Credentials submitted, waiting...")
                    time.sleep(6)
                    
                    # Check if login was successful
                    current_url = self.driver.current_url
                    print(f"📍 URL after login: {current_url}")
                    
                    if "LOGIN" not in current_url.upper():
                        print("✅ Login successful")
                        return True
                    else:
                        print(f"⚠️  Still on login page, attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            self.driver.refresh()
                            time.sleep(3)
                        
                except Exception as e:
                    print(f"⚠️  Login attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        self.driver.refresh()
                        time.sleep(3)
            
            print("❌ All login attempts failed")
            return False
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def navigate_to_reservations(self):
        """Navigeer naar reservaties pagina via menu"""
        try:
            print("🧭 Navigeren naar reservaties...")
            
            # Check huidige URL
            print(f"📍 Huidige URL: {self.driver.current_url}")
            
            # Wait for page to fully load
            time.sleep(5)
            
            # Try to find the JULIEN button with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"🔍 Looking for JULIEN button, attempt {attempt + 1}/{max_retries}")
                    
                    # Wait for JULIEN button
                    julien_btn = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'js-menuButton') and contains(., 'JULIEN')]"))
                    )
                    print("✅ JULIEN button found")
                    
                    # Click JULIEN button to open menu
                    print("🖱️  Clicking JULIEN button...")
                    julien_btn.click()
                    time.sleep(3)  # Wait for menu to open
                    
                    # Look for "Uw reservaties" link
                    print("🔍 Looking for 'Uw reservaties' link...")
                    reservations_link = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Uw reservaties')]"))
                    )
                    print("✅ 'Uw reservaties' link found")
                    
                    # Click on "Uw reservaties"
                    print("🖱️  Clicking 'Uw reservaties'...")
                    reservations_link.click()
                    
                    # Wait for page load
                    time.sleep(6)
                    
                    # Check new URL
                    current_url = self.driver.current_url
                    print(f"📍 New URL: {current_url}")
                    
                    if "LOGIN" not in current_url.upper():
                        print("✅ Successfully navigated to reservations page")
                        return True
                    else:
                        print(f"⚠️  Still on login page, attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            self.driver.refresh()
                            time.sleep(3)
                        
                except Exception as e:
                    print(f"⚠️  Navigation attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        self.driver.refresh()
                        time.sleep(3)
            
            print("❌ All navigation attempts failed")
            return False
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def scrape_reservations(self):
        """Scrape alle reservaties van de pagina"""
        try:
            print("📊 Bezig met scrapen van reservaties...")
            
            # Get page source en parse met BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Debug: Print pagina titel
            print(f"📄 Pagina titel: {self.driver.title}")
            
            # Debug: Check for regions
            wedstrijden_region = soup.find('div', id='WEDSTRIJDEN')
            tee_region = soup.find('div', id='TEE')
            itee_co_region = soup.find('div', id='ITEE_CO')
            
            print(f"🔍 WEDSTRIJDEN region gevonden: {wedstrijden_region is not None}")
            print(f"🔍 TEE region gevonden: {tee_region is not None}")
            print(f"🔍 ITEE_CO region gevonden: {itee_co_region is not None}")
            
            # Debug: Check for any t-Card-title elements
            all_cards = soup.find_all('h3', class_='t-Card-title')
            print(f"🔍 Totaal aantal t-Card-title elementen: {len(all_cards)}")
            
            for i, card in enumerate(all_cards[:5]):  # Show first 5
                title = card.get_text(strip=True)
                print(f"  {i+1}. {title}")
            
            all_events = []
            
            # A. Scrape wedstrijden
            wedstrijden_events = self.scrape_wedstrijden(soup)
            all_events.extend(wedstrijden_events)
            print(f"📋 {len(wedstrijden_events)} wedstrijden gevonden")
            
            # B. Scrape tee-reservaties
            tee_events = self.scrape_tee_reservations(soup)
            all_events.extend(tee_events)
            print(f"⛳ {len(tee_events)} tee-reservaties gevonden")
            
            # C. Scrape medespeler reservaties
            medespeler_events = self.scrape_medespeler_reservations(soup)
            all_events.extend(medespeler_events)
            print(f"👥 {len(medespeler_events)} medespeler reservaties gevonden")
            
            print(f"✅ Totaal {len(all_events)} reservaties gescraped")
            return all_events
            
        except Exception as e:
            print(f"❌ Scraping gefaald: {e}")
            return []
    
    def scrape_wedstrijden(self, soup):
        """Scrape wedstrijden uit WEDSTRIJDEN div"""
        events = []
        
        # Zoek naar de WEDSTRIJDEN region
        wedstrijden_region = soup.find('div', id='WEDSTRIJDEN')
        if not wedstrijden_region:
            print("⚠️  WEDSTRIJDEN region niet gevonden")
            return events
        
        # Zoek naar alle t-Card-title elementen binnen WEDSTRIJDEN
        cards = wedstrijden_region.find_all('h3', class_='t-Card-title')
        print(f"🔍 WEDSTRIJDEN: {len(cards)} cards gevonden")
        
        for i, card in enumerate(cards):
            try:
                title = card.get_text(strip=True)
                print(f"🔍 WEDSTRIJDEN card {i+1}: {title}")
                
                # Skip als het een tee-reservatie is (heeft datum/tijd format in titel)
                if re.search(r'\d{2}/\d{2}/\d{4}\s*\(\d{1,2}:\d{2}-\d{1,2}:\d{2}\)', title):
                    print(f"  ⏭️  Skip (tee-reservatie format)")
                    continue
                
                # Zoek beschrijving direct in de WEDSTRIJDEN region
                desc_elem = wedstrijden_region.find('div', class_='t-Card-desc')
                if not desc_elem:
                    print(f"  ❌ t-Card-desc niet gevonden in WEDSTRIJDEN region")
                    continue
                
                desc_text = desc_elem.get_text()
                print(f"  📝 Beschrijving: {desc_text[:100]}...")
                
                # Zoek datum
                datum_match = re.search(r'Datum:\s*(\d{2}/\d{2}/\d{4})', desc_text)
                if not datum_match:
                    print(f"  ❌ Datum niet gevonden in beschrijving")
                    continue
                datum_str = datum_match.group(1)
                print(f"  📅 Datum gevonden: {datum_str}")
                
                # Zoek voorkeur start tijd
                voorkeur_match = re.search(r'Voorkeur start:\s*(\d{1,2}:\d{2})', desc_text)
                if voorkeur_match:
                    start_tijd_str = voorkeur_match.group(1)
                    print(f"  ⏰ Voorkeur start tijd: {start_tijd_str}")
                    # Parse tijd en trek 30 minuten af
                    start_tijd = datetime.strptime(start_tijd_str, '%H:%M').time()
                    start_datetime = datetime.combine(
                        datetime.strptime(datum_str, '%d/%m/%Y').date(),
                        start_tijd
                    ) - timedelta(minutes=30)
                else:
                    print(f"  ⏰ Geen voorkeur start tijd, gebruik standaard 10:00")
                    # Gebruik standaard 10:00
                    start_datetime = datetime.combine(
                        datetime.strptime(datum_str, '%d/%m/%Y').date(),
                        datetime.strptime('10:00', '%H:%M').time()
                    )
                
                # Locatie uit beschrijving (eerste regel) - proper golf club name
                lines = [line.strip() for line in desc_text.split('\n') if line.strip()]
                location_raw = lines[0] if lines else "Onbekende locatie"
                
                # Clean up location name (remove extra text, proper case)
                location_parts = location_raw.split()
                if len(location_parts) >= 3 and location_parts[0] == "ROYAL" and location_parts[1] == "LATEM":
                    location = "Royal Latem Golf Club"
                else:
                    # General cleanup - title case
                    location = location_raw.title()
                
                print(f"  🏌️  Locatie: {location}")
                
                # Zoek voorkeur start en tee info voor notes
                voorkeur_start = "Voorkeur start: -"
                tee_info = ""
                
                # Parse voorkeur start
                voorkeur_match = re.search(r'Voorkeur start:\s*([^\n]*)', desc_text)
                if voorkeur_match:
                    voorkeur_value = voorkeur_match.group(1).strip()
                    if voorkeur_value and voorkeur_value != "-":
                        voorkeur_start = f"Voorkeur start: {voorkeur_value}"
                    else:
                        voorkeur_start = "Voorkeur start: -"
                
                # Parse tee info
                tee_match = re.search(r'Tee:\s*(\d+)', desc_text)
                if tee_match:
                    tee_number = tee_match.group(1)
                    tee_info = f"Tee: {tee_number}"
                
                # Maak notes
                notes_parts = [voorkeur_start]
                if tee_info:
                    notes_parts.append(tee_info)
                notes = '\n'.join(notes_parts)
                
                # Maak event met proper formatting
                event = {
                    'title': f"Competition ⛳️ {title}",
                    'location': location,
                    'start': start_datetime,
                    'duration': timedelta(hours=4),
                    'notes': notes
                }
                events.append(event)
                print(f"  ✅ Wedstrijd toegevoegd: {title} op {datum_str}")
                
            except Exception as e:
                print(f"⚠️  Fout bij wedstrijd parsing: {e}")
                continue
        
        return events
    
    def scrape_tee_reservations(self, soup):
        """Scrape tee-reservaties uit TEE div"""
        events = []
        
        # Zoek naar de TEE region
        tee_region = soup.find('div', id='TEE')
        if not tee_region:
            print("⚠️  TEE region niet gevonden")
            return events
        
        # Zoek naar alle t-Card-title elementen binnen TEE
        cards = tee_region.find_all('h3', class_='t-Card-title')
        print(f"🔍 TEE: {len(cards)} cards gevonden")
        
        for i, card in enumerate(cards):
            try:
                title_text = card.get_text(strip=True)
                print(f"🔍 TEE card {i+1}: {title_text}")
                
                # Parse datum en tijd: "05/08/2025 (17:00-17:00)"
                datetime_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*\((\d{1,2}:\d{2})-(\d{1,2}:\d{2})\)', title_text)
                if not datetime_match:
                    print(f"  ❌ Datum/tijd format niet herkend")
                    continue
                
                datum_str = datetime_match.group(1)
                start_tijd_str = datetime_match.group(2)
                print(f"  📅 Datum: {datum_str}, Tijd: {start_tijd_str}")
                
                # Zoek beschrijving direct in de TEE region
                desc_elem = tee_region.find('div', class_='t-Card-desc')
                if not desc_elem:
                    print(f"  ❌ t-Card-desc niet gevonden in TEE region")
                    continue
                if desc_elem:
                    desc_text = desc_elem.get_text()
                    print(f"  📝 Beschrijving: {desc_text[:100]}...")
                    lines = [line.strip() for line in desc_text.split('\n') if line.strip()]
                    location_raw = lines[0] if lines else "Onbekende golfclub"
                    
                    # Clean up location name (proper case)
                    location_parts = location_raw.split()
                    if len(location_parts) >= 3 and location_parts[0] == "ROYAL" and location_parts[1] == "LATEM":
                        location = "Royal Latem Golf Club"
                    else:
                        # General cleanup - title case
                        location = location_raw.title()
                    
                    notes = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                else:
                    location = "Onbekende golfclub"
                    notes = ""
                
                print(f"  🏌️  Locatie: {location}")
                
                # Parse datetime en trek 30 minuten af
                start_tijd = datetime.strptime(start_tijd_str, '%H:%M').time()
                start_datetime = datetime.combine(
                    datetime.strptime(datum_str, '%d/%m/%Y').date(),
                    start_tijd
                ) - timedelta(minutes=30)
                
                # Maak event met proper formatting
                event = {
                    'title': f'Tee-time ⛳️ {location}',
                    'location': location,
                    'start': start_datetime,
                    'duration': timedelta(hours=4),
                    'notes': notes
                }
                events.append(event)
                print(f"  ✅ Tee-reservatie toegevoegd: {title_text} @ {location}")
                
            except Exception as e:
                print(f"⚠️  Fout bij tee-reservatie parsing: {e}")
                continue
        
        return events
    
    def scrape_medespeler_reservations(self, soup):
        """Scrape medespeler reservaties uit ITEE_CO div"""
        events = []
        
        # Zoek naar de ITEE_CO region
        itee_co_region = soup.find('div', id='ITEE_CO')
        if not itee_co_region:
            print("⚠️  ITEE_CO region niet gevonden")
            return events
        
        # Zoek naar alle t-Card-title elementen binnen ITEE_CO
        cards = itee_co_region.find_all('h3', class_='t-Card-title')
        print(f"🔍 ITEE_CO: {len(cards)} cards gevonden")
        
        for i, card in enumerate(cards):
            try:
                title_text = card.get_text(strip=True)
                print(f"🔍 ITEE_CO card {i+1}: {title_text}")
                
                # Parse datum en tijd: "05/08/2025 (17:00-17:00)"
                datetime_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*\((\d{1,2}:\d{2})-(\d{1,2}:\d{2})\)', title_text)
                if not datetime_match:
                    print(f"  ❌ Datum/tijd format niet herkend")
                    continue
                
                datum_str = datetime_match.group(1)
                start_tijd_str = datetime_match.group(2)
                print(f"  📅 Datum: {datum_str}, Tijd: {start_tijd_str}")
                
                # Zoek beschrijving direct in de ITEE_CO region
                desc_elem = itee_co_region.find('div', class_='t-Card-desc')
                if not desc_elem:
                    print(f"  ❌ t-Card-desc niet gevonden in ITEE_CO region")
                    continue
                if desc_elem:
                    desc_text = desc_elem.get_text()
                    print(f"  📝 Beschrijving: {desc_text[:100]}...")
                    lines = [line.strip() for line in desc_text.split('\n') if line.strip()]
                    location_raw = lines[0] if lines else "Onbekende golfclub"
                    
                    # Clean up location name (proper case)
                    location_parts = location_raw.split()
                    if len(location_parts) >= 3 and location_parts[0] == "ROYAL" and location_parts[1] == "LATEM":
                        location = "Royal Latem Golf Club"
                    else:
                        # General cleanup - title case
                        location = location_raw.title()
                    
                    # Zoek verantwoordelijke en medespelers info
                    notes_parts = []
                    for line in lines:
                        if 'Verantwoordelijke:' in line:
                            notes_parts.append(line)
                        elif 'Medespelers:' in line:
                            notes_parts.append(line)
                    notes = '\n'.join(notes_parts)
                else:
                    location = "Onbekende golfclub"
                    notes = ""
                
                print(f"  🏌️  Locatie: {location}")
                
                # Parse datetime en trek 30 minuten af
                start_tijd = datetime.strptime(start_tijd_str, '%H:%M').time()
                start_datetime = datetime.combine(
                    datetime.strptime(datum_str, '%d/%m/%Y').date(),
                    start_tijd
                ) - timedelta(minutes=30)
                
                # Maak event met proper formatting
                event = {
                    'title': f'Tee-time ⛳️ {location}',
                    'location': location,
                    'start': start_datetime,
                    'duration': timedelta(hours=4),
                    'notes': notes
                }
                events.append(event)
                print(f"  ✅ Medespeler reservatie toegevoegd: {title_text} @ {location}")
                
            except Exception as e:
                print(f"⚠️  Fout bij medespeler reservatie parsing: {e}")
                continue
        
        return events
    
    def close(self):
        """Sluit de browser driver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser gesloten")


def create_ical_calendar(events):
    """Maak iCal calendar van events"""
    calendar = Calendar()
    
    for event_data in events:
        event = Event()
        event.name = event_data['title']
        event.location = event_data['location']
        event.begin = event_data['start']
        event.duration = event_data['duration']
        event.description = event_data.get('notes', '')
        
        calendar.events.add(event)
    
    return calendar


def main():
    """Hoofdfunctie voor GitHub Actions"""
    print("=== GOLF ICAL GENERATOR START ===")
    print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Debug system info
    print("=== SYSTEM INFO ===")
    import platform
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Debug environment
    print("=== ENVIRONMENT DEBUG ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    scraper = None
    try:
        print("=== INITIALIZING SCRAPER ===")
        # Initialiseer scraper
        scraper = IGolfScraper()
        print("✅ Scraper initialized")
        
        print("=== LOGGING IN ===")
        # Login
        if not scraper.login():
            raise Exception("Login gefaald")
        print("✅ Login successful")
        
        print("=== NAVIGATING TO RESERVATIONS ===")
        # Navigeer naar reservaties
        if not scraper.navigate_to_reservations():
            raise Exception("Navigatie naar reservaties gefaald")
        print("✅ Navigation successful")
        
        print("=== SCRAPING RESERVATIONS ===")
        # Scrape reservaties
        events = scraper.scrape_reservations()
        print(f"✅ Scraped {len(events)} events")
        
        print("=== CREATING ICAL ===")
        # Maak iCal calendar
        calendar = create_ical_calendar(events)
        print("✅ Calendar created")
        
        # Save to file
        output_file = 'golf.ics'
        print(f"=== SAVING TO {output_file} ===")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(calendar))
        
        print(f"✅ iCal bestand gegenereerd: {output_file}")
        print(f"📊 Aantal events: {len(events)}")
        
        # Print event details for debugging
        print("=== EVENT DETAILS ===")
        for i, event_data in enumerate(events[:5]):  # Show first 5
            print(f"  {i+1}. {event_data['title']} - {event_data['start'].strftime('%Y-%m-%d %H:%M')}")
        
        if len(events) > 5:
            print(f"  ... en {len(events) - 5} meer events")
        
        print("=== SUCCESS ===")
        return True
        
    except Exception as e:
        print("=== ERROR OCCURRED ===")
        print(f"❌ Fout bij genereren iCal: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Create empty calendar file
        print("=== CREATING EMPTY CALENDAR ===")
        empty_calendar = Calendar()
        with open('golf.ics', 'w', encoding='utf-8') as f:
            f.write(str(empty_calendar))
        print("⚠️  Leeg iCal bestand gegenereerd")
        return False
        
    finally:
        print("=== CLEANUP ===")
        if scraper:
            scraper.close()
            print("✅ Scraper closed")


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1) 