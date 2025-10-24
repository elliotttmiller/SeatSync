"""
Debug script to see what's actually on the StubHub page
"""

import sys
import asyncio
from pathlib import Path
import concurrent.futures

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def debug_stubhub_page():
    """See what elements we can actually find on StubHub"""
    try:
        from scrapling.fetchers import StealthyFetcher
        
        url = "https://www.stubhub.com/minnesota-timberwolves-tickets/performer/5937/"
        print(f"Fetching: {url}\n")
        
        loop = asyncio.get_event_loop()
        
        def fetch():
            return StealthyFetcher.fetch(
                url,
                headless=True,
                solve_cloudflare=True,
                google_search=False,
                network_idle=True,
                wait=5  # Wait 5 seconds for JS to render
            )
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            page = await loop.run_in_executor(executor, fetch)
        
        print("Page fetched successfully!\n")
        
        # Try to get all links
        all_links = page.css('a')
        print(f"Total links on page: {len(all_links)}")
        
        # Filter for event-like links
        event_patterns = ['/event/', '-tickets-', '-vs-', '/game/']
        event_like_links = []
        
        for link in all_links[:100]:  # Check first 100 links
            href = link.attrib.get('href', '')
            text = link.text.strip() if link.text else ''
            
            if any(pattern in href.lower() for pattern in event_patterns):
                event_like_links.append((href, text))
        
        print(f"\nEvent-like links found: {len(event_like_links)}")
        if event_like_links:
            print("\nSample event links:")
            for href, text in event_like_links[:10]:
                print(f"  - {text[:50] if text else '(no text)'}")
                print(f"    {href[:80]}")
        
        # Try to find specific elements
        print("\n" + "=" * 80)
        print("Testing various selectors:")
        
        selectors_to_test = [
            'a[href*="/event/"]',
            'a[data-testid*="event"]',
            '.eventCard a',
            '.event-card a',
            '[class*="Event"] a',
            '[data-testid*="card"]',
            'button[href]',
            '[role="link"]',
        ]
        
        for selector in selectors_to_test:
            try:
                elements = page.css(selector)
                print(f"  {selector}: {len(elements)} elements")
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        # Get page HTML (first 5000 chars)
        print("\n" + "=" * 80)
        print("Page HTML sample (first 2000 chars):")
        html = page.html if hasattr(page, 'html') else str(page)
        print(html[:2000])
        
        # Try to find any event data in JSON/script tags
        print("\n" + "=" * 80)
        print("Looking for JSON data in page...")
        scripts = page.css('script')
        for i, script in enumerate(scripts[:5]):
            text = script.text if script.text else ''
            if 'event' in text.lower() and len(text) > 100:
                print(f"\nScript {i} (first 500 chars):")
                print(text[:500])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_stubhub_page())
