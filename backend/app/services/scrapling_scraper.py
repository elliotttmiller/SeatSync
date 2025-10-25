"""
Scrapling-Powered Web Scraping Service - Production Ready
Modern, fully-featured scraping with all advanced capabilities enabled by default.

This service provides enterprise-grade web scraping with:
- Full stealth mode (TLS fingerprinting, OS randomization, WebGL/WebRTC)
- Adaptive element tracking (survives website structure changes automatically)
- Anti-bot detection bypass (Cloudflare, DataDome, AWS WAF)
- 685x faster parsing than traditional methods
- Concurrent multi-marketplace scraping
- Human behavior simulation
- Network idle detection
"""

import logging
import time
import asyncio
import re
import urllib.parse
from typing import Dict, List, Any, Optional
from datetime import datetime

from scrapling.fetchers import StealthyFetcher

logger = logging.getLogger(__name__)

# Supported marketplaces
MARKETPLACES = ("stubhub", "seatgeek", "ticketmaster", "vividseats")

# Configuration - all advanced features enabled
STEALTH_CONFIG = {
    "headless": True,
    "network_idle": True,
    "humanize": True,
    "disable_resources": False,  # Load all resources for realistic behavior
    "os_randomize": True,  # Randomize OS fingerprints
    "allow_webgl": True,  # Enable WebGL for realistic fingerprint
    "block_webrtc": False,  # Allow WebRTC for realistic fingerprint
    "google_search": True,  # Simulate Google referer
    "timeout": 150000,  # 150 seconds
    "load_dom": True,  # Wait for full DOM load
}

# AWS WAF specific configuration
AWS_WAF_CONFIG = {
    "wait_time": 30,  # seconds to wait for AWS WAF challenge
    "retry_attempts": 3,
    "retry_delay": 5,
}


