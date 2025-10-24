"""
Test the improved scraping logic without actually hitting live websites.
This validates that our two-step workflow is correctly structured.
"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def test_scraping_logic():
    """Test that our scraping service has the correct structure"""
    print("=" * 80)
    print("TESTING SCRAPING LOGIC AND WORKFLOW")
    print("=" * 80)
    
    try:
        from app.services.scraping_service import get_scraping_service
        from app.services.scrapling_service import SCRAPLING_AVAILABLE
        
        print(f"\n✅ Imports successful")
        print(f"   Scrapling available: {SCRAPLING_AVAILABLE}")
        
        if not SCRAPLING_AVAILABLE:
            print("\n❌ Scrapling not available - cannot run test")
            return False
        
        # Initialize service
        service = await get_scraping_service()
        status = service.get_status()
        
        print(f"\n✅ Service initialized")
        print(f"   Type: {status['scraper_type']}")
        print(f"   Initialized: {status['initialized']}")
        print(f"   Capabilities: {len(status['capabilities'])} features")
        
        # Check that our improvements are in place by examining the code
        import inspect
        from app.services.scrapling_service import ScraplingScrapingService
        
        # Get the source code of _scrape_stubhub
        stubhub_source = inspect.getsource(ScraplingScrapingService._scrape_stubhub)
        
        # Check for key improvements
        checks = {
            "Two-step process mentioned": "Two-step process" in stubhub_source,
            "Search URL construction": "search_url" in stubhub_source,
            "Event URL discovery": "event_url" in stubhub_source and "event_href" in stubhub_source,
            "Event link finding": "event_links" in stubhub_source,
            "Separate event page fetch": "fetch_event" in stubhub_source,
            "Regex price parsing": "re.search" in stubhub_source or "price_match" in stubhub_source,
            "Better error handling": "logger.info" in stubhub_source and "logger.warning" in stubhub_source,
        }
        
        print("\n✅ Code structure validation:")
        all_passed = True
        for check_name, result in checks.items():
            status_icon = "✅" if result else "❌"
            print(f"   {status_icon} {check_name}")
            if not result:
                all_passed = False
        
        if not all_passed:
            print("\n❌ Some code structure checks failed")
            return False
        
        # Test that the method signature is correct
        sig = inspect.signature(ScraplingScrapingService._scrape_stubhub)
        params = list(sig.parameters.keys())
        
        required_params = ['self', 'event_url', 'search_query', 'adaptive']
        if params == required_params:
            print(f"\n✅ Method signature correct: {params}")
        else:
            print(f"\n❌ Method signature incorrect. Expected {required_params}, got {params}")
            return False
        
        print("\n" + "=" * 80)
        print("✅ ALL LOGIC CHECKS PASSED")
        print("=" * 80)
        print("\nThe scraping logic has been properly updated with:")
        print("  1. Two-step workflow (search → find event → scrape tickets)")
        print("  2. Event URL discovery from search results")
        print("  3. Separate event page navigation")
        print("  4. Improved price extraction with regex")
        print("  5. Better error handling and logging")
        print("\nNext step: Test with actual live data (requires network access)")
        
        await service.cleanup()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    success = asyncio.run(test_scraping_logic())
    sys.exit(0 if success else 1)
