# 🏌️ Golf iCal Feed Generator

Automatically sync your golf reservations from i-Golf.be to your calendar! This project uses GitHub Actions to scrape your golf reservations daily and provides them as an iCal feed that works with Apple Calendar, Google Calendar, and other calendar applications.

## ✨ Features

- 🔄 **Automatic Updates**: Runs hourly via GitHub Actions
- 📱 **Universal Compatibility**: Works with Apple Calendar, Google Calendar, Outlook, and more
- 🔒 **Secure**: Credentials stored as GitHub secrets
- 🌍 **Timezone Aware**: Properly handles Belgian timezone
- 📊 **Comprehensive**: Captures competitions, tee times, and playing partner reservations
- 🚀 **Zero Maintenance**: Set it up once and forget about it

## 🎯 What It Does

This tool automatically:
1. Logs into your i-Golf.be account
2. Scrapes all your golf reservations (competitions, tee times, playing partner bookings)
3. Generates an iCal file with proper formatting
4. Updates the feed hourly so your calendar stays current

## 🚀 Quick Start

### Prerequisites
- A GitHub account
- An i-Golf.be account with active reservations
- Basic familiarity with GitHub

### Setup Steps

1. **Fork this repository**
   - Click the "Fork" button at the top right of this page
   - This creates your own copy of the project

2. **Configure GitHub Secrets**
   - Go to your forked repository → Settings → Secrets and variables → Actions
   - Add two new repository secrets:
     - `I_GOLF_USERNAME`: Your i-Golf federation number
     - `I_GOLF_PASSWORD`: Your i-Golf password

3. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: "main" → Save

4. **Update the Reservations URL**
   - Open `github_action.py` in your repository
   - Find line 37: `RESERVATIONS_URL = "https://www.i-golf.be/ords/f?p=165:119:714053694681593:::::"`
   - Go to i-Golf.be and navigate to your reservations page
   - Copy the URL from your browser's address bar
   - Replace the URL in the code with your personal reservations URL
   - Commit and push the changes

5. **Test the Workflow**
   - Go to Actions tab → "Update Golf Calendar" → "Run workflow"
   - Wait 2-3 minutes for completion

6. **Get Your iCal URL**
   - Your feed will be available at: `https://[YOUR_USERNAME].github.io/golf-ical-project/golf.ics`
   - Replace `[YOUR_USERNAME]` with your GitHub username

## 📱 Adding to Your Calendar

### Apple Calendar (Mac/iPhone)
1. Open Calendar app
2. **Mac**: File → New Calendar Subscription...
   **iPhone**: Settings → Calendar → Accounts → Add Account → Other → Add CalDAV Account
3. Paste your iCal URL
4. Set refresh frequency to "Every hour"

### Google Calendar
1. Go to [calendar.google.com](https://calendar.google.com)
2. Settings → Import & Export → Add calendar → From URL
3. Paste your iCal URL
4. Click "Add calendar"

### Other Calendar Apps
Most calendar applications support iCal feeds. Look for options like:
- "Add calendar from URL"
- "Subscribe to calendar"
- "Import calendar"

## 🛠️ Technical Details

### Project Structure
```
golf-ical-project/
├── github_action.py          # Main scraping script
├── requirements.txt          # Python dependencies
├── .github/workflows/        # GitHub Actions configuration
├── golf.ics                 # Generated iCal file (auto-created)
└── README.md               # This file
```

### Dependencies
- **selenium**: Web scraping automation
- **beautifulsoup4**: HTML parsing
- **ics**: iCal file generation
- **pytz**: Timezone handling
- **python-dotenv**: Environment variable management

### How It Works
1. **Authentication**: Uses Selenium to log into i-Golf.be
2. **Scraping**: Extracts reservation data from three sections:
   - Competitions (wedstrijden)
   - Tee reservations (tee-reservaties)
   - Playing partner bookings (medespeler reservaties)
3. **Processing**: Parses dates, times, and locations
4. **Generation**: Creates properly formatted iCal events
5. **Deployment**: Commits the file to GitHub for public access

## 🔒 Security & Privacy

- **Credentials**: Stored securely as GitHub repository secrets
- **No Data Storage**: Only processes your reservations, doesn't store them
- **Public Feed**: The generated iCal file is publicly accessible via GitHub Pages
- **Local Development**: Use `.env` file for testing (see below)

### Local Development
For testing or development:
1. Create a `.env` file:
   ```
   I_GOLF_USERNAME=your_federation_number
   I_GOLF_PASSWORD=your_password
   ```
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python github_action.py`

## 🐛 Troubleshooting

### Common Issues

**Workflow fails to run:**
- Check GitHub Actions logs for detailed error messages
- Verify your GitHub secrets are correctly set
- Ensure your i-Golf credentials are valid

**Calendar not updating:**
- Verify the iCal URL is correct
- Check that GitHub Pages is enabled
- Wait for the next scheduled update or trigger manually

**No reservations showing:**
- Confirm you have active reservations on i-Golf.be
- Check the workflow logs for scraping errors
- Verify the reservation dates are in the future

### Getting Help
1. Check the GitHub Actions logs for detailed error information
2. Verify all setup steps were completed correctly
3. Ensure your repository is public (required for GitHub Pages)
4. Test with a manual workflow run

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs or issues
- Suggest improvements
- Submit pull requests
- Help improve documentation

## 🙏 Acknowledgments

- Built for the Belgian golf community
- Uses GitHub Actions for automation
- Inspired by the need for better calendar integration

---

**Made with ❤️ for golf enthusiasts**

*If this project helps you stay organized with your golf schedule, consider giving it a ⭐!*
