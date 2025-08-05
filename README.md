# Golf iCal Feed Generator

Een automatische iCal feed generator voor golfreservaties van i-Golf.be. Dit project gebruikt GitHub Actions om dagelijks je golfreservaties op te halen en beschikbaar te maken als iCal feed.

## 🚀 Snelle Setup (Stap-voor-Stap)

### Stap 1: GitHub Repository Aanmaken

1. Ga naar [GitHub.com](https://github.com) en log in
2. Klik op de groene "New" knop om een nieuwe repository aan te maken
3. Geef je repository een naam: `golf-ical-project`
4. Zorg ervoor dat de repository **Public** is (nodig voor GitHub Pages)
5. Klik "Create repository"

### Stap 2: Bestanden Uploaden

1. In je nieuwe repository, klik op "uploading an existing file"
2. Sleep alle bestanden uit deze map naar de upload area:
   - `github_action.py`
   - `requirements.txt`
   - `.github/workflows/update-golf-calendar.yml`
   - `index.html`
   - `README.md`
3. Klik "Commit changes"

### Stap 3: GitHub Secrets Instellen

1. Ga naar je repository op GitHub
2. Klik op "Settings" (tandwiel icoon)
3. Scroll naar beneden en klik op "Secrets and variables" → "Actions"
4. Klik op "New repository secret"
5. Voeg twee secrets toe:

   **Secret 1:**
   - Name: `I_GOLF_USERNAME`

   **Secret 2:**
   - Name: `I_GOLF_PASSWORD`

6. Klik "Add secret" voor beide

### Stap 4: GitHub Pages Activeren

1. Ga naar "Settings" → "Pages"
2. Onder "Source", selecteer "Deploy from a branch"
3. Onder "Branch", selecteer "main" en klik "Save"
4. Wacht een paar minuten tot je site live is

### Stap 5: GitHub Actions Testen

1. Ga naar "Actions" tab in je repository
2. Je zou de "Update Golf Calendar" workflow moeten zien
3. Klik erop en klik "Run workflow" → "Run workflow"
4. Wacht tot de workflow klaar is (ongeveer 2-3 minuten)

### Stap 6: iCal Feed Gebruiken

1. Ga naar je GitHub Pages site: `https://[YOUR_USERNAME].github.io/golf-ical-project/`
2. Kopieer de iCal URL: `https://[YOUR_USERNAME].github.io/golf-ical-project/golf.ics`
3. Vervang `[YOUR_USERNAME]` met je GitHub gebruikersnaam

## 📱 Calendar App Setup

### Apple Calendar (Mac/iPhone)

1. Open Calendar app
2. File → New Calendar Subscription... (Mac)
   of Settings → Calendar → Accounts → Add Account → Other → Add CalDAV Account (iPhone)
3. Voer de iCal URL in
4. Klik Subscribe
5. Geef calendar een naam (bijv. "Golf Reservaties")
6. Refresh frequency: Every hour

### Google Calendar

1. Ga naar [calendar.google.com](https://calendar.google.com)
2. Settings → Import & Export → Add calendar → From URL
3. Voer de iCal URL in
4. Klik "Add calendar"

## 🔧 Technische Details

### Bestanden Uitleg

- `github_action.py`: Het hoofdscript dat de golfreservaties ophaalt
- `requirements.txt`: Python dependencies
- `.github/workflows/update-golf-calendar.yml`: GitHub Actions workflow
- `index.html`: Webpagina met instructies
- `golf.ics`: Het gegenereerde iCal bestand (wordt automatisch aangemaakt)

### Workflow Schema

De GitHub Actions workflow:
- Draait elke dag om 8:00 AM (Belgische tijd)
- Logt in op i-Golf.be
- Scraped alle reservaties
- Genereert een iCal bestand
- Commit en pusht het bestand naar de repository

### Automatische Updates

- **Frequentie**: Dagelijks om 8:00 AM
- **Trigger**: Automatisch via cron job
- **Manual trigger**: Mogelijk via GitHub Actions tab

## 🛠️ Troubleshooting

### Workflow Fails

1. Check de "Actions" tab voor error logs
2. Controleer of je GitHub secrets correct zijn ingesteld
3. Zorg ervoor dat je i-Golf credentials nog geldig zijn

### iCal Feed Werkt Niet

1. Controleer of het `golf.ics` bestand bestaat in je repository
2. Verifieer de URL spelling
3. Wacht een paar minuten na een workflow run

### Calendar Updates Niet

1. Controleer de refresh frequency in je calendar app
2. Probeer de calendar opnieuw toe te voegen
3. Wacht tot de volgende dagelijkse update

## 🔒 Veiligheid

- Je i-Golf credentials worden veilig opgeslagen als GitHub secrets
- Ze zijn niet zichtbaar in de code of logs
- Alleen jij en GitHub hebben toegang tot deze secrets

## 📞 Support

Als je problemen ondervindt:

1. Check de GitHub Actions logs voor error details
2. Controleer of alle stappen correct zijn uitgevoerd
3. Zorg ervoor dat je repository public is
4. Verifieer dat GitHub Pages is geactiveerd

## 🎯 Wat Je Krijgt

Na setup heb je:
- ✅ Automatische dagelijkse updates van je golfreservaties
- ✅ iCal feed beschikbaar via GitHub Pages
- ✅ Werkt met Apple Calendar, Google Calendar en andere apps
- ✅ Geen handmatige updates nodig
- ✅ Gratis hosting via GitHub

---

**Gemaakt met ❤️ voor golf liefhebbers**
