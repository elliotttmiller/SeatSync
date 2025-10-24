"""
Scrapling-based Web Scraping Service
Modern, efficient web scraping using the Scrapling library

This service provides:
- Adaptive element tracking (survives website structure changes)
- Superior anti-bot detection bypass
- 685x faster parsing performance
- Built-in TLS fingerprinting and Cloudflare bypass
- Clean, simple API
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Try to import Scrapling
try:
    from scrapling.fetchers import StealthyFetcher, StealthySession
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False
    logger.warning("Scrapling not available. Install with: pip install 'scrapling[all]' && scrapling install")


class ScraplingScrapingService:
    """
    Modern web scraping service powered by Scrapling
    
    Features:
    - Adaptive element tracking (auto-relocates elements when websites change)
    - Advanced stealth mode with Cloudflare bypass
    - TLS fingerprint impersonation
    - Superior performance (685x faster parsing)
    - Clean API with session management
    """
    
    def __init__(self):
        self.session = None
        self.initialized = False
        self.scraper_type = "scrapling"
    
    async def initialize(self) -> bool:
        """
        Initialize the Scrapling-based scraper
        Much simpler than the old implementation!
        """
        if not SCRAPLING_AVAILABLE:
            logger.error("Scrapling not available. Cannot initialize.")
            return False
        
        if self.initialized:
            return True
        
        try:
            # Initialize with advanced stealth settings
            # Note: We'll use one-off requests for now, session can be added later
            logger.info("Initializing Scrapling scraper...")
            
            self.initialized = True
            self.scraper_type = "scrapling"
            
            logger.info("✅ Scrapling scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Scrapling scraper: {e}")
            return False
    
    async def scrape_marketplace(
        self,
        marketplace: str,
        search_query: Optional[str] = None,
        event_url: Optional[str] = None,
        adaptive: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape a marketplace with Scrapling
        
        Args:
            marketplace: Name of marketplace (stubhub, seatgeek, etc)
            search_query: Search term for events
            event_url: Direct URL to event page
            adaptive: Use adaptive element tracking (survives website changes)
            
        Returns:
            Dictionary with scraping results
        """
        if not self.initialized:
            await self.initialize()
        
        if not self.initialized:
            return {
                'status': 'error',
                'platform': marketplace.lower(),
                'listings': [],
                'error': 'Failed to initialize Scrapling. Please install: pip install "scrapling[all]" && scrapling install',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            marketplace_lower = marketplace.lower()
            
            # Route to appropriate scraper method
            if marketplace_lower == 'stubhub':
                result = await self._scrape_stubhub(event_url, search_query, adaptive)
            elif marketplace_lower == 'seatgeek':
                result = await self._scrape_seatgeek(event_url, search_query, adaptive)
            elif marketplace_lower == 'ticketmaster':
                result = await self._scrape_ticketmaster(event_url, search_query, adaptive)
            elif marketplace_lower == 'vividseats':
                result = await self._scrape_vividseats(event_url, search_query, adaptive)
            else:
                result = {
                    'status': 'error',
                    'error': f'Unsupported marketplace: {marketplace}'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Scraping error for {marketplace}: {e}", exc_info=True)
            return {
                'status': 'error',
                'platform': marketplace.lower(),
                'listings': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _scrape_stubhub(
        self,
        event_url: Optional[str] = None,
        search_query: Optional[str] = None,
        adaptive: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape StubHub using Scrapling's advanced stealth features
        
        This is MUCH simpler than the old implementation!
        """
        try:
            # Determine URL
            if event_url:
                url = event_url
            else:
                url = f'https://www.stubhub.com/find/s/?q={search_query or "sports"}'
            
            logger.info(f"Scraping StubHub with Scrapling: {url}")
            
            # Use StealthyFetcher with Cloudflare bypass
            # This is a one-off request - for production, consider using StealthySession
            page = StealthyFetcher.fetch(
                url,
                headless=True,
                solve_cloudflare=True,  # Auto-bypass Cloudflare!
                google_search=False,
                network_idle=True
            )
            
            # Extract listings using adaptive selection if enabled
            # Scrapling's adaptive feature will find elements even if selectors change!
            if adaptive:
                # Use adaptive mode - Scrapling will find similar elements
                listing_elements = page.css('[data-testid*="listing"], .sc-listing, .EventCard', adaptive=True)
            else:
                # First time scraping - use auto_save to remember the structure
                listing_elements = page.css('[data-testid*="listing"], .sc-listing, .EventCard', auto_save=True)
            
            # Extract data from listings
            listings = []
            for element in listing_elements:
                try:
                    # Extract price - Scrapling supports multiple methods
                    price_element = element.css_first('[data-testid*="price"], .price, .PriceLabel')
                    price_text = price_element.text if price_element else None
                    
                    if price_text:
                        # Clean price
                        price = float(price_text.replace('$', '').replace(',', '').strip())
                        
                        # Extract section
                        section_element = element.css_first('[data-testid*="section"], .section')
                        section = section_element.text if section_element else ''
                        
                        # Extract row
                        row_element = element.css_first('[data-testid*="row"], .row')
                        row = row_element.text if row_element else ''
                        
                        # Extract quantity
                        qty_element = element.css_first('[data-testid*="quantity"], .quantity')
                        qty_text = qty_element.text if qty_element else '1'
                        quantity = int(''.join(filter(str.isdigit, qty_text)) or '1')
                        
                        listings.append({
                            'price': price,
                            'section': section,
                            'row': row,
                            'quantity': quantity,
                            'platform': 'stubhub'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing listing element: {e}")
                    continue
            
            logger.info(f"StubHub: Found {len(listings)} listings with Scrapling")
            
            return {
                'status': 'success',
                'platform': 'stubhub',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
                'scraper': 'scrapling'
            }
            
        except Exception as e:
            logger.error(f"StubHub scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'stubhub',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _scrape_seatgeek(
        self,
        event_url: Optional[str] = None,
        search_query: Optional[str] = None,
        adaptive: bool = False
    ) -> Dict[str, Any]:
        """Scrape SeatGeek using Scrapling"""
        try:
            url = event_url or f'https://seatgeek.com/search?q={search_query or "sports"}'
            logger.info(f"Scraping SeatGeek with Scrapling: {url}")
            
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
            
            # Use adaptive selection
            listing_elements = page.css(
                '[data-testid="listing"], .listing, .EventCard',
                adaptive=adaptive,
                auto_save=not adaptive
            )
            
            listings = []
            for element in listing_elements:
                try:
                    price_element = element.css_first('[data-testid="price"], .price')
                    if price_element and price_element.text:
                        price = float(price_element.text.replace('$', '').replace(',', '').strip())
                        
                        section_element = element.css_first('[data-testid="section"], .section')
                        section = section_element.text if section_element else ''
                        
                        listings.append({
                            'price': price,
                            'section': section,
                            'platform': 'seatgeek'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing listing: {e}")
                    continue
            
            logger.info(f"SeatGeek: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'seatgeek',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
                'scraper': 'scrapling'
            }
            
        except Exception as e:
            logger.error(f"SeatGeek scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'seatgeek',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _scrape_ticketmaster(
        self,
        event_url: Optional[str] = None,
        search_query: Optional[str] = None,
        adaptive: bool = False
    ) -> Dict[str, Any]:
        """Scrape Ticketmaster using Scrapling"""
        try:
            url = event_url or f'https://www.ticketmaster.com/search?q={search_query or "sports"}'
            logger.info(f"Scraping Ticketmaster with Scrapling: {url}")
            
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
            
            listing_elements = page.css(
                '[data-testid="event-card"], .event-card, .offer',
                adaptive=adaptive,
                auto_save=not adaptive
            )
            
            listings = []
            for element in listing_elements:
                try:
                    price_element = element.css_first('[data-testid="price"], .price')
                    if price_element and price_element.text:
                        price = float(price_element.text.replace('$', '').replace(',', '').strip())
                        
                        section_element = element.css_first('[data-testid="section"], .section')
                        section = section_element.text if section_element else ''
                        
                        listings.append({
                            'price': price,
                            'section': section,
                            'platform': 'ticketmaster'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing listing: {e}")
                    continue
            
            logger.info(f"Ticketmaster: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'ticketmaster',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
                'scraper': 'scrapling'
            }
            
        except Exception as e:
            logger.error(f"Ticketmaster scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'ticketmaster',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _scrape_vividseats(
        self,
        event_url: Optional[str] = None,
        search_query: Optional[str] = None,
        adaptive: bool = False
    ) -> Dict[str, Any]:
        """Scrape Vivid Seats using Scrapling"""
        try:
            url = event_url or f'https://www.vividseats.com/search?search={search_query or "sports"}'
            logger.info(f"Scraping Vivid Seats with Scrapling: {url}")
            
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
            
            listing_elements = page.css(
                '[data-testid="listing"], .listing, .productionListItem',
                adaptive=adaptive,
                auto_save=not adaptive
            )
            
            listings = []
            for element in listing_elements:
                try:
                    price_element = element.css_first('[data-testid="price"], .price')
                    if price_element and price_element.text:
                        price = float(price_element.text.replace('$', '').replace(',', '').strip())
                        
                        section_element = element.css_first('[data-testid="section"], .section')
                        section = section_element.text if section_element else ''
                        
                        listings.append({
                            'price': price,
                            'section': section,
                            'platform': 'vividseats'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing listing: {e}")
                    continue
            
            logger.info(f"Vivid Seats: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'vividseats',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
                'scraper': 'scrapling'
            }
            
        except Exception as e:
            logger.error(f"Vivid Seats scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'vividseats',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Clean up resources - Scrapling handles most cleanup automatically"""
        logger.info("Scrapling scraper cleanup complete")
        self.initialized = False
        self.session = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scraper status"""
        return {
            'initialized': self.initialized,
            'scraper_type': self.scraper_type,
            'capabilities': self._get_capabilities()
        }
    
    def _get_capabilities(self) -> List[str]:
        """Get list of supported features"""
        if not self.initialized:
            return []
        
        return [
            'stubhub',
            'seatgeek',
            'ticketmaster',
            'vividseats',
            'adaptive_tracking',  # NEW: Survives website changes!
            'cloudflare_bypass',  # NEW: Built-in Cloudflare bypass
            'tls_fingerprinting', # NEW: Browser impersonation
            'fast_parsing',       # NEW: 685x faster than BeautifulSoup
            'javascript_rendering',
            'anti_detection',
            'human_simulation'
        ]


# Global instance
_scrapling_service = None


async def get_scrapling_service() -> ScraplingScrapingService:
    """Get or create the global Scrapling service instance"""
    global _scrapling_service
    
    if _scrapling_service is None:
        _scrapling_service = ScraplingScrapingService()
        await _scrapling_service.initialize()
    
    return _scrapling_service


async def scrape_tickets_scrapling(
    marketplace: str,
    search_query: Optional[str] = None,
    event_url: Optional[str] = None,
    adaptive: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for quick scraping with Scrapling
    
    Args:
        marketplace: Marketplace name (stubhub, seatgeek, ticketmaster, vividseats)
        search_query: Search query string
        event_url: Direct event URL
        adaptive: Use adaptive element tracking (True if website structure changed)
        
    Returns:
        Scraping results dictionary
    """
    service = await get_scrapling_service()
    return await service.scrape_marketplace(
        marketplace=marketplace,
        search_query=search_query,
        event_url=event_url,
        adaptive=adaptive
    )
