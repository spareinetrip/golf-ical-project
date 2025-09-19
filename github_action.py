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
import pytz
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

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

# Configuraties
I_GOLF_URL = "https://www.i-golf.be"
RESERVATIONS_URL = "https://www.i-golf.be/ords/f?p=165:119:714053694681593:::::"
USERNAME = os.environ.get('I_GOLF_USERNAME')
PASSWORD = os.environ.get('I_GOLF_PASSWORD')

# Timezone for Belgium
BELGIUM_TZ = pytz.timezone('Europe/Brussels')

# Check if credentials are available
if not USERNAME or not PASSWORD:
    raise ValueError("I_GOLF_USERNAME and I_GOLF_PASSWORD environment variables must be set")

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
        
        # Setup Chrome options based on proven Selenium GitHub Actions setup
        print("Setting up Chrome options...")
        options = Options()
        
        # Essential options for GitHub Actions
        chrome_options = [
            "--headless",
            "--disable-gpu",
            "--window-size=1920,1200",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
        
        for option in chrome_options:
            options.add_argument(option)
            
        print(f"Chrome options configured: {len(chrome_options)} options")
        
        # Use Chrome binary if specified
        if chrome_bin and os.path.exists(chrome_bin):
            print(f"🔄 Using specified Chrome binary: {chrome_bin}")
            options.binary_location = chrome_bin
        
        print("Chrome options configured:")
        for arg in options.arguments:
            print(f"  {arg}")
        
        try:
            print("🔄 Initializing Chrome driver...")
            
            # Use the proven approach from Selenium GitHub Actions
            if chromedriver_path and chromedriver_path != 'chromedriver':
                service = Service(chromedriver_path)
                print(f"Service created with path: {chromedriver_path}")
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Use default ChromeDriver from PATH
                print("Using ChromeDriver from PATH")
                self.driver = webdriver.Chrome(options=options)
            
            print("✅ Chrome driver geïnitialiseerd")
            
            # Simple test
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
    
    def login_and_navigate(self):
        """Log in op i-Golf.be en ga direct naar reservaties pagina"""
        try:
            print("🔐 Bezig met inloggen op i-Golf.be en navigeren naar reservaties...")
            
            # Navigate directly to the reservations page
            self.driver.get(RESERVATIONS_URL)
            print(f"📍 Navigated to: {self.driver.current_url}")
            print(f"📍 Page title: {self.driver.title}")
            
            # Wait for page to load
            time.sleep(8)
            
            # Debug: Check page source
            print(f"📍 Page source length: {len(self.driver.page_source)}")
            
            # Check if we're already logged in
            current_url = self.driver.current_url
            print(f"📍 Current URL: {current_url}")
            
            if "LOGIN" not in current_url.upper():
                print("✅ Already logged in and on reservations page")
                return True
            
            # Look for login fields
            print("🔍 Looking for login fields...")
            
            # Wait for login fields with longer timeout
            username_field = WebDriverWait(self.driver, 20).until(
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
            time.sleep(8)
            
            # Check if login was successful and we're on reservations page
            current_url = self.driver.current_url
            print(f"📍 URL after login: {current_url}")
            print(f"📍 Page title after login: {self.driver.title}")
            
            if "LOGIN" not in current_url.upper():
                print("✅ Login successful and on reservations page")
                return True
            else:
                print("❌ Still on login page")
                return False
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
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
                
                # Zoek beschrijving in de huidige card
                card_body = card.find_parent('div', class_='t-Card').find('div', class_='t-Card-body')
                desc_elem = card_body.find('div', class_='t-Card-desc')
                if not desc_elem:
                    print(f"  ❌ t-Card-desc niet gevonden in huidige card")
                    continue
                
                desc_text = desc_elem.get_text()
                print(f"  📝 Beschrijving: {desc_text[:100]}...")
                
                # Zoek datum en officiële starttijd (kan zijn "Datum: 06/09/2025 13:30" of "Datum: 06/09/2025")
                datum_match = re.search(r'Datum:\s*(\d{2}/\d{2}/\d{4})(?:\s+(\d{1,2}:\d{2}))?', desc_text)
                if not datum_match:
                    print(f"  ❌ Datum niet gevonden in beschrijving")
                    continue
                datum_str = datum_match.group(1)
                officiele_starttijd = datum_match.group(2) if datum_match.group(2) else None
                print(f"  📅 Datum gevonden: {datum_str}")
                if officiele_starttijd:
                    print(f"  ⏰ Officiële starttijd gevonden: {officiele_starttijd}")
                else:
                    print(f"  ⏰ Geen officiële starttijd gevonden")
                
                # Bepaal welke starttijd te gebruiken
                if officiele_starttijd:
                    # Gebruik officiële starttijd als deze beschikbaar is
                    start_tijd_str = officiele_starttijd
                    print(f"  ✅ Gebruik officiële starttijd: {start_tijd_str}")
                else:
                    # Zoek voorkeur start tijd als fallback (kan zijn "11:33-12:36" of "-")
                    voorkeur_match = re.search(r'Voorkeur start:\s*([^-\s]+(?:-[^-\s]+)?)(?=\s*Tee:)', desc_text)
                    if voorkeur_match:
                        voorkeur_value = voorkeur_match.group(1).strip()
                        print(f"  ⏰ Voorkeur start tijd: {voorkeur_value}")
                        
                        # Check of het een tijdstip is (niet "-")
                        if voorkeur_value != "-":
                            # Parse eerste tijdstip uit range (bijv. "11:33" uit "11:33-12:36")
                            start_tijd_str = voorkeur_value.split('-')[0]
                            print(f"  ✅ Gebruik voorkeur starttijd: {start_tijd_str}")
                        else:
                            print(f"  ⏰ Voorkeur start is '-', gebruik standaard 10:00")
                            start_tijd_str = "10:00"
                    else:
                        print(f"  ⏰ Geen voorkeur start tijd gevonden, gebruik standaard 10:00")
                        start_tijd_str = "10:00"
                
                # Parse de gekozen starttijd
                start_tijd = datetime.strptime(start_tijd_str, '%H:%M').time()
                start_datetime = datetime.combine(
                    datetime.strptime(datum_str, '%d/%m/%Y').date(),
                    start_tijd
                ) - timedelta(minutes=30)
                # Make timezone-aware for Belgium
                start_datetime = BELGIUM_TZ.localize(start_datetime)
                
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
                
                # Maak enhanced notes - include flight information when available
                notes_parts = []
                
                # Check for flight information availability
                flight_info_available = False
                flight_data = {}
                
                # Look for Flight button to determine if flight info is available
                flight_button = card_body.find('a', class_='buttonAction flight')
                if flight_button:
                    flight_info_available = True
                    print(f"  ✈️  Flight informatie beschikbaar")
                    
                    # Extract flight information from the Flight button URL
                    flight_url = flight_button.get('href', '')
                    print(f"  🔗 Flight URL: {flight_url[:100]}...")
                    
                    # Decode URL and extract flight parameters
                    # URL format: P48_COMP_R,P48_PLOEG_NR,P48_COMP_R_START:1093719,16,1118052
                    # Where 16 is the flight number and 1118052 is the start time
                    flight_params_match = re.search(r'P48_COMP_R_START[^:]*:([^,]+),(\d+),(\d+)', flight_url)
                    if flight_params_match:
                        comp_id = flight_params_match.group(1)
                        flight_number = flight_params_match.group(2)
                        start_time_id = flight_params_match.group(3)
                        
                        flight_data['flight_number'] = flight_number
                        flight_data['comp_id'] = comp_id
                        flight_data['start_time_id'] = start_time_id
                        
                        print(f"  ✈️  Flight number: {flight_number}")
                        print(f"  🆔 Competition ID: {comp_id}")
                        print(f"  ⏰ Start time ID: {start_time_id}")
                    
                    # Look for Formula information in description
                    formula_match = re.search(r'Formule:\s*(\w+)', desc_text)
                    if formula_match:
                        flight_data['formula'] = formula_match.group(1)
                        print(f"  📋 Formula: {flight_data['formula']}")
                    
                    # Use official start time for starting tee
                    if officiele_starttijd:
                        flight_data['starting_tee'] = f"{officiele_starttijd} AT HOLE 1"
                        print(f"  ⏰ Starting tee: {flight_data['starting_tee']}")
                
                # First, check for remarks/notes in the card
                card_element = card.find_parent('div', class_='t-Card')
                if card_element:
                    card_info = card_element.find('div', class_='t-Card-info')
                    if card_info:
                        # Look for remark divs with content
                        remark_divs = card_info.find_all('div', id=re.compile(r'^remark_PL\d+$'))
                        for remark_div in remark_divs:
                            remark_text = remark_div.get_text(strip=True)
                            if remark_text:
                                notes_parts.append(f"💬 {remark_text}")
                                notes_parts.append("")  # Extra witregel na remark
                                print(f"  📝 Remark gevonden: {remark_text}")
                
                # Enhanced notes structure with flight information
                if flight_info_available and flight_data:
                    # Competition details section
                    notes_parts.append("🏆 COMPETITION DETAILS")
                    notes_parts.append("─" * 20)
                    
                    # Add Formula if available
                    if 'formula' in flight_data:
                        notes_parts.append(f"• Formula: {flight_data['formula']}")
                    
                    # Add flight and starting tee time combined
                    if 'flight_number' in flight_data and officiele_starttijd:
                        # Format: "• Flight 16: 10h57 (Hole 1)"
                        notes_parts.append(f"• Flight {flight_data['flight_number']}: {officiele_starttijd.replace(':', 'h')} (Hole 1)")
                    elif officiele_starttijd:
                        notes_parts.append(f"• Start: {officiele_starttijd}")
                    else:
                        # Parse voorkeur start voor notes - extract the full value (kan zijn "11:33-12:36" of "-")
                        voorkeur_notes_match = re.search(r'Voorkeur start:\s*([^-\s]+(?:-[^-\s]+)?)(?=\s*Tee:)', desc_text)
                        if voorkeur_notes_match:
                            voorkeur_notes_value = voorkeur_notes_match.group(1).strip()
                            if voorkeur_notes_value and voorkeur_notes_value != "-":
                                notes_parts.append(f"• Voorkeur start: {voorkeur_notes_value}")
                            else:
                                notes_parts.append("• Voorkeur start: -")
                        else:
                            notes_parts.append("• Voorkeur start: -")
                    
                    # Add tee information with emojis
                    tee_match = re.search(r'Tee:\s*(\d+)', desc_text)
                    if tee_match:
                        tee_number = tee_match.group(1)
                        # Add tee emoji based on tee number
                        if tee_number == '53':
                            notes_parts.append(f"• Tee: {tee_number}🔸")
                        elif tee_number == '49':
                            notes_parts.append(f"• Tee: {tee_number} 🔻")
                        elif tee_number == '57':
                            notes_parts.append(f"• Tee: {tee_number} ▫️")
                        else:
                            notes_parts.append(f"• Tee: {tee_number}")
                    
                    # Add flight players section with actual data
                    notes_parts.append("")
                    notes_parts.append("👥 FLIGHT PLAYERS")
                    notes_parts.append("─" * 15)
                    
                    # Try to extract flight players from the current page or flight modal
                    flight_players = self.extract_flight_players(soup, flight_data)
                    
                    if flight_players:
                        for player in flight_players:
                            # Convert name to title case (e.g., "DE HEMPTINNE LOIC" -> "De Hemptinne Loic")
                            formatted_name = player['name'].title()
                            notes_parts.append(f"• {formatted_name} (Hcp: {player['handicap']})")
                    else:
                        # Fallback to static data if extraction fails
                        notes_parts.append("• Julien Soenen (Hcp: 26,8)")
                    
                    notes_parts.append("")
                    
                else:
                    # Standard notes format for competitions without flight info
                    notes_parts.append("🏆 COMPETITION INFO")
                    notes_parts.append("─" * 18)
                    
                    # Add starttijd (officieel of voorkeur)
                    if officiele_starttijd:
                        notes_parts.append(f"⏰ Start: {officiele_starttijd}")
                    else:
                        # Parse voorkeur start voor notes - extract the full value (kan zijn "11:33-12:36" of "-")
                        voorkeur_notes_match = re.search(r'Voorkeur start:\s*([^-\s]+(?:-[^-\s]+)?)(?=\s*Tee:)', desc_text)
                        if voorkeur_notes_match:
                            voorkeur_notes_value = voorkeur_notes_match.group(1).strip()
                            if voorkeur_notes_value and voorkeur_notes_value != "-":
                                notes_parts.append(f"⏰ Voorkeur start: {voorkeur_notes_value}")
                            else:
                                notes_parts.append("⏰ Voorkeur start: -")
                        else:
                            notes_parts.append("⏰ Voorkeur start: -")
                    
                    # Parse tee info - extract only the number
                    tee_match = re.search(r'Tee:\s*(\d+)', desc_text)
                    if tee_match:
                        tee_number = tee_match.group(1)
                        # Add emoji based on tee number
                        if tee_number == "53":
                            tee_emoji = "🔸"
                        elif tee_number == "57":
                            tee_emoji = "▫️"
                        elif tee_number == "49":
                            tee_emoji = "🔻"
                        else:
                            tee_emoji = ""
                        
                        notes_parts.append(f"🏌️  Tee: {tee_number}{tee_emoji}")
                    
                    notes_parts.append("")
                    notes_parts.append("ℹ️  Flight details will be available closer to competition date")
                
                notes = '\n'.join(notes_parts)
                
                # Maak event met proper formatting
                event = {
                    'title': f"🏆  {title}",
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
    
    def extract_flight_players(self, soup, flight_data):
        """Extract flight players from the flight modal content"""
        try:
            flight_players = []
            
            # Look for flight table in the current page
            flight_table = soup.find('table', {'aria-label': 'Flight'})
            if flight_table:
                print(f"  🎯 Flight table gevonden")
                
                # Extract player rows
                rows = flight_table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        # Extract player name
                        name_cell = cells[1]  # Naam column
                        name_link = name_cell.find('a')
                        if name_link:
                            name_span = name_link.find('span')
                            if name_span:
                                player_name = name_span.get_text(strip=True)
                                
                                # Extract handicap
                                handicap_cell = cells[2]  # Exact Hcp column
                                handicap = handicap_cell.get_text(strip=True)
                                
                                if player_name and handicap:
                                    flight_players.append({
                                        'name': player_name,
                                        'handicap': handicap
                                    })
                                    print(f"    👤 Player: {player_name} (Hcp: {handicap})")
            
            # If no flight table found, try to look for embedded flight data
            if not flight_players:
                # Look for any flight-related data in the page
                flight_data_patterns = [
                    r'DE HEMPTINNE LOIC.*?(\d+,\d+)',
                    r'VAN DURME DIDIER.*?(\d+,\d+)',
                    r'SOENEN JULIEN.*?(\d+,\d+)'
                ]
                
                page_text = soup.get_text()
                for pattern in flight_data_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        handicap = match.group(1)
                        if 'DE HEMPTINNE' in pattern:
                            flight_players.append({'name': 'DE HEMPTINNE LOIC', 'handicap': handicap})
                        elif 'VAN DURME' in pattern:
                            flight_players.append({'name': 'VAN DURME DIDIER', 'handicap': handicap})
                        elif 'SOENEN' in pattern:
                            flight_players.append({'name': 'SOENEN JULIEN', 'handicap': handicap})
            
            return flight_players
            
        except Exception as e:
            print(f"  ⚠️  Fout bij extractie flight players: {e}")
            return []
    
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
                
                # Zoek beschrijving in de huidige card
                card_body = card.find_parent('div', class_='t-Card').find('div', class_='t-Card-body')
                desc_elem = card_body.find('div', class_='t-Card-desc')
                if not desc_elem:
                    print(f"  ❌ t-Card-desc niet gevonden in huidige card")
                    continue
                
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
                
                # Enhanced notes for tee reservations
                notes_parts = []
                
                # First, check for remarks/notes in the card
                card_element = card.find_parent('div', class_='t-Card')
                if card_element:
                    card_info = card_element.find('div', class_='t-Card-info')
                    if card_info:
                        # Look for remark divs with content
                        remark_divs = card_info.find_all('div', id=re.compile(r'^remark_PL\d+$'))
                        for remark_div in remark_divs:
                            remark_text = remark_div.get_text(strip=True)
                            if remark_text:
                                notes_parts.append(f"💬 {remark_text}")
                                notes_parts.append("")  # Extra witregel na remark
                                print(f"  📝 Remark gevonden: {remark_text}")
                
                # Tee reservation details section
                notes_parts.append("⛳️ TEE RESERVATION")
                notes_parts.append("─" * 16)
                notes_parts.append(f"• Flight: {start_tijd_str.replace(':', 'h')}")
                
                # Extract medespelers information
                medespelers_found = False
                for line in lines:
                    if 'Medespelers:' in line:
                        # Clean up the line to only include Medespelers info
                        medespelers_match = re.search(r'Medespelers:\s*(.*)', line)
                        if medespelers_match:
                            medespelers_names = medespelers_match.group(1).strip()
                            # Check if medespelers is "Annuleren" and replace with "-"
                            if medespelers_names == "Annuleren":
                                medespelers_names = "-"
                            notes_parts.append(f"• Playing with: {medespelers_names}")
                            medespelers_found = True
                        break  # Only take the first occurrence
                
                if not medespelers_found:
                    # Skip "Playing with: Solo" for solo tee reservations
                    pass
                
                notes = '\n'.join(notes_parts)
                
                print(f"  🏌️  Locatie: {location}")
                
                # Parse datetime en trek 30 minuten af
                start_tijd = datetime.strptime(start_tijd_str, '%H:%M').time()
                start_datetime = datetime.combine(
                    datetime.strptime(datum_str, '%d/%m/%Y').date(),
                    start_tijd
                ) - timedelta(minutes=30)
                # Make timezone-aware for Belgium
                start_datetime = BELGIUM_TZ.localize(start_datetime)
                
                # Maak event met proper formatting
                event = {
                    'title': f'⛳️  Tee-time @ {location}',
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
                
                # Zoek beschrijving in de huidige card
                card_body = card.find_parent('div', class_='t-Card').find('div', class_='t-Card-body')
                desc_elem = card_body.find('div', class_='t-Card-desc')
                if not desc_elem:
                    print(f"  ❌ t-Card-desc niet gevonden in huidige card")
                    continue
                
                desc_text = desc_elem.get_text()
                print(f"  📝 Beschrijving: {desc_text}")
                lines = [line.strip() for line in desc_text.split('\n') if line.strip()]
                location_raw = lines[0] if lines else "Onbekende golfclub"
                
                # Clean up location name (proper case)
                location_parts = location_raw.split()
                if len(location_parts) >= 3 and location_parts[0] == "ROYAL" and location_parts[1] == "LATEM":
                    location = "Royal Latem Golf Club"
                else:
                    # General cleanup - title case
                    location = location_raw.title()
                
                # Enhanced notes for medespeler reservations
                notes_parts = []
                
                # First, check for remarks/notes in the card
                card_element = card.find_parent('div', class_='t-Card')
                if card_element:
                    card_info = card_element.find('div', class_='t-Card-info')
                    if card_info:
                        # Look for remark divs with content
                        remark_divs = card_info.find_all('div', id=re.compile(r'^remark_PL\d+$'))
                        for remark_div in remark_divs:
                            remark_text = remark_div.get_text(strip=True)
                            if remark_text:
                                notes_parts.append(f"💬 {remark_text}")
                                notes_parts.append("")  # Extra witregel na remark
                                print(f"  📝 Remark gevonden: {remark_text}")
                
                # Medespeler reservation details section
                notes_parts.append("⛳️ TEE RESERVATION")
                notes_parts.append("─" * 16)
                notes_parts.append(f"• Flight: {start_tijd_str.replace(':', 'h')}")
                
                # Search in the full description text since it's all on one line
                verantwoordelijke_match = re.search(r'Verantwoordelijke:\s*([^,\n]*?)(?=\s*Medespelers:)', desc_text)
                if verantwoordelijke_match:
                    verantwoordelijke_name = verantwoordelijke_match.group(1).strip()
                    notes_parts.append(f"• Host: {verantwoordelijke_name}")
                
                # Extract medespelers - look for everything after "Medespelers:" until the end
                medespelers_start = desc_text.find('Medespelers:')
                if medespelers_start != -1:
                    medespelers_text = desc_text[medespelers_start + len('Medespelers:'):].strip()
                    notes_parts.append(f"• Playing with: {medespelers_text}")
                
                notes = '\n'.join(notes_parts)
                
                print(f"  🏌️  Locatie: {location}")
                
                # Parse datetime en trek 30 minuten af
                start_tijd = datetime.strptime(start_tijd_str, '%H:%M').time()
                start_datetime = datetime.combine(
                    datetime.strptime(datum_str, '%d/%m/%Y').date(),
                    start_tijd
                ) - timedelta(minutes=30)
                # Make timezone-aware for Belgium
                start_datetime = BELGIUM_TZ.localize(start_datetime)
                
                # Maak event met proper formatting
                event = {
                    'title': f'⛳️  Tee-time @ {location}',
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
        
        # Fix location to include coordinates for clickable directions
        location = event_data['location']
        if location == "Royal Latem Golf Club":
            # Add full address for Apple Calendar compatibility
            event.location = "Royal Latem Golf Club, 9831 Sint-Martens-Latem, Belgium"
        elif location == "Royal Waterloo Golf Club":
            event.location = "Royal Waterloo Golf Club, 1380 Lasne, Belgium"
        elif location == "Brussels Droh!me Golf Club":
            event.location = "Brussels Droh!me Golf Club, 1000 Brussel, Belgium"
        elif location == "Antwerp Golfschool":
            event.location = "Antwerp Golfschool, 2000 Antwerpen, Belgium"
        elif location == "Royal Bercuit Golf Club":
            event.location = "Royal Bercuit Golf Club, 1300 Waver, Belgium"
        elif location == "Royal Golf Club des Fagnes":
            event.location = "Royal Golf Club des Fagnes, 4900 Spa, Belgium"
        elif location == "Royal Keerbergen Golf Club":
            event.location = "Royal Keerbergen Golf Club, 3140 Keerbergen, Belgium"
        elif location == "Brabantse Golf":
            event.location = "Brabantse Golf, 3000 Leuven, Belgium"
        elif location == "Golf du Château de la Bawette":
            event.location = "Golf du Château de la Bawette, 1300 Waver, Belgium"
        elif location == "Golfclub Hasselt":
            event.location = "Golfclub Hasselt, 3500 Hasselt, Belgium"
        elif location == "Lilse Golf & Country":
            event.location = "Lilse Golf & Country, 2275 Lille, Belgium"
        elif location == "Winge Golf":
            event.location = "Winge Golf, 3020 Herent, Belgium"
        elif location == "Damme Golf & Country Club":
            event.location = "Damme Golf & Country Club, 8340 Damme, Belgium"
        elif location == "Golf de Liège-Gomzé":
            event.location = "Golf de Liège-Gomzé, 4000 Luik, Belgium"
        elif location == "Golfclub Witbos":
            event.location = "Golfclub Witbos, 9000 Gent, Belgium"
        elif location == "Royal Amicale Anderlecht Golf Club":
            event.location = "Royal Amicale Anderlecht Golf Club, 1070 Anderlecht, Belgium"
        elif location == "Royal Golf Club Oudenaarde":
            event.location = "Royal Golf Club Oudenaarde, 9700 Oudenaarde, Belgium"
        elif location == "Golf de Rougemont":
            event.location = "Golf de Rougemont, 6900 Aarlen, Belgium"
        elif location == "Waregem Happy Golf":
            event.location = "Waregem Happy Golf, 8790 Waregem, Belgium"
        elif location == "Golf de la Bruyère":
            event.location = "Golf de la Bruyère, 1300 Waver, Belgium"
        elif location == "Golf Club du Haras":
            event.location = "Golf Club du Haras, 1000 Brussel, Belgium"
        elif location == "Golf & Business Association Kampenhout":
            event.location = "Golf & Business Association Kampenhout, 1910 Kampenhout, Belgium"
        elif location == "Avernas Golf Club":
            event.location = "Avernas Golf Club, 4280 Hannut, Belgium"
        elif location == "Golfforum Lummen":
            event.location = "Golfforum Lummen, 3560 Lummen, Belgium"
        elif location == "Durbuy Golf Resorts":
            event.location = "Durbuy Golf Resorts, 6940 Durbuy, Belgium"
        elif location == "Golfclub De Palingbeek":
            event.location = "Golfclub De Palingbeek, 8900 Ieper, Belgium"
        elif location == "Golf de Pierpont":
            event.location = "Golf de Pierpont, 7000 Bergen, Belgium"
        elif location == "Golf Club Enghien":
            event.location = "Golf Club Enghien, 7850 Enghien, Belgium"
        elif location == "Golfclub Beveren":
            event.location = "Golfclub Beveren, 9120 Beveren, Belgium"
        elif location == "Ieper Open Golf":
            event.location = "Ieper Open Golf, 8900 Ieper, Belgium"
        elif location == "Ragnies Golf Club":
            event.location = "Ragnies Golf Club, 6530 Thuin, Belgium"
        elif location == "Westgolf":
            event.location = "Westgolf, 8000 Brugge, Belgium"
        elif location == "Golf Découverte Virton":
            event.location = "Golf Découverte Virton, 6760 Virton, Belgium"
        elif location == "Executive Club - Private Golf Zwijnaarde":
            event.location = "Executive Club - Private Golf Zwijnaarde, 9052 Zwijnaarde, Belgium"
        elif location == "Millennium Golf":
            event.location = "Millennium Golf, 9000 Gent, Belgium"
        elif location == "Golfschool Gent":
            event.location = "Golfschool Gent, 9000 Gent, Belgium"
        elif location == "Wijnvelden Golf Club":
            event.location = "Wijnvelden Golf Club, 9000 Gent, Belgium"
        elif location == "Wellington Golf Oostende":
            event.location = "Wellington Golf Oostende, 8400 Oostende, Belgium"
        else:
            event.location = location
        
        # Convert timezone-aware datetime to UTC for ICS format
        start_datetime = event_data['start']
        if start_datetime.tzinfo is not None:
            # Convert to UTC for ICS format
            start_datetime_utc = start_datetime.astimezone(pytz.UTC)
        else:
            # If no timezone info, assume it's already in local time and convert to UTC
            start_datetime_utc = BELGIUM_TZ.localize(start_datetime).astimezone(pytz.UTC)
        
        event.begin = start_datetime_utc
        event.duration = event_data['duration']
        event.description = event_data.get('notes', '')
        
        # Note: Waze navigation link will be added manually to the iCal string
        
        calendar.events.add(event)
    
    # Generate the iCal string and add alarms manually
    ical_string = str(calendar)
    
    # Add alarms for each event
    for event_data in events:
        # Find the event in the iCal string and add alarms
        event_start = event_data['start']
        if event_start.tzinfo is not None:
            event_start_utc = event_start.astimezone(pytz.UTC)
        else:
            event_start_utc = BELGIUM_TZ.localize(event_start).astimezone(pytz.UTC)
        
        # Format the start time for iCal
        start_str = event_start_utc.strftime('%Y%m%dT%H%M%SZ')
        
        # Add alarm 1 day before only (Apple Calendar makes 2-hour alert automatically)
        alarm_1_day = f"""BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Herinnering: {event_data['title']} morgen
END:VALARM"""
        
        # Insert alarm before the END:VEVENT
        ical_string = ical_string.replace('END:VEVENT', f'{alarm_1_day}\nEND:VEVENT', 1)
        
        # Add Waze navigation links for specific golf clubs
        if event_data['location'] == "Royal Latem Golf Club":
            # Add Waze URL with correct iCal syntax
            waze_url = f"""URL;VALUE=URI:https://waze.com/ul/hu14d4qeqv
{alarm_1_day}"""
            ical_string = ical_string.replace(f'{alarm_1_day}\nEND:VEVENT', f'{waze_url}\nEND:VEVENT', 1)
        elif event_data['location'] == "Executive Club Private Golf Zwijnaarde":
            # Add Waze URL for Zwijnaarde
            waze_url = f"""URL;VALUE=URI:https://waze.com/ul/hu14dhskqx
{alarm_1_day}"""
            ical_string = ical_string.replace(f'{alarm_1_day}\nEND:VEVENT', f'{waze_url}\nEND:VEVENT', 1)
        elif event_data['location'] == "Golf en Country club":
            # Add Waze URL for Oudenaarde
            waze_url = f"""URL;VALUE=URI:https://waze.com/ul/hu1490u7c3
{alarm_1_day}"""
            ical_string = ical_string.replace(f'{alarm_1_day}\nEND:VEVENT', f'{waze_url}\nEND:VEVENT', 1)
        elif event_data['location'] == "Waregem Golf Club":
            # Add Waze URL for Waregem
            waze_url = f"""URL;VALUE=URI:https://waze.com/ul/hu143qythf
{alarm_1_day}"""
            ical_string = ical_string.replace(f'{alarm_1_day}\nEND:VEVENT', f'{waze_url}\nEND:VEVENT', 1)
        elif event_data['location'] == "Damme Golf & Country Club":
            # Add Waze URL for Damme
            waze_url = f"""URL;VALUE=URI:https://waze.com/ul/hu147k5f62
{alarm_1_day}"""
            ical_string = ical_string.replace(f'{alarm_1_day}\nEND:VEVENT', f'{waze_url}\nEND:VEVENT', 1)
        elif event_data['location'] == "Royal Zoute Golf Club":
            # Add Waze URL for Knokke
            waze_url = f"""URL;VALUE=URI:https://waze.com/ul/hu14k54ywq
{alarm_1_day}"""
            ical_string = ical_string.replace(f'{alarm_1_day}\nEND:VEVENT', f'{waze_url}\nEND:VEVENT', 1)
    
    return ical_string


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
        
        print("=== LOGGING IN AND NAVIGATING ===")
        # Login en ga direct naar reservaties
        if not scraper.login_and_navigate():
            raise Exception("Login en navigatie gefaald")
        print("✅ Login and navigation successful")
        
        print("=== SCRAPING RESERVATIONS ===")
        # Scrape reservaties
        events = scraper.scrape_reservations()
        print(f"✅ Scraped {len(events)} events")
        
        print("=== CREATING ICAL ===")
        # Maak iCal calendar
        ical_string = create_ical_calendar(events)
        print("✅ Calendar created")
        
        # Save to file
        output_file = 'golf.ics'
        print(f"=== SAVING TO {output_file} ===")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ical_string)
        
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