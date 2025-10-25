"""
Simple example: Using direct event URLs during development
This approach works immediately and bypasses search-based discovery challenges
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def demo_direct_urls():
    """
    Demonstrate using direct event URLs - works immediately!
    No need to deal with AWS WAF on search pages
    """
    print("=" * 80)
    print("DIRECT EVENT URL APPROACH - Development Friendly")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        from app.services.scraping_service import scrape_tickets
        from app.services.scrapling_service import SCRAPLING_AVAILABLE
        
        if not SCRAPLING_AVAILABLE:
            print("❌ Scrapling not available")
            print("Install: pip install 'scrapling[all]>=0.3.7' && camoufox fetch")
            return False
        
        print("✅ Scrapling is available\n")
        
        # Example 1: Minnesota Timberwolves (from user's comment)
        print("=" * 80)
        print("EXAMPLE 1: Minnesota Timberwolves")
        print("=" * 80)
        print("URL: https://www.stubhub.com/minnesota-timberwolves-tickets/performer/2986")
        print("Approach: Direct URL (bypasses search)")
        print()
        
        result = await scrape_tickets(
            marketplace="StubHub",
            event_url="https://www.stubhub.com/minnesota-timberwolves-tickets/performer/2986"
        )
        
        print(f"Status: {result['status']}")
        print(f"Listings: {len(result.get('listings', []))}")
        
        if result.get('listings'):
            print("\n✅ SUCCESS! Sample listings:")
            for i, listing in enumerate(result['listings'][:5], 1):
                print(f"  {i}. ${listing.get('price', 'N/A'):.2f} - "
                      f"Section: {listing.get('section', 'N/A')}")
        else:
            print("\n⚠️ No listings found (may be off-season or awaiting event page)")
        
        print("\n" + "=" * 80)
        print("HOW TO GET EVENT URLs FOR YOUR TEAM")
        print("=" * 80)
        print("""
1. Visit marketplace website (stubhub.com, seatgeek.com, etc.)
2. Search for your team/event manually
3. Click on the team/performer page (not a specific game)
4. Copy the URL from browser
5. Use it in your code

Example URLs:
- StubHub: https://www.stubhub.com/{team-slug}-tickets/performer/{id}
- SeatGeek: https://seatgeek.com/{team-slug}-tickets

This approach:
✅ Works immediately (no AWS WAF on event pages)
✅ Tests your scraping logic
✅ Gets real ticket data
✅ Perfect for development

For production, you can still add search-based discovery later.
        """)
        
        print("=" * 80)
        print("USAGE IN YOUR CODE")
        print("=" * 80)
        print("""
from backend.app.services.scraping_service import scrape_tickets

# Just provide the event URL
result = await scrape_tickets(
    marketplace="StubHub",
    event_url="https://www.stubhub.com/minnesota-timberwolves-tickets/performer/2986"
)

# Check if we got tickets
if result['status'] == 'success':
    tickets = result['listings']
    print(f"Found {len(tickets)} tickets")
    
    for ticket in tickets:
        print(f"${ticket['price']:.2f} - Section {ticket['section']}")
else:
    print(f"Error: {result.get('error')}")
        """)
        
        print(f"\n✅ Demo completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    success = asyncio.run(demo_direct_urls())
    sys.exit(0 if success else 1)
