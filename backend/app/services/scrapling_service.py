"""
Scrapling-based Web Scraping Service
Modern, efficient web scraping using the Scrapling library

This service provides:
- Adaptive element tracking (survives website structure changes)
- Superior anti-bot detection bypass (Cloudflare, AWS WAF, etc.)
- 685x faster parsing performance
- Built-in TLS fingerprinting and challenge solving
- Clean, simple API

ANTI-BOT BYPASS CAPABILITIES:
Scrapling uses StealthyFetcher with advanced capabilities:
- Modified Firefox browser with fingerprint spoofing
- Automatic Cloudflare Turnstile/Interstitial bypass
- AWS WAF challenge solving
- TLS fingerprint randomization
- Realistic browser behavior simulation

For best results during development:
- Use full stealth mode (stealth=True)
- Allow sufficient wait time for dynamic content (wait=3-5 seconds)
- Enable solve_cloudflare for automatic challenge handling
- Keep disable_resources=False to ensure proper page rendering

If you still encounter blocks, consider:
- Using residential IPs or proxy rotation
- Adding random delays between requests
- Running from different geographic locations
- For production: official APIs still recommended for reliability
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import re
import urllib.parse

logger = logging.getLogger(__name__)

# Configuration constants
AWS_WAF_WAIT_TIME = 25  # seconds to wait for AWS WAF challenge to complete

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
        
        NOTE: StubHub uses AWS WAF which may block automated browsers.
        If scraping fails, consider:
        - Using StubHub's official API (recommended for production)
        - Using residential proxies
        - Running from different geographic locations
        
        Two-step process:
        1. If no event_url provided, search for events and find the first matching event URL
        2. Navigate to event page and scrape actual ticket listings
        """
        try:
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            # Step 1: Find event URL if not provided
            if not event_url:
                if not search_query:
                    return {
                        'status': 'error',
                        'platform': 'stubhub',
                        'error': 'Either event_url or search_query must be provided',
                        'listings': [],
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Search for events on StubHub
                # StubHub structure: performer pages list all events for a team/artist
                encoded_query = urllib.parse.quote(search_query)
                
                # Try multiple URL formats for StubHub
                # Format: https://www.stubhub.com/{team-slug}-tickets/performer/{id}
                # We'll try the direct performer page format first
                performer_slug = search_query.lower().replace(' ', '-')
                search_urls = [
                    f'https://www.stubhub.com/{performer_slug}-tickets',
                    f'https://www.stubhub.com/find?q={encoded_query}',
                ]
                
                logger.info(f"Searching StubHub for: {search_query}")
                
                search_page = None
                successful_url = None
                
                for search_url in search_urls:
                    try:
                        logger.info(f"Trying URL: {search_url}")
                        
                        def fetch_search():
                            # Use Scrapling's stealth capabilities
                            # AWS WAF requires JavaScript execution and page reload
                            # We'll use page_action to wait for navigation after the challenge
                            
                            def wait_for_reload(page):
                                """Wait for AWS WAF challenge to complete and page to reload"""
                                # Wait for AWS WAF challenge to process
                                time.sleep(AWS_WAF_WAIT_TIME)  # Give plenty of time for JavaScript to execute
                                logger.info(f"Waited {AWS_WAF_WAIT_TIME} seconds for AWS WAF challenge to complete")
                            
                            return StealthyFetcher.fetch(
                                search_url,
                                headless=True,  # Use headless mode (required for server environments)
                                solve_cloudflare=False,
                                google_search=False,
                                network_idle=True,
                                wait=5000,
                                humanize=True,
                                disable_resources=False,
                                os_randomize=False,
                                timeout=120000,
                                load_dom=True,
                                page_action=wait_for_reload
                            )
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            page = await loop.run_in_executor(executor, fetch_search)
                        
                        # Check if we got an AWS WAF challenge page that wasn't solved
                        page_html = page.html if hasattr(page, 'html') else str(page)
                        if 'aws-waf-token' in page_html.lower() or 'challenge-container' in page_html.lower():
                            logger.warning(f"AWS WAF challenge still present on {search_url} after waiting")
                            logger.info("AWS WAF challenges may require:")
                            logger.info("  - Official API access (recommended)")
                            logger.info("  - Residential IP addresses")
                            logger.info("  - Non-headless browser mode")
                            logger.info("  - Additional wait time or manual intervention")
                            # Skip this URL and try the next one
                            continue
                        
                        # Check if page loaded successfully (not a 404 or challenge page)
                        # Try multiple selectors to find content on the page
                        # StubHub may have changed their page structure
                        test_selectors = [
                            'a[href*="/event/"]',
                            'a[data-testid*="event"]',
                            '[class*="event"]',
                            '[class*="Event"]',
                            'a[href*="-tickets-"]',
                            '[data-testid*="performer"]',
                            '[class*="EventCard"]',
                            'main',  # Any main content
                            '#content',  # Content div
                        ]
                        
                        page_has_content = False
                        for selector in test_selectors:
                            try:
                                elements = page.css(selector)
                                if elements and len(elements) > 0:
                                    page_has_content = True
                                    logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                                    break
                            except Exception as e:
                                logger.debug(f"Selector '{selector}' failed: {e}")
                        
                        if page_has_content:
                            search_page = page
                            successful_url = search_url
                            logger.info(f"Successfully loaded page: {search_url}")
                            break
                        else:
                            logger.info(f"Page loaded but no content found: {search_url}")
                            # Log a sample of the HTML for debugging
                            logger.debug(f"Page HTML sample: {page_html[:500]}")
                    except Exception as e:
                        logger.debug(f"Failed to load {search_url}: {e}")
                        continue
                
                if not search_page:
                    logger.warning(f"Could not bypass AWS WAF protection for: {search_query}")
                    return {
                        'status': 'error',
                        'platform': 'stubhub',
                        'url': search_urls[0],
                        'listings': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat(),
                        'scraper': 'scrapling',
                        'error': f'AWS WAF protection blocked access to StubHub for "{search_query}"',
                        'message': 'StubHub uses AWS WAF which blocks automated browsers. Consider using their official API for production use.',
                        'recommendations': [
                            'Use StubHub Official API (recommended)',
                            'Try with residential IP addresses',
                            'Use official partnership programs',
                            'Contact StubHub for API access'
                        ]
                    }
                
                # Find event links on the page
                # Try multiple selectors to find event links
                event_link_selectors = [
                    'a[href*="/event/"]',
                    'a[data-testid*="event"]',
                    '.eventCard a',
                    '.event-card a',
                    '[class*="EventCard"] a',
                    'a[href*="-tickets-"]',
                    'a[href*="/performer/"]'
                ]
                
                event_links = []
                for selector in event_link_selectors:
                    try:
                        links = search_page.css(selector)
                        if links:
                            event_links.extend(links)
                            logger.info(f"Found {len(links)} event links with selector '{selector}'")
                    except Exception as e:
                        logger.debug(f"Selector '{selector}' failed: {e}")
                
                if not event_links:
                    logger.warning(f"No event links found for: {search_query}")
                    # If we can't find event links, this might actually be an event page already
                    # Let's try to scrape it as an event page
                    logger.info("Attempting to scrape the page as an event page directly")
                    event_url = successful_url
                else:
                    # Get the first event URL
                    first_event = event_links[0]
                    event_href = first_event.attrib.get('href', '')
                    
                    # Handle relative URLs
                    if event_href.startswith('/'):
                        event_url = f'https://www.stubhub.com{event_href}'
                    elif event_href.startswith('http'):
                        event_url = event_href
                    else:
                        logger.warning(f"Invalid event URL format: {event_href}")
                        # Try to use the page we loaded as the event page
                        event_url = successful_url
                    
                    logger.info(f"Found event URL: {event_url}")
            
            # Step 2: Scrape ticket listings from event page
            logger.info(f"Scraping tickets from event page: {event_url}")
            
            def fetch_event():
                # Use stealth capabilities without solve_cloudflare for AWS WAF
                # AWS WAF challenges need more time to load, not automated solving
                return StealthyFetcher.fetch(
                    event_url,
                    headless=True,
                    solve_cloudflare=False,  # Don't try to solve Cloudflare challenges - AWS WAF is different
                    google_search=False,
                    network_idle=True,
                    wait=15000,  # Wait 15 seconds for ticket listings to load (milliseconds)
                    humanize=True,  # Humanize cursor movement
                    disable_resources=False,  # Ensure all page resources load
                    os_randomize=False,
                    timeout=60000  # Increase timeout to 60 seconds
                )
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                event_page = await loop.run_in_executor(executor, fetch_event)
            
            # Extract ticket listings from event page
            # StubHub ticket listings have specific selectors
            if adaptive:
                listing_elements = event_page.css(
                    '[data-testid*="ticket"], [data-testid*="listing"], .ticket-card, .listing-row, .inventory-listing',
                    adaptive=True
                )
            else:
                listing_elements = event_page.css(
                    '[data-testid*="ticket"], [data-testid*="listing"], .ticket-card, .listing-row, .inventory-listing',
                    auto_save=True
                )
            
            # Extract data from ticket listings
            listings = []
            for element in listing_elements:
                try:
                    # Extract price - try multiple selectors
                    price_element = element.css_first(
                        '[data-testid*="price"], [class*="price"], .price, .Price, span[class*="Price"]'
                    )
                    price_text = price_element.text if price_element else None
                    
                    if price_text:
                        # Clean price - remove $, commas, "each", etc.
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                            
                            # Extract section
                            section_element = element.css_first(
                                '[data-testid*="section"], [class*="section"], .section, .Section'
                            )
                            section = section_element.text.strip() if section_element else ''
                            
                            # Extract row
                            row_element = element.css_first(
                                '[data-testid*="row"], [class*="row"], .row, .Row'
                            )
                            row = row_element.text.strip() if row_element else ''
                            
                            # Extract quantity
                            qty_element = element.css_first(
                                '[data-testid*="quantity"], [class*="quantity"], .quantity, .Quantity'
                            )
                            if qty_element:
                                qty_text = qty_element.text
                                quantity = int(''.join(filter(str.isdigit, qty_text)) or '1')
                            else:
                                quantity = 1
                            
                            listings.append({
                                'price': price,
                                'section': section,
                                'row': row,
                                'quantity': quantity,
                                'platform': 'stubhub'
                            })
                except Exception as e:
                    logger.debug(f"Error parsing ticket listing: {e}")
                    continue
            
            logger.info(f"StubHub: Found {len(listings)} ticket listings")
            
            return {
                'status': 'success',
                'platform': 'stubhub',
                'url': event_url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
                'scraper': 'scrapling'
            }
            
        except Exception as e:
            logger.error(f"StubHub scraping error: {e}", exc_info=True)
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
        """
        Scrape SeatGeek using Scrapling
        
        Two-step process:
        1. If no event_url provided, search for events and find the first matching event URL
        2. Navigate to event page and scrape actual ticket listings
        """
        try:
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            # Step 1: Find event URL if not provided
            if not event_url:
                if not search_query:
                    return {
                        'status': 'error',
                        'platform': 'seatgeek',
                        'error': 'Either event_url or search_query must be provided',
                        'listings': [],
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Search for events on SeatGeek
                encoded_query = urllib.parse.quote(search_query)
                
                # Try multiple URL formats for SeatGeek
                performer_slug = search_query.lower().replace(' ', '-')
                search_urls = [
                    f'https://seatgeek.com/{performer_slug}-tickets',
                    f'https://seatgeek.com/search?q={encoded_query}',
                ]
                
                logger.info(f"Searching SeatGeek for: {search_query}")
                
                search_page = None
                successful_url = None
                
                for search_url in search_urls:
                    try:
                        logger.info(f"Trying URL: {search_url}")
                        
                        def fetch_search():
                            # Use stealth capabilities without solve_cloudflare
                            # Rely on stealth mode and longer wait time
                            return StealthyFetcher.fetch(
                                search_url,
                                headless=True,
                                solve_cloudflare=False,
                                google_search=False,
                                network_idle=True,
                                wait=15000,  # Wait 15 seconds for dynamic content (milliseconds)
                                humanize=True,
                                disable_resources=False,
                                os_randomize=False,
                                timeout=60000
                            )
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            page = await loop.run_in_executor(executor, fetch_search)
                        
                        # Check if page loaded successfully
                        test_links = page.css('a[href*="/event/"], a[href*="-tickets-"]')
                        if test_links:
                            search_page = page
                            successful_url = search_url
                            logger.info(f"Successfully loaded page with events: {search_url}")
                            break
                        else:
                            logger.info(f"Page loaded but no events found: {search_url}")
                    except Exception as e:
                        logger.debug(f"Failed to load {search_url}: {e}")
                        continue
                
                if not search_page:
                    logger.warning(f"Could not load any SeatGeek page for: {search_query}")
                    return {
                        'status': 'success',
                        'platform': 'seatgeek',
                        'url': search_urls[0],
                        'listings': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat(),
                        'scraper': 'scrapling',
                        'message': f'Could not find events page for "{search_query}"'
                    }
                
                # Find event links on the page
                event_links = search_page.css('a[href*="/event/"], a[href*="-tickets-"], .event-card a, .EventCard a')
                
                if not event_links:
                    logger.warning(f"No event links found for: {search_query}")
                    return {
                        'status': 'success',
                        'platform': 'seatgeek',
                        'url': successful_url,
                        'listings': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat(),
                        'scraper': 'scrapling',
                        'message': f'No events found for "{search_query}"'
                    }
                
                # Get the first event URL
                first_event = event_links[0]
                event_href = first_event.attrib.get('href', '')
                
                # Handle relative URLs
                if event_href.startswith('/'):
                    event_url = f'https://seatgeek.com{event_href}'
                elif event_href.startswith('http'):
                    event_url = event_href
                else:
                    logger.warning(f"Invalid event URL format: {event_href}")
                    return {
                        'status': 'error',
                        'platform': 'seatgeek',
                        'error': f'Could not find valid event URL for "{search_query}"',
                        'listings': [],
                        'timestamp': datetime.now().isoformat()
                    }
                
                logger.info(f"Found event URL: {event_url}")
            
            # Step 2: Scrape ticket listings from event page
            logger.info(f"Scraping tickets from event page: {event_url}")
            
            def fetch_event():
                # Use stealth capabilities without solve_cloudflare
                return StealthyFetcher.fetch(
                    event_url,
                    headless=True,
                    solve_cloudflare=False,
                    google_search=False,
                    network_idle=True,
                    wait=15000,  # Wait 15 seconds (milliseconds)
                    humanize=True,
                    disable_resources=False,
                    os_randomize=False,
                    timeout=60000
                )
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                event_page = await loop.run_in_executor(executor, fetch_event)
            
            # Extract ticket listings from event page
            # SeatGeek ticket listings have specific selectors
            if adaptive:
                listing_elements = event_page.css(
                    '[data-testid*="listing"], .listing, .ticket-listing, [class*="TicketListing"]',
                    adaptive=True
                )
            else:
                listing_elements = event_page.css(
                    '[data-testid*="listing"], .listing, .ticket-listing, [class*="TicketListing"]',
                    auto_save=True
                )
            
            listings = []
            for element in listing_elements:
                try:
                    price_element = element.css_first(
                        '[data-testid*="price"], [class*="price"], .price, .Price'
                    )
                    
                    if price_element and price_element.text:
                        # Clean price
                        price_text = price_element.text
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                            
                            # Extract section
                            section_element = element.css_first(
                                '[data-testid*="section"], [class*="section"], .section, .Section'
                            )
                            section = section_element.text.strip() if section_element else ''
                            
                            # Extract row
                            row_element = element.css_first(
                                '[data-testid*="row"], [class*="row"], .row, .Row'
                            )
                            row = row_element.text.strip() if row_element else ''
                            
                            listings.append({
                                'price': price,
                                'section': section,
                                'row': row,
                                'platform': 'seatgeek'
                            })
                except Exception as e:
                    logger.debug(f"Error parsing listing: {e}")
                    continue
            
            logger.info(f"SeatGeek: Found {len(listings)} ticket listings")
            
            return {
                'status': 'success',
                'platform': 'seatgeek',
                'url': event_url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
                'scraper': 'scrapling'
            }
            
        except Exception as e:
            logger.error(f"SeatGeek scraping error: {e}", exc_info=True)
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
            
            # Run in thread pool
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            def fetch_sync():
                return StealthyFetcher.fetch(url, headless=True, network_idle=True)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                page = await loop.run_in_executor(executor, fetch_sync)
            
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
            
            # Run in thread pool
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            def fetch_sync():
                return StealthyFetcher.fetch(url, headless=True, network_idle=True)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                page = await loop.run_in_executor(executor, fetch_sync)
            
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
