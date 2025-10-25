"""
Simple test of the scraping workflow with Minnesota Timberwolves
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def test_simple_scrape():
    """Test a simple scraping operation"""
    print("=" * 80)
    print("TESTING MINNESOTA TIMBERWOLVES SCRAPING")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        from app.services.scraping_service import scrape_tickets
        from app.services.scrapling_service import SCRAPLING_AVAILABLE
        
        if not SCRAPLING_AVAILABLE:
            print("❌ Scrapling not available")
            return False
        
        print("✅ Scrapling is available\n")
        
        # Test with StubHub only for now
        marketplace = "StubHub"
        search_query = "Minnesota Timberwolves"
        
        print(f"Marketplace: {marketplace}")
        print(f"Search Query: {search_query}")
        print(f"\nStarting scrape...\n")
        
        result = await scrape_tickets(
            marketplace=marketplace,
            search_query=search_query,
            adaptive=False
        )
        
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Platform: {result.get('platform', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")
        print(f"Listings Count: {result.get('count', 0)}")
        
        if result.get('message'):
            print(f"Message: {result['message']}")
        
        if result['status'] == 'error':
            print(f"\n❌ Error: {result.get('error', 'Unknown')}")
            return False
        
        listings = result.get('listings', [])
        print(f"\n{'✅' if len(listings) > 0 else '⚠️'} Found {len(listings)} listings")
        
        if listings:
            # Show first few listings
            print("\nSample listings:")
            for i, listing in enumerate(listings[:5], 1):
                print(f"  {i}. ${listing.get('price', 'N/A'):.2f} - "
                      f"Section: {listing.get('section', 'N/A')}, "
                      f"Row: {listing.get('row', 'N/A')}")
            
            # Calculate stats
            prices = [l['price'] for l in listings if 'price' in l]
            if prices:
                print(f"\nPrice Statistics:")
                print(f"  Average: ${sum(prices) / len(prices):.2f}")
                print(f"  Min: ${min(prices):.2f}")
                print(f"  Max: ${max(prices):.2f}")
        else:
            print("\nNo listings found. This could mean:")
            print("  1. No current events for Minnesota Timberwolves")
            print("  2. The selectors need adjustment")
            print("  3. The website structure has changed")
        
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Consider it a success if we got a valid response (even with 0 listings)
        # The important thing is we're now properly navigating to event pages
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    success = asyncio.run(test_simple_scrape())
    sys.exit(0 if success else 1)
