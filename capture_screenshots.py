"""
Create screenshots of the Streamlit app demonstrating the Minnesota Timberwolves workflow
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import time

async def capture_streamlit_screenshots():
    """Capture screenshots of the Streamlit dashboard"""
    
    screenshots_dir = Path(__file__).parent / "test_screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    print("Starting browser for screenshot capture...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            # Navigate to Streamlit app
            print("Navigating to Streamlit app...")
            await page.goto('http://localhost:8502', wait_until='networkidle', timeout=30000)
            
            # Wait for the app to load
            await page.wait_for_timeout(3000)
            
            # Capture home page
            print("Capturing home page...")
            await page.screenshot(path=screenshots_dir / '1_home_page.png', full_page=True)
            
            # Navigate to scraping page
            print("Navigating to scraping page...")
            # Click on the scraping nav button - use the first one (radio button)
            await page.get_by_test_id("stRadio").get_by_text('🕷️ Data Collection & Scraping').click()
            await page.wait_for_timeout(2000)
            
            # Capture scraping page
            print("Capturing scraping page...")
            await page.screenshot(path=screenshots_dir / '2_scraping_page.png', full_page=True)
            
            # Fill in Minnesota Timberwolves
            print("Filling in search query...")
            search_box = page.get_by_label('Search Query')
            if await search_box.count() > 0:
                await search_box.fill('Minnesota Timberwolves')
                await page.wait_for_timeout(1000)
                
                # Take screenshot with filled form
                await page.screenshot(path=screenshots_dir / '3_scraping_form_filled.png', full_page=True)
            
            # Navigate to ML Training page
            print("Navigating to ML Training page...")
            await page.get_by_test_id("stRadio").get_by_text('🤖 ML Model Training').click()
            await page.wait_for_timeout(2000)
            
            # Capture ML training page
            print("Capturing ML training page...")
            await page.screenshot(path=screenshots_dir / '4_ml_training_page.png', full_page=True)
            
            # Navigate to Price Prediction
            print("Navigating to Price Prediction page...")
            await page.get_by_test_id("stRadio").get_by_text('💰 Price Prediction').click()
            await page.wait_for_timeout(2000)
            
            # Capture prediction page
            print("Capturing prediction page...")
            await page.screenshot(path=screenshots_dir / '5_price_prediction_page.png', full_page=True)
            
            # Navigate to Performance Metrics
            print("Navigating to Performance Metrics page...")
            await page.get_by_test_id("stRadio").get_by_text('📊 Performance Metrics').click()
            await page.wait_for_timeout(2000)
            
            # Capture metrics page
            print("Capturing metrics page...")
            await page.screenshot(path=screenshots_dir / '6_performance_metrics.png', full_page=True)
            
            print(f"\n✅ Screenshots saved to: {screenshots_dir}")
            print("Screenshots captured:")
            for screenshot in sorted(screenshots_dir.glob('*.png')):
                print(f"  - {screenshot.name}")
            
        except Exception as e:
            print(f"Error capturing screenshots: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_streamlit_screenshots())
