#!/bin/bash

echo "🚀 Golf iCal Project GitHub Setup Script"
echo "========================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Initial commit
echo "💾 Making initial commit..."
git commit -m "Initial commit: Golf iCal Feed Generator"

echo ""
echo "✅ Local git repository is ready!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub.com named 'golf-ical-project'"
echo "2. Make sure it's PUBLIC (required for GitHub Pages)"
echo "3. Run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/golf-ical-project.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Set up GitHub Secrets (I_GOLF_USERNAME and I_GOLF_PASSWORD)"
echo "5. Enable GitHub Pages in repository settings"
echo ""
echo "📖 See README.md for detailed step-by-step instructions" 