class ScraplingScraperService:
    """
    Production-ready scraping service powered by Scrapling.
    All advanced features enabled by default - no optional parameters.
    """
    
    def __init__(self):
        self.initialized = True
        self.scraper_type = "scrapling"
        logger.info("✅ Scrapling scraper initialized with full stealth mode")
    
    async def scrape_marketplace(
        self,
        marketplace: str,
        search_query: Optional[str] = None,
        event_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scrape a marketplace using Scrapling with all advanced features.
        
        Args:
            marketplace: Marketplace name (stubhub, seatgeek, ticketmaster, vividseats)
            search_query: Search term for events
            event_url: Direct URL to event page
            
        Returns:
            Dictionary with scraping results
        """
        try:
            marketplace_lower = marketplace.lower()
            
            if marketplace_lower == 'stubhub':
                return await self._scrape_stubhub(event_url, search_query)
            elif marketplace_lower == 'seatgeek':
                return await self._scrape_seatgeek(event_url, search_query)
            elif marketplace_lower == 'ticketmaster':
                return await self._scrape_ticketmaster(event_url, search_query)
            elif marketplace_lower == 'vividseats':
                return await self._scrape_vividseats(event_url, search_query)
            else:
                return {
                    'status': 'error',
                    'platform': marketplace_lower,
                    'listings': [],
                    'error': f'Unsupported marketplace: {marketplace}',
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Scraping error for {marketplace}: {e}", exc_info=True)
            return {
                'status': 'error',
                'platform': marketplace.lower(),
                'listings': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def scrape_all_marketplaces(
        self,
        search_query: Optional[str] = None,
        event_url: Optional[str] = None,
        marketplaces: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape all marketplaces concurrently with full stealth mode.
        
        Args:
            search_query: Search term for events
            event_url: Direct URL to event page
            marketplaces: Optional list of marketplaces (defaults to all)
            
        Returns:
            Aggregated results from all marketplaces
        """
        marketplaces_to_scrape = marketplaces if marketplaces else list(MARKETPLACES)
        
        # Initialize tracking
        per_marketplace_results = {}
        all_listings = []
        successful_count = 0
        failed_count = 0
        errors = []
        
        # Concurrent scraping with semaphore (limit to 4 parallel)
        semaphore = asyncio.Semaphore(4)
        
        async def scrape_with_semaphore(marketplace: str):
            async with semaphore:
                try:
                    logger.info(f"Scraping {marketplace} with full stealth mode...")
                    result = await self.scrape_marketplace(
                        marketplace=marketplace,
                        search_query=search_query,
                        event_url=event_url,
                    )
                    return marketplace, result
                except Exception as e:
                    logger.error(f"Exception scraping {marketplace}: {e}", exc_info=True)
                    return marketplace, {
                        'status': 'error',
                        'platform': marketplace.lower(),
                        'listings': [],
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
        
        # Launch all scraping tasks concurrently
        tasks = [scrape_with_semaphore(mp) for mp in marketplaces_to_scrape]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for item in results:
            if isinstance(item, Exception):
                failed_count += 1
                errors.append(f"Exception: {str(item)}")
                logger.error(f"Unexpected exception: {item}", exc_info=True)
            else:
                marketplace, result = item
                per_marketplace_results[marketplace] = result
                
                if result.get('status') == 'success':
                    successful_count += 1
                    marketplace_listings = result.get('listings', [])
                    all_listings.extend(marketplace_listings)
                    logger.info(f"✅ {marketplace}: {len(marketplace_listings)} listings")
                else:
                    failed_count += 1
                    error_msg = result.get('error', 'Unknown error')
                    errors.append(f"{marketplace}: {error_msg}")
                    logger.warning(f"❌ {marketplace}: {error_msg}")
        
        # Determine overall status
        total_marketplaces = len(marketplaces_to_scrape)
        if successful_count == 0:
            overall_status = 'error'
        elif failed_count == 0:
            overall_status = 'success'
        else:
            overall_status = 'partial'
        
        result = {
            'status': overall_status,
            'total_listings': len(all_listings),
            'listings': all_listings,
            'per_marketplace': per_marketplace_results,
            'summary': {
                'successful': successful_count,
                'failed': failed_count,
                'total': total_marketplaces,
                'errors': errors if errors else None,
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Multi-marketplace scrape complete: {successful_count}/{total_marketplaces} successful, {len(all_listings)} total listings")
        
        return result
    
    async def _scrape_stubhub(
        self,
        event_url: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scrape StubHub with full stealth mode and AWS WAF bypass"""
        try:
            # Find event URL if not provided
            if not event_url:
                if not search_query:
                    return {
                        'status': 'error',
                        'platform': 'stubhub',
                        'error': 'Either event_url or search_query must be provided',
                        'listings': [],
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Search for events
                performer_slug = search_query.lower().replace(' ', '-')
                search_urls = [
                    f'https://www.stubhub.com/{performer_slug}-tickets',
                    f'https://www.stubhub.com/find?q={urllib.parse.quote(search_query)}',
                ]
                
                logger.info(f"Searching StubHub for: {search_query}")
                
                search_page = None
                successful_url = None
                
                for search_url in search_urls:
                    for attempt in range(AWS_WAF_CONFIG["retry_attempts"]):
                        try:
                            logger.info(f"Trying URL: {search_url} (Attempt {attempt + 1}/{AWS_WAF_CONFIG['retry_attempts']})")
                            
                            def fetch_search():
                                def wait_for_reload(page):
                                    time.sleep(AWS_WAF_CONFIG["wait_time"])
                                    logger.info(f"Waited {AWS_WAF_CONFIG['wait_time']}s for AWS WAF challenge")
                                
                                return StealthyFetcher.fetch(
                                    search_url,
                                    **STEALTH_CONFIG,
                                    solve_cloudflare=False,
                                    wait=10000,
                                    page_action=wait_for_reload,
                                )
                            
                            page = await asyncio.to_thread(fetch_search)
                            
                            # Check for AWS WAF challenge
                            page_html = page.html if hasattr(page, 'html') else str(page)
                            if 'aws-waf-token' not in page_html.lower() and 'challenge-container' not in page_html.lower():
                                # Check for content
                                test_selectors = [
                                    'a[href*="/event/"]',
                                    'a[data-testid*="event"]',
                                    '[class*="event"]',
                                    'main',
                                ]
                                
                                for selector in test_selectors:
                                    try:
                                        elements = page.css(selector)
                                        if elements and len(elements) > 0:
                                            search_page = page
                                            successful_url = search_url
                                            logger.info(f"✅ Successfully loaded page: {search_url}")
                                            break
                                    except Exception:
                                        continue
                                
                                if search_page:
                                    break
                            
                            if attempt < AWS_WAF_CONFIG["retry_attempts"] - 1:
                                await asyncio.sleep(AWS_WAF_CONFIG["retry_delay"])
                                
                        except Exception as e:
                            if attempt < AWS_WAF_CONFIG["retry_attempts"] - 1:
                                await asyncio.sleep(AWS_WAF_CONFIG["retry_delay"])
                            else:
                                logger.debug(f"All attempts failed for {search_url}: {e}")
                    
                    if search_page:
                        break
                
                if not search_page:
                    return {
                        'status': 'error',
                        'platform': 'stubhub',
                        'listings': [],
                        'error': f'AWS WAF blocked access after {AWS_WAF_CONFIG["retry_attempts"]} attempts',
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Find event links
                event_link_selectors = [
                    'a[href*="/event/"]',
                    'a[data-testid*="event"]',
                    'a[href*="-tickets-"]',
                ]
                
                event_links = []
                for selector in event_link_selectors:
                    try:
                        links = search_page.css(selector)
                        if links:
                            event_links.extend(links)
                    except Exception:
                        continue
                
                if event_links:
                    first_event = event_links[0]
                    event_href = first_event.attrib.get('href', '')
                    if event_href.startswith('/'):
                        event_url = f'https://www.stubhub.com{event_href}'
                    elif event_href.startswith('http'):
                        event_url = event_href
                    else:
                        event_url = successful_url
                else:
                    event_url = successful_url
            
            # Scrape ticket listings
            logger.info(f"Scraping tickets from: {event_url}")
            
            def fetch_event():
                def wait_for_tickets(page):
                    time.sleep(AWS_WAF_CONFIG["wait_time"])
                
                return StealthyFetcher.fetch(
                    event_url,
                    **STEALTH_CONFIG,
                    solve_cloudflare=False,
                    wait=10000,
                    page_action=wait_for_tickets,
                )
            
            event_page = await asyncio.to_thread(fetch_event)
            
            # Extract listings with adaptive tracking
            listing_elements = event_page.css(
                '[data-testid*="ticket"], [data-testid*="listing"], .ticket-card, .listing-row',
                adaptive=True
            )
            
            listings = []
            for element in listing_elements:
                try:
                    price_element = element.css_first('[data-testid*="price"], [class*="price"], .price')
                    price_text = price_element.text if price_element else None
                    
                    if price_text:
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                            
                            section_element = element.css_first('[data-testid*="section"], .section')
                            section = section_element.text.strip() if section_element else ''
                            
                            row_element = element.css_first('[data-testid*="row"], .row')
                            row = row_element.text.strip() if row_element else ''
                            
                            qty_element = element.css_first('[data-testid*="quantity"], .quantity')
                            quantity = 1
                            if qty_element:
                                qty_text = qty_element.text
                                quantity = int(''.join(filter(str.isdigit, qty_text)) or '1')
                            
                            listings.append({
                                'price': price,
                                'section': section,
                                'row': row,
                                'quantity': quantity,
                                'platform': 'stubhub'
                            })
                except Exception as e:
                    logger.debug(f"Error parsing listing: {e}")
            
            logger.info(f"StubHub: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'stubhub',
                'url': event_url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
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
    ) -> Dict[str, Any]:
        """Scrape SeatGeek with full stealth mode"""
        try:
            # Find event URL if not provided
            if not event_url:
                if not search_query:
                    return {
                        'status': 'error',
                        'platform': 'seatgeek',
                        'error': 'Either event_url or search_query must be provided',
                        'listings': [],
                        'timestamp': datetime.now().isoformat()
                    }
                
                performer_slug = search_query.lower().replace(' ', '-')
                search_urls = [
                    f'https://seatgeek.com/{performer_slug}-tickets',
                    f'https://seatgeek.com/search?q={urllib.parse.quote(search_query)}',
                ]
                
                logger.info(f"Searching SeatGeek for: {search_query}")
                
                for search_url in search_urls:
                    try:
                        def fetch_search():
                            return StealthyFetcher.fetch(search_url, **STEALTH_CONFIG, wait=15000)
                        
                        page = await asyncio.to_thread(fetch_search)
                        
                        test_links = page.css('a[href*="/event/"], a[href*="-tickets-"]')
                        if test_links:
                            event_links = page.css('a[href*="/event/"], a[href*="-tickets-"]')
                            if event_links:
                                first_event = event_links[0]
                                event_href = first_event.attrib.get('href', '')
                                
                                if event_href.startswith('/'):
                                    event_url = f'https://seatgeek.com{event_href}'
                                elif event_href.startswith('http'):
                                    event_url = event_href
                                else:
                                    continue
                                
                                logger.info(f"Found event URL: {event_url}")
                                break
                    except Exception as e:
                        logger.debug(f"Failed to load {search_url}: {e}")
                        continue
                
                if not event_url:
                    return {
                        'status': 'success',
                        'platform': 'seatgeek',
                        'listings': [],
                        'count': 0,
                        'message': f'No events found for "{search_query}"',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Scrape ticket listings
            logger.info(f"Scraping tickets from: {event_url}")
            
            def fetch_event():
                return StealthyFetcher.fetch(event_url, **STEALTH_CONFIG, wait=15000)
            
            event_page = await asyncio.to_thread(fetch_event)
            
            # Extract listings with adaptive tracking
            listing_elements = event_page.css(
                '[data-testid*="listing"], .listing, .ticket-listing',
                adaptive=True
            )
            
            listings = []
            for element in listing_elements:
                try:
                    price_element = element.css_first('[data-testid*="price"], [class*="price"], .price')
                    
                    if price_element and price_element.text:
                        price_text = price_element.text
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            price = float(price_match.group())
                            
                            section_element = element.css_first('[data-testid*="section"], .section')
                            section = section_element.text.strip() if section_element else ''
                            
                            row_element = element.css_first('[data-testid*="row"], .row')
                            row = row_element.text.strip() if row_element else ''
                            
                            listings.append({
                                'price': price,
                                'section': section,
                                'row': row,
                                'platform': 'seatgeek'
                            })
                except Exception as e:
                    logger.debug(f"Error parsing listing: {e}")
            
            logger.info(f"SeatGeek: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'seatgeek',
                'url': event_url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
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
    ) -> Dict[str, Any]:
        """Scrape Ticketmaster with full stealth mode"""
        try:
            url = event_url or f'https://www.ticketmaster.com/search?q={search_query or "sports"}'
            logger.info(f"Scraping Ticketmaster: {url}")
            
            def fetch_sync():
                return StealthyFetcher.fetch(url, **STEALTH_CONFIG)
            
            page = await asyncio.to_thread(fetch_sync)
            
            listing_elements = page.css(
                '[data-testid="event-card"], .event-card, .offer',
                adaptive=True
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
            
            logger.info(f"Ticketmaster: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'ticketmaster',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
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
    ) -> Dict[str, Any]:
        """Scrape Vivid Seats with full stealth mode"""
        try:
            url = event_url or f'https://www.vividseats.com/search?search={search_query or "sports"}'
            logger.info(f"Scraping Vivid Seats: {url}")
            
            def fetch_sync():
                return StealthyFetcher.fetch(url, **STEALTH_CONFIG)
            
            page = await asyncio.to_thread(fetch_sync)
            
            listing_elements = page.css(
                '[data-testid="listing"], .listing, .productionListItem',
                adaptive=True
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
            
            logger.info(f"Vivid Seats: Found {len(listings)} listings")
            
            return {
                'status': 'success',
                'platform': 'vividseats',
                'url': url,
                'listings': listings,
                'count': len(listings),
                'timestamp': datetime.now().isoformat(),
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


# Global instance
_scraper_service = None


async def get_scraper_service() -> ScraplingScraperService:
    """Get or create the global scraper service instance"""
    global _scraper_service
    
    if _scraper_service is None:
        _scraper_service = ScraplingScraperService()
    
    return _scraper_service


async def scrape_tickets(
    search_query: Optional[str] = None,
    event_url: Optional[str] = None,
    marketplaces: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Scrape tickets from marketplaces with full stealth mode.
    Always scrapes all marketplaces concurrently.
    
    Args:
        search_query: Search query string
        event_url: Direct event URL
        marketplaces: Optional list of marketplaces (defaults to all)
        
    Returns:
        Scraping results with per-marketplace breakdown
    """
    service = await get_scraper_service()
    return await service.scrape_all_marketplaces(
        search_query=search_query,
        event_url=event_url,
        marketplaces=marketplaces
    )
