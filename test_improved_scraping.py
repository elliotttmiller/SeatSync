"""
Test improved anti-bot bypass with actual Minnesota Timberwolves URL
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def test_improved_scraping():
    """Test with actual StubHub URL and improved stealth settings"""
    print("=" * 80)
    print("TESTING IMPROVED ANTI-BOT BYPASS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        from app.services.scraping_service import scrape_tickets
        from app.services.scrapling_service import SCRAPLING_AVAILABLE
        
        if not SCRAPLING_AVAILABLE:
            print("❌ Scrapling not available")
            return False
        
        print("✅ Scrapling is available\n")
        
        # Test 1: With actual StubHub URL (from user comment)
        print("=" * 80)
        print("TEST 1: Direct URL (Actual Minnesota Timberwolves page)")
        print("=" * 80)
        print("URL: https://www.stubhub.com/minnesota-timberwolves-tickets/performer/2986")
        print("\nUsing enhanced stealth mode:")
        print("  ✓ Full stealth enabled")
        print("  ✓ AWS WAF challenge solving")
        print("  ✓ Extended wait time (5s)")
        print("  ✓ All resources loaded\n")
        
        result = await scrape_tickets(
            marketplace="StubHub",
            event_url="https://www.stubhub.com/minnesota-timberwolves-tickets/performer/2986"
        )
        
        print(f"Status: {result['status']}")
        print(f"Listings Found: {len(result.get('listings', []))}")
        
        if result.get('message'):
            print(f"Message: {result['message']}")
        
        if result['status'] == 'error':
            print(f"Error: {result.get('error', 'Unknown')}")
        else:
            listings = result.get('listings', [])
            if listings:
                print(f"\n✅ SUCCESS! Found {len(listings)} ticket listings")
                print("\nFirst 3 listings:")
                for i, listing in enumerate(listings[:3], 1):
                    print(f"  {i}. ${listing.get('price', 'N/A'):.2f} - "
                          f"Section: {listing.get('section', 'N/A')}, "
                          f"Row: {listing.get('row', 'N/A')}")
            else:
                print("\n⚠️ No listings found (may be off-season or no current games)")
        
        # Test 2: Search-based discovery
        print("\n" + "=" * 80)
        print("TEST 2: Search-Based Discovery")
        print("=" * 80)
        print("Search Query: 'Minnesota Timberwolves'")
        print("Using enhanced stealth for automatic URL discovery\n")
        
        result2 = await scrape_tickets(
            marketplace="StubHub",
            search_query="Minnesota Timberwolves"
        )
        
        print(f"Status: {result2['status']}")
        print(f"URL Found: {result2.get('url', 'N/A')}")
        print(f"Listings Found: {len(result2.get('listings', []))}")
        
        if result2.get('message'):
            print(f"Message: {result2['message']}")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("\n✅ IMPROVEMENTS IMPLEMENTED:")
        print("  • Full stealth mode enabled (stealth=True)")
        print("  • AWS WAF challenge solving (solve_cloudflare=True)")
        print("  • Extended wait time for dynamic content (wait=3-5s)")
        print("  • All resources loaded (disable_resources=False)")
        print("  • AWS WAF detection and logging")
        print("  • Better page validation (checks for event links)")
        
        print("\n📝 KEY FEATURES:")
        print("  • Scrapling uses modified Firefox with fingerprint spoofing")
        print("  • Automatic Cloudflare & AWS WAF bypass")
        print("  • TLS fingerprint randomization")
        print("  • Realistic browser behavior simulation")
        
        print(f"\n✅ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return result['status'] == 'success' or result2['status'] == 'success'
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    success = asyncio.run(test_improved_scraping())
    sys.exit(0 if success else 1)
