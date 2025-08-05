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
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # GitHub Actions specific options
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--single-process')
        
        # Use Chrome for Testing if available
        chrome_bin = os.environ.get('CHROME_BIN')
        if chrome_bin and os.path.exists(chrome_bin):
            print(f"🔄 Using Chrome for Testing: {chrome_bin}")
            options.binary_location = chrome_bin
        
        try:
            # Try system ChromeDriver first (for GitHub Actions)
            try:
                print("🔄 Trying system ChromeDriver...")
                service = Service('/usr/local/bin/chromedriver')
                self.driver = webdriver.Chrome(service=service, options=options)
                print("✅ Chrome driver geïnitialiseerd met system ChromeDriver")
            except Exception as e:
                print(f"⚠️  System ChromeDriver failed: {e}")
                # Fallback to webdriver-manager with specific version
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    print("🔄 Falling back to webdriver-manager...")
                    driver_path = ChromeDriverManager().install()
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                    print("✅ Chrome driver geïnitialiseerd met webdriver-manager")
                except Exception as e2:
                    print(f"⚠️  Webdriver-manager failed: {e2}")
                    # Final fallback: use a specific ChromeDriver version
                    print("🔄 Final fallback: downloading specific ChromeDriver version...")
                    import urllib.request
                    import zipfile
                    
                    # Download ChromeDriver 120.0.6099.109 (known to work with newer Chrome)
                    chromedriver_url = "https://chromedriver.storage.googleapis.com/120.0.6099.109/chromedriver_linux64.zip"
                    zip_path = "/tmp/chromedriver_fallback.zip"
                    
                    urllib.request.urlretrieve(chromedriver_url, zip_path)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall("/tmp/chromedriver_fallback")
                    
                    service = Service("/tmp/chromedriver_fallback/chromedriver")
                    self.driver = webdriver.Chrome(service=service, options=options)
                    print("✅ Chrome driver geïnitialiseerd met fallback ChromeDriver")
            
        except Exception as e:
            print(f"❌ Fout bij Chrome driver setup: {e}")
            raise
    
    def login(self):
        """Log in op i-Golf.be"""
        try:
            print("🔐 Bezig met inloggen op i-Golf.be...")
            self.driver.get(I_GOLF_URL)
            
            # Wacht op splash screen (4 seconden)
            time.sleep(4)
            
            # Zoek login velden
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "P101_USERNAME"))
            )
            password_field = self.driver.find_element(By.NAME, "P101_PASSWORD")
            
            # Vul credentials in
            username_field.clear()
            username_field.send_keys(USERNAME)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            # Submit via Enter key
            password_field.send_keys(Keys.RETURN)
            
            print("✅ Login gelukt, wachten op pagina...")
            time.sleep(4)
            
            # Check of we echt ingelogd zijn
            current_url = self.driver.current_url
            print(f"📍 URL na login: {current_url}")
            
            # Als we nog steeds op de login pagina zijn, probeer opnieuw
            if "LOGIN" in current_url.upper():
                print("⚠️  Nog steeds op login pagina, probeer opnieuw...")
                
                # Wacht langer
                time.sleep(6)
                
                # Check opnieuw
                current_url = self.driver.current_url
                print(f"📍 URL na extra wachttijd: {current_url}")
                
                if "LOGIN" in current_url.upper():
                    print("❌ Nog steeds niet ingelogd")
                    return False
            
            print("✅ Succesvol ingelogd")
            return True
            
        except Exception as e:
            print(f"❌ Login gefaald: {e}")
            return False
    
    def navigate_to_reservations(self):
        """Navigeer naar reservaties pagina via menu"""
        try:
            print("🧭 Navigeren naar reservaties...")
            
            # Check huidige URL
            print(f"📍 Huidige URL: {self.driver.current_url}")
            
            # Wacht even voor de pagina om te laden
            time.sleep(3)
            
            # Zoek naar de JULIEN knop
            print("🔍 Zoeken naar JULIEN knop...")
            julien_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'js-menuButton') and contains(., 'JULIEN')]"))
            )
            print("✅ JULIEN knop gevonden")
            
            # Klik op JULIEN knop om menu te openen
            print("🖱️  Klikken op JULIEN knop...")
            julien_btn.click()
            time.sleep(2)  # Wacht tot menu opent
            
            # Zoek naar "Uw reservaties" link in het menu
            print("🔍 Zoeken naar 'Uw reservaties' link...")
            reservations_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Uw reservaties')]"))
            )
            print("✅ 'Uw reservaties' link gevonden")
            
            # Klik op "Uw reservaties"
            print("🖱️  Klikken op 'Uw reservaties'...")
            reservations_link.click()
            
            # Wacht op pagina load
            time.sleep(4)
            
            # Check nieuwe URL
            current_url = self.driver.current_url
            print(f"📍 Nieuwe URL: {current_url}")
            
            if "LOGIN" not in current_url.upper():
                print("✅ Succesvol naar reservaties pagina gegaan")
                return True
            else:
                print("❌ Nog steeds op login pagina")
                return False
            
        except Exception as e:
            print(f"❌ Navigatie gefaald: {e}")
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
    print("🚀 Starting Golf iCal Generator for GitHub Actions...")
    print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    scraper = None
    try:
        # Initialiseer scraper
        scraper = IGolfScraper()
        
        # Login
        if not scraper.login():
            raise Exception("Login gefaald")
        
        # Navigeer naar reservaties
        if not scraper.navigate_to_reservations():
            raise Exception("Navigatie naar reservaties gefaald")
        
        # Scrape reservaties
        events = scraper.scrape_reservations()
        
        # Maak iCal calendar
        calendar = create_ical_calendar(events)
        
        # Save to file
        output_file = 'golf.ics'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(calendar))
        
        print(f"✅ iCal bestand gegenereerd: {output_file}")
        print(f"📊 Aantal events: {len(events)}")
        
        # Print event details for debugging
        for i, event_data in enumerate(events[:5]):  # Show first 5
            print(f"  {i+1}. {event_data['title']} - {event_data['start'].strftime('%Y-%m-%d %H:%M')}")
        
        if len(events) > 5:
            print(f"  ... en {len(events) - 5} meer events")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout bij genereren iCal: {e}")
        # Create empty calendar file
        empty_calendar = Calendar()
        with open('golf.ics', 'w', encoding='utf-8') as f:
            f.write(str(empty_calendar))
        print("⚠️  Leeg iCal bestand gegenereerd")
        return False
        
    finally:
        if scraper:
            scraper.close()


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1) 