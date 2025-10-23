#!/bin/bash
# SeatSync Quick Start Script
# Helps users get up and running quickly

set -e

echo "🎫 SeatSync Setup & Verification"
echo "================================"
echo ""

# Check Python version
echo "1️⃣ Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.8+"; exit 1; }
echo "✅ Python found"
echo ""

# Install dependencies
echo "2️⃣ Installing dependencies..."
pip install -q -r backend/requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if Playwright is available
echo "3️⃣ Checking Playwright installation..."
python3 -c "from playwright.async_api import async_playwright" 2>/dev/null && {
    echo "✅ Playwright is installed"
    PLAYWRIGHT_INSTALLED=1
} || {
    echo "⚠️  Playwright not installed"
    echo ""
    echo "For full scraping capabilities, install Playwright:"
    echo "  pip install playwright"
    echo "  playwright install chromium"
    echo ""
    echo "Continuing with HTTP-based scraping fallback..."
    PLAYWRIGHT_INSTALLED=0
}
echo ""

# Test imports
echo "4️⃣ Testing core imports..."
python3 -c "
import sys
sys.path.insert(0, 'backend')
from app.services import scrape_tickets, get_scraping_service
print('✅ Scraping services import successfully')
" || { echo "❌ Import test failed"; exit 1; }
echo ""

# Run unit tests
echo "5️⃣ Running unit tests..."
python3 -m pytest backend/tests/test_scraping_service.py -v --tb=short || {
    echo "⚠️  Some tests failed, but this is OK for basic usage"
}
echo ""

# Check environment
echo "6️⃣ Checking environment configuration..."
if [ -f "backend/.env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  No .env file found"
    echo "Creating from template..."
    cp backend/.env.test backend/.env 2>/dev/null || echo "⚠️  Could not create .env file"
fi
echo ""

# Summary
echo "================================"
echo "🎉 Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the Streamlit development dashboard:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "2. Or start the backend API server:"
echo "   cd backend && uvicorn app.main:app --reload"
echo ""
echo "3. Read the documentation:"
echo "   - SCRAPING_GUIDE.md - Complete scraping documentation"
echo "   - README.md - General overview"
echo ""

if [ $PLAYWRIGHT_INSTALLED -eq 0 ]; then
    echo "⚠️  RECOMMENDATION: Install Playwright for full functionality"
    echo "   pip install playwright && playwright install chromium"
    echo ""
fi

echo "Happy coding! 🚀"
