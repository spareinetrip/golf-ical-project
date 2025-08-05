#!/usr/bin/env python3
"""
Test script voor debugging van de scraping
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
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Configuraties
I_GOLF_URL = "https://www.i-golf.be"
USERNAME = "714410"
PASSWORD = "Julien"

def setup_driver():
    """Setup Chrome driver (zichtbaar voor debugging)"""
    options = Options()
    # options.add_argument('--headless')  # Commented out for debugging
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        service = Service('/opt/homebrew/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome driver geïnitialiseerd")
        return driver
    except Exception as e:
        print(f"❌ Fout bij Chrome driver setup: {e}")
        raise

def login(driver):
    """Log in op i-Golf.be"""
    try:
        print("🔐 Bezig met inloggen op i-Golf.be...")
        driver.get(I_GOLF_URL)
        
        # Wacht op splash screen
        time.sleep(4)
        
        # Zoek login velden
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "P101_USERNAME"))
        )
        password_field = driver.find_element(By.NAME, "P101_PASSWORD")
        
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
        current_url = driver.current_url
        print(f"📍 URL na login: {current_url}")
        
        # Als we nog steeds op de login pagina zijn, probeer opnieuw
        if "LOGIN" in current_url.upper():
            print("⚠️  Nog steeds op login pagina, probeer opnieuw...")
            
            # Wacht langer
            time.sleep(6)
            
            # Check opnieuw
            current_url = driver.current_url
            print(f"📍 URL na extra wachttijd: {current_url}")
            
            if "LOGIN" in current_url.upper():
                print("❌ Nog steeds niet ingelogd")
                return False
        
        print("✅ Succesvol ingelogd")
        return True
        
    except Exception as e:
        print(f"❌ Login gefaald: {e}")
        return False

def navigate_to_reservations(driver):
    """Navigeer naar reservaties pagina via menu"""
    try:
        print("🧭 Navigeren naar reservaties...")
        
        # Check huidige URL
        print(f"📍 Huidige URL: {driver.current_url}")
        
        # Wacht even voor de pagina om te laden
        time.sleep(3)
        
        # Zoek naar de JULIEN knop
        print("🔍 Zoeken naar JULIEN knop...")
        julien_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'js-menuButton') and contains(., 'JULIEN')]"))
        )
        print("✅ JULIEN knop gevonden")
        
        # Klik op JULIEN knop om menu te openen
        print("🖱️  Klikken op JULIEN knop...")
        julien_btn.click()
        time.sleep(2)  # Wacht tot menu opent
        
        # Zoek naar "Uw reservaties" link in het menu
        print("🔍 Zoeken naar 'Uw reservaties' link...")
        reservations_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Uw reservaties')]"))
        )
        print("✅ 'Uw reservaties' link gevonden")
        
        # Klik op "Uw reservaties"
        print("🖱️  Klikken op 'Uw reservaties'...")
        reservations_link.click()
        
        # Wacht op pagina load
        time.sleep(4)
        
        # Check nieuwe URL
        current_url = driver.current_url
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

def test_scraping(driver):
    """Test de scraping"""
    try:
        print("📊 Bezig met testen van scraping...")
        
        # Get page source en parse met BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Debug: Print pagina titel
        print(f"📄 Pagina titel: {driver.title}")
        
        # Zoek naar alle h3 elementen
        h3_elements = soup.find_all('h3')
        print(f"🔍 Gevonden {len(h3_elements)} h3 elementen")
        
        for i, h3 in enumerate(h3_elements):
            title = h3.get_text(strip=True)
            classes = h3.get('class', [])
            print(f"  {i+1}. {title} (classes: {classes})")
        
        # Zoek naar alle div elementen met 'Card' in de class
        card_divs = soup.find_all('div', class_=lambda x: x and 'Card' in x)
        print(f"🔍 Gevonden {len(card_divs)} div elementen met 'Card' in class")
        
        for i, div in enumerate(card_divs):
            classes = div.get('class', [])
            print(f"  {i+1}. classes: {classes}")
        
        # Zoek naar alle elementen met 't-Card' in de class
        t_card_elements = soup.find_all(class_=lambda x: x and 't-Card' in x)
        print(f"🔍 Gevonden {len(t_card_elements)} elementen met 't-Card' in class")
        
        for i, elem in enumerate(t_card_elements):
            tag = elem.name
            classes = elem.get('class', [])
            text = elem.get_text(strip=True)[:50]
            print(f"  {i+1}. <{tag}> classes: {classes} text: {text}...")
        
        # Zoek naar alle elementen met datum/tijd patterns
        all_text = soup.get_text()
        date_patterns = re.findall(r'\d{2}/\d{2}/\d{4}', all_text)
        print(f"🔍 Gevonden {len(date_patterns)} datum patterns: {date_patterns[:5]}")
        
        # Print alle tekst op de pagina (eerste 1000 karakters)
        print(f"📄 Pagina tekst (eerste 1000 karakters):")
        print(all_text[:1000])
        
        # Zoek naar specifieke woorden die op reservaties duiden
        keywords = ['reservatie', 'reservation', 'wedstrijd', 'competition', 'tee', 'golf']
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in all_text.lower():
                found_keywords.append(keyword)
        print(f"🔍 Gevonden keywords: {found_keywords}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test scraping gefaald: {e}")
        return False

def main():
    """Hoofdfunctie"""
    driver = None
    try:
        # Setup driver
        driver = setup_driver()
        
        # Login
        if not login(driver):
            return
        
        # Navigeer naar reservaties
        if not navigate_to_reservations(driver):
            return
        
        # Test scraping
        test_scraping(driver)
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🔒 Browser gesloten")

if __name__ == '__main__':
    main() 