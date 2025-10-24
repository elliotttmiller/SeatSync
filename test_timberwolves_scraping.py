"""
Comprehensive End-to-End Test Script for Minnesota Timberwolves Ticket Price Scraping
This script validates the entire scraping workflow with real-time data collection
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
import json

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_scraping_workflow():
    """
    Test the complete ticket scraping workflow for Minnesota Timberwolves
    """
    print("=" * 80)
    print("COMPREHENSIVE END-TO-END TEST: Minnesota Timberwolves Ticket Price Scraping")
    print("=" * 80)
    print(f"\nTest Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Import scraping services
        from app.services.scraping_service import scrape_tickets, get_scraping_service
        from app.services.scrapling_service import SCRAPLING_AVAILABLE
        
        print("✅ Backend services imported successfully\n")
        
        # Check Scrapling availability
        if not SCRAPLING_AVAILABLE:
            print("❌ ERROR: Scrapling is not available!")
            print("   Install with: pip install 'scrapling[all]>=0.3.7' && scrapling install")
            return False
        else:
            print("✅ Scrapling is available and ready\n")
        
        # Get scraping service status
        service = await get_scraping_service()
        status = service.get_status()
        
        print("=" * 80)
        print("SCRAPING SERVICE STATUS")
        print("=" * 80)
        print(f"Initialized: {status['initialized']}")
        print(f"Scraper Type: {status['scraper_type']}")
        print(f"Capabilities: {', '.join(status['capabilities'])}")
        print()
        
        # Test parameters for Minnesota Timberwolves
        test_team = "Minnesota Timberwolves"
        marketplaces_to_test = ["StubHub", "SeatGeek"]  # Start with 2 as recommended
        
        print("=" * 80)
        print(f"TEST CONFIGURATION: {test_team}")
        print("=" * 80)
        print(f"Marketplaces to test: {', '.join(marketplaces_to_test)}")
        print(f"Search Query: {test_team}")
        print()
        
        # Store results for each marketplace
        all_results = {}
        
        for marketplace in marketplaces_to_test:
            print("=" * 80)
            print(f"TESTING MARKETPLACE: {marketplace}")
            print("=" * 80)
            print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
            print(f"Target: {test_team}")
            print(f"URL will be constructed automatically by scraper\n")
            
            try:
                # Scrape the marketplace
                result = await scrape_tickets(
                    marketplace=marketplace,
                    search_query=test_team,
                    adaptive=False  # First run, not adaptive
                )
                
                all_results[marketplace] = result
                
                # Display results
                print(f"\nRESULTS from {marketplace}:")
                print(f"Status: {result['status']}")
                print(f"Platform: {result.get('platform', 'N/A')}")
                print(f"URL: {result.get('url', 'N/A')}")
                print(f"Timestamp: {result.get('timestamp', 'N/A')}")
                
                if result['status'] == 'success':
                    listings = result.get('listings', [])
                    print(f"\n✅ SUCCESS: Found {len(listings)} listings")
                    
                    if listings:
                        # Calculate statistics
                        prices = [l['price'] for l in listings if 'price' in l]
                        
                        if prices:
                            print(f"\nPRICE STATISTICS:")
                            print(f"  Total Listings: {len(listings)}")
                            print(f"  Average Price: ${sum(prices) / len(prices):.2f}")
                            print(f"  Minimum Price: ${min(prices):.2f}")
                            print(f"  Maximum Price: ${max(prices):.2f}")
                            print(f"  Price Range: ${max(prices) - min(prices):.2f}")
                            
                            # Show sample listings
                            print(f"\nSAMPLE LISTINGS (first 5):")
                            for i, listing in enumerate(listings[:5], 1):
                                print(f"  {i}. ${listing.get('price', 'N/A'):.2f} - "
                                      f"Section: {listing.get('section', 'N/A')}, "
                                      f"Row: {listing.get('row', 'N/A')}, "
                                      f"Qty: {listing.get('quantity', 'N/A')}")
                        else:
                            print("⚠️ WARNING: No price data in listings")
                    else:
                        print("⚠️ WARNING: No listings found (might be no current events)")
                else:
                    print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
                
                print(f"\nCompleted: {datetime.now().strftime('%H:%M:%S')}")
                print()
                
            except Exception as e:
                print(f"\n❌ ERROR scraping {marketplace}: {str(e)}")
                import traceback
                traceback.print_exc()
                all_results[marketplace] = {
                    'status': 'error',
                    'error': str(e),
                    'listings': []
                }
            
            # Small delay between marketplaces
            await asyncio.sleep(2)
        
        # Final summary
        print("=" * 80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print(f"Test Team: {test_team}")
        print(f"Marketplaces Tested: {len(marketplaces_to_test)}")
        print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        total_listings = 0
        successful_scrapes = 0
        
        for marketplace, result in all_results.items():
            status = result['status']
            count = len(result.get('listings', []))
            total_listings += count
            
            if status == 'success':
                successful_scrapes += 1
                print(f"✅ {marketplace}: SUCCESS - {count} listings")
            else:
                print(f"❌ {marketplace}: FAILED - {result.get('error', 'Unknown error')}")
        
        print(f"\nTotal Listings Collected: {total_listings}")
        print(f"Success Rate: {successful_scrapes}/{len(marketplaces_to_test)} "
              f"({successful_scrapes/len(marketplaces_to_test)*100:.0f}%)")
        
        # Save results to file
        results_file = Path(__file__).parent / "test_results_timberwolves.json"
        with open(results_file, 'w') as f:
            json.dump({
                'test_team': test_team,
                'test_date': datetime.now().isoformat(),
                'marketplaces': marketplaces_to_test,
                'results': all_results,
                'summary': {
                    'total_listings': total_listings,
                    'successful_scrapes': successful_scrapes,
                    'success_rate': f"{successful_scrapes/len(marketplaces_to_test)*100:.0f}%"
                }
            }, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_file}")
        
        # Cleanup
        await service.cleanup()
        print("\n✅ Cleanup complete")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        return successful_scrapes > 0
        
    except ImportError as e:
        print(f"\n❌ ERROR: Failed to import backend services")
        print(f"Error: {e}")
        print("\nPlease ensure backend dependencies are installed:")
        print("  pip install -r backend/requirements.txt")
        return False
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Fix Windows asyncio issue
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the test
    success = asyncio.run(test_scraping_workflow())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
