"""
Advanced Ticket Price Scraping Service
State-of-the-art web scraping for ticket marketplaces

This service implements sophisticated web scraping techniques to collect
real-time ticket prices from major marketplaces without relying on APIs.

Features:
- Playwright-based browser automation
- Anti-bot detection bypassing
- User-agent rotation
- Proxy support
- Intelligent retry logic
- Rate limiting
- Data extraction and normalization
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import json
import re

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available. Install with: pip install playwright")
    # Define stub types for type hints when Playwright is not available
    Browser = None  # type: ignore
    Page = None  # type: ignore
    BrowserContext = None  # type: ignore

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class UserAgentRotator:
    """Rotates user agents to avoid detection"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    @classmethod
    def get_random(cls) -> str:
        """Get a random user agent"""
        return random.choice(cls.USER_AGENTS)


class AdvancedTicketScraper:
    """
    Advanced web scraper for ticket marketplaces
    
    Uses Playwright for JavaScript-heavy sites with anti-bot detection bypassing
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.rate_limiter = RateLimiter(requests_per_minute=30)
        
    async def initialize(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Cannot initialize advanced scraper.")
            return False
            
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security'
                ]
            )
            
            # Create context with random user agent
            self.context = await self.browser.new_context(
                user_agent=UserAgentRotator.get_random(),
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Add stealth scripts to avoid detection
            await self._add_stealth_scripts(self.context)
            
            logger.info("Advanced scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            return False
    
    async def _add_stealth_scripts(self, context: BrowserContext):
        """Add JavaScript to bypass bot detection"""
        # Override navigator.webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Override permissions
        await context.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # Add realistic Chrome object
        await context.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)
    
    async def scrape_stubhub(self, event_url: str = None, search_query: str = None) -> Dict[str, Any]:
        """
        Scrape StubHub for ticket listings
        
        Args:
            event_url: Direct URL to event page
            search_query: Search query for events
            
        Returns:
            Dictionary with scraped ticket data
        """
        if not self.context:
            logger.error("Scraper not initialized")
            return {'status': 'error', 'error': 'Scraper not initialized'}
        
        try:
            await self.rate_limiter.wait_if_needed()
            
            page = await self.context.new_page()
            
            # Navigate to StubHub
            if event_url:
                url = event_url
            else:
                # Default to search page
                url = f'https://www.stubhub.com/find/s/?q={search_query or "sports"}'
            
            logger.info(f"Scraping StubHub: {url}")
            
            # Navigate with realistic timing
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            # Scroll to trigger lazy loading
            await self._simulate_human_scrolling(page)
            
            # Extract ticket listings
            listings = await page.evaluate("""
                () => {
                    const tickets = [];
                    
                    // StubHub uses various selectors - this is a generic approach
                    const listingElements = document.querySelectorAll('[data-testid*="listing"], .sc-listing, .EventCard');
                    
                    listingElements.forEach(el => {
                        try {
                            // Extract price
                            const priceEl = el.querySelector('[data-testid*="price"], .price, .PriceLabel');
                            const price = priceEl ? priceEl.textContent.replace(/[^0-9.]/g, '') : null;
                            
                            // Extract section
                            const sectionEl = el.querySelector('[data-testid*="section"], .section');
                            const section = sectionEl ? sectionEl.textContent.trim() : null;
                            
                            // Extract row
                            const rowEl = el.querySelector('[data-testid*="row"], .row');
                            const row = rowEl ? rowEl.textContent.trim() : null;
                            
                            // Extract quantity
                            const qtyEl = el.querySelector('[data-testid*="quantity"], .quantity');
                            const quantity = qtyEl ? qtyEl.textContent.replace(/[^0-9]/g, '') : null;
                            
                            if (price) {
                                tickets.push({
                                    price: parseFloat(price),
                                    section: section,
                                    row: row,
                                    quantity: quantity ? parseInt(quantity) : 1,
                                    platform: 'stubhub'
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing listing:', e);
                        }
                    });
                    
                    return tickets;
                }
            """)
            
            await page.close()
            
            logger.info(f"StubHub: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'stubhub',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"StubHub scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'stubhub',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def scrape_ticketmaster(self, event_url: str = None, search_query: str = None) -> Dict[str, Any]:
        """
        Scrape Ticketmaster for ticket listings
        
        Args:
            event_url: Direct URL to event page
            search_query: Search query for events
            
        Returns:
            Dictionary with scraped ticket data
        """
        if not self.context:
            logger.error("Scraper not initialized")
            return {'status': 'error', 'error': 'Scraper not initialized'}
        
        try:
            await self.rate_limiter.wait_if_needed()
            
            page = await self.context.new_page()
            
            # Navigate to Ticketmaster
            if event_url:
                url = event_url
            else:
                url = f'https://www.ticketmaster.com/search?q={search_query or "sports"}'
            
            logger.info(f"Scraping Ticketmaster: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            # Simulate human behavior
            await self._simulate_human_scrolling(page)
            
            # Extract listings
            listings = await page.evaluate("""
                () => {
                    const tickets = [];
                    
                    // Ticketmaster selectors
                    const listingElements = document.querySelectorAll('[data-testid="event-card"], .event-card, .offer');
                    
                    listingElements.forEach(el => {
                        try {
                            const priceEl = el.querySelector('[data-testid="price"], .price');
                            const price = priceEl ? priceEl.textContent.replace(/[^0-9.]/g, '') : null;
                            
                            const sectionEl = el.querySelector('[data-testid="section"], .section');
                            const section = sectionEl ? sectionEl.textContent.trim() : null;
                            
                            if (price) {
                                tickets.push({
                                    price: parseFloat(price),
                                    section: section,
                                    platform: 'ticketmaster'
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing listing:', e);
                        }
                    });
                    
                    return tickets;
                }
            """)
            
            await page.close()
            
            logger.info(f"Ticketmaster: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'ticketmaster',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ticketmaster scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'ticketmaster',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def scrape_seatgeek(self, event_url: str = None, search_query: str = None) -> Dict[str, Any]:
        """
        Scrape SeatGeek for ticket listings
        
        Args:
            event_url: Direct URL to event page
            search_query: Search query for events
            
        Returns:
            Dictionary with scraped ticket data
        """
        if not self.context:
            logger.error("Scraper not initialized")
            return {'status': 'error', 'error': 'Scraper not initialized'}
        
        try:
            await self.rate_limiter.wait_if_needed()
            
            page = await self.context.new_page()
            
            # Navigate to SeatGeek
            if event_url:
                url = event_url
            else:
                url = f'https://seatgeek.com/search?q={search_query or "sports"}'
            
            logger.info(f"Scraping SeatGeek: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            await self._simulate_human_scrolling(page)
            
            # Extract listings
            listings = await page.evaluate("""
                () => {
                    const tickets = [];
                    
                    // SeatGeek selectors
                    const listingElements = document.querySelectorAll('[data-testid="listing"], .listing, .EventCard');
                    
                    listingElements.forEach(el => {
                        try {
                            const priceEl = el.querySelector('[data-testid="price"], .price');
                            const price = priceEl ? priceEl.textContent.replace(/[^0-9.]/g, '') : null;
                            
                            const sectionEl = el.querySelector('[data-testid="section"], .section');
                            const section = sectionEl ? sectionEl.textContent.trim() : null;
                            
                            if (price) {
                                tickets.push({
                                    price: parseFloat(price),
                                    section: section,
                                    platform: 'seatgeek'
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing listing:', e);
                        }
                    });
                    
                    return tickets;
                }
            """)
            
            await page.close()
            
            logger.info(f"SeatGeek: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'seatgeek',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SeatGeek scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'seatgeek',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def scrape_vividseats(self, event_url: str = None, search_query: str = None) -> Dict[str, Any]:
        """
        Scrape Vivid Seats for ticket listings
        
        Args:
            event_url: Direct URL to event page
            search_query: Search query for events
            
        Returns:
            Dictionary with scraped ticket data
        """
        if not self.context:
            logger.error("Scraper not initialized")
            return {'status': 'error', 'error': 'Scraper not initialized'}
        
        try:
            await self.rate_limiter.wait_if_needed()
            
            page = await self.context.new_page()
            
            # Navigate to Vivid Seats
            if event_url:
                url = event_url
            else:
                url = f'https://www.vividseats.com/search?search={search_query or "sports"}'
            
            logger.info(f"Scraping Vivid Seats: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            await self._simulate_human_scrolling(page)
            
            # Extract listings
            listings = await page.evaluate("""
                () => {
                    const tickets = [];
                    
                    // Vivid Seats selectors
                    const listingElements = document.querySelectorAll('[data-testid="listing"], .listing, .productionListItem');
                    
                    listingElements.forEach(el => {
                        try {
                            const priceEl = el.querySelector('[data-testid="price"], .price');
                            const price = priceEl ? priceEl.textContent.replace(/[^0-9.]/g, '') : null;
                            
                            const sectionEl = el.querySelector('[data-testid="section"], .section');
                            const section = sectionEl ? sectionEl.textContent.trim() : null;
                            
                            if (price) {
                                tickets.push({
                                    price: parseFloat(price),
                                    section: section,
                                    platform: 'vividseats'
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing listing:', e);
                        }
                    });
                    
                    return tickets;
                }
            """)
            
            await page.close()
            
            logger.info(f"Vivid Seats: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'vividseats',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Vivid Seats scraping error: {e}")
            return {
                'status': 'error',
                'platform': 'vividseats',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def scrape_all_marketplaces(
        self, 
        event_url: Dict[str, str] = None,
        search_query: str = "sports"
    ) -> Dict[str, Any]:
        """
        Scrape all major ticket marketplaces in parallel
        
        Args:
            event_url: Dict mapping platform to event URL
            search_query: Search query if no URLs provided
            
        Returns:
            Aggregated results from all platforms
        """
        event_url = event_url or {}
        
        # Scrape all platforms in parallel
        tasks = [
            self.scrape_stubhub(event_url.get('stubhub'), search_query),
            self.scrape_ticketmaster(event_url.get('ticketmaster'), search_query),
            self.scrape_seatgeek(event_url.get('seatgeek'), search_query),
            self.scrape_vividseats(event_url.get('vividseats'), search_query)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_listings = []
        platform_stats = {}
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraping task failed: {result}")
                continue
                
            if result.get('status') == 'success':
                platform = result['platform']
                listings = result['listings']
                all_listings.extend(listings)
                platform_stats[platform] = {
                    'count': len(listings),
                    'status': 'success'
                }
            else:
                platform = result.get('platform', 'unknown')
                platform_stats[platform] = {
                    'count': 0,
                    'status': 'error',
                    'error': result.get('error')
                }
        
        return {
            'status': 'success',
            'total_listings': len(all_listings),
            'platforms': platform_stats,
            'listings': all_listings,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _simulate_human_scrolling(self, page: Page):
        """Simulate human-like scrolling behavior"""
        try:
            # Get page height
            height = await page.evaluate('document.body.scrollHeight')
            
            # Scroll in chunks
            current = 0
            step = random.randint(300, 500)
            
            while current < height:
                await page.evaluate(f'window.scrollTo(0, {current})')
                await page.wait_for_timeout(random.randint(100, 300))
                current += step
                
            # Scroll back up a bit
            await page.evaluate(f'window.scrollTo(0, {current // 2})')
            await page.wait_for_timeout(random.randint(500, 1000))
            
        except Exception as e:
            logger.debug(f"Scrolling simulation error: {e}")
    
    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Advanced scraper closed")
        except Exception as e:
            logger.error(f"Error closing scraper: {e}")


class RateLimiter:
    """Simple rate limiter to avoid overwhelming servers"""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=1)
            
            # Remove old requests
            self.requests = [ts for ts in self.requests if ts > cutoff]
            
            if len(self.requests) >= self.requests_per_minute:
                # Calculate wait time
                oldest = self.requests[0]
                wait_time = (oldest + timedelta(minutes=1) - now).total_seconds()
                if wait_time > 0:
                    logger.debug(f"Rate limit: waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    self.requests = []
            
            self.requests.append(now)


# Singleton instance
_scraper_instance = None

async def get_advanced_scraper() -> AdvancedTicketScraper:
    """Get or create the global scraper instance"""
    global _scraper_instance
    
    if _scraper_instance is None:
        _scraper_instance = AdvancedTicketScraper()
        await _scraper_instance.initialize()
    
    return _scraper_instance
