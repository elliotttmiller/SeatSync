"""
Unified Scraping Service - Scrapling-Powered
Provides a clean, simple interface for all ticket scraping operations

This service uses Scrapling exclusively for modern, adaptive web scraping:
- Adaptive element tracking (survives website changes)
- Built-in Cloudflare bypass
- TLS fingerprint impersonation
- 685x faster parsing than BeautifulSoup
- Superior anti-bot detection
"""

import logging
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


# Canonical list of supported marketplaces
MARKETPLACES = ("stubhub", "seatgeek", "ticketmaster", "vividseats")


# Fix Windows asyncio issue
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        logger.info("Windows asyncio policy set")
    except Exception as e:
        logger.warning(f"Could not set Windows asyncio policy: {e}")


class ScrapingService:
    """
    Scrapling-powered scraping service
    Modern, adaptive web scraping with superior performance
    """
    
    def __init__(self):
        self.scraper = None
        self.scraper_type = "scrapling"
        self.initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize Scrapling scraper
        """
        if self.initialized:
            return True
        
        try:
            from .scrapling_service import get_scrapling_service, SCRAPLING_AVAILABLE
            
            if not SCRAPLING_AVAILABLE:
                logger.error("Scrapling not available. Install with: pip install 'scrapling[all]>=0.3.7' && scrapling install")
                return False
            
            logger.info("Initializing Scrapling scraper...")
            self.scraper = await get_scrapling_service()
            self.scraper_type = "scrapling"
            self.initialized = True
            logger.info("✅ Scrapling scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Scrapling scraper: {e}")
            logger.error("Install Scrapling with: pip install 'scrapling[all]>=0.3.7' && scrapling install")
            return False
    
    async def scrape_marketplace(
        self,
        marketplace: str,
        search_query: Optional[str] = None,
        event_url: Optional[str] = None,
        adaptive: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape a marketplace using Scrapling
        
        Args:
            marketplace: Name of marketplace (stubhub, seatgeek, etc)
            search_query: Search term for events
            event_url: Direct URL to event page
            adaptive: Use adaptive element tracking (True if website structure changed)
            
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
                'error': 'Failed to initialize Scrapling. Install with: pip install "scrapling[all]>=0.3.7" && scrapling install',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Use Scrapling service
            result = await self.scraper.scrape_marketplace(
                marketplace=marketplace,
                search_query=search_query,
                event_url=event_url,
                adaptive=adaptive
            )
            
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
    
    async def scrape_all_marketplaces(
        self,
        search_query: Optional[str] = None,
        event_url: Optional[str] = None,
        adaptive: bool = False,
        marketplaces: Optional[List[str]] = None,
        concurrent: bool = True,
        max_concurrent: int = 4
    ) -> Dict[str, Any]:
        """
        Scrape all marketplaces and return aggregated results
        
        Args:
            search_query: Search term for events
            event_url: Direct URL to event page (applied to all marketplaces)
            adaptive: Use adaptive element tracking
            marketplaces: Optional list of marketplaces to scrape (defaults to all)
            concurrent: Whether to scrape concurrently (default: True for better performance)
            max_concurrent: Maximum concurrent scrapes (default: 4)
            
        Returns:
            Dictionary with aggregated results including:
            - status: overall status
            - total_listings: combined count
            - listings: flattened array of all listings
            - per_marketplace: individual results for each marketplace
            - summary: metadata about statuses, counts, errors
        """
        # Ensure initialization
        if not self.initialized:
            await self.initialize()
        
        if not self.initialized:
            return {
                'status': 'error',
                'total_listings': 0,
                'listings': [],
                'per_marketplace': {},
                'summary': {
                    'error': 'Failed to initialize scraping service',
                    'successful': 0,
                    'failed': 0,
                    'total': 0
                },
                'timestamp': datetime.now().isoformat()
            }
        
        # Use provided marketplaces or default to all
        marketplaces_to_scrape = marketplaces if marketplaces else list(MARKETPLACES)
        
        # Initialize result tracking
        per_marketplace_results = {}
        all_listings = []
        successful_count = 0
        failed_count = 0
        errors = []
        
        if concurrent:
            # Concurrent scraping with semaphore to limit parallel requests
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def scrape_with_semaphore(marketplace: str):
                """Scrape a single marketplace with semaphore control"""
                async with semaphore:
                    try:
                        logger.info(f"Scraping {marketplace}...")
                        result = await self.scrape_marketplace(
                            marketplace=marketplace,
                            search_query=search_query,
                            event_url=event_url,
                            adaptive=adaptive
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
                    # Handle unexpected exceptions from asyncio.gather
                    failed_count += 1
                    error_msg = str(item)
                    errors.append(f"Exception during scraping: {error_msg}")
                    logger.error(f"Unexpected exception: {item}", exc_info=True)
                else:
                    marketplace, result = item
                    per_marketplace_results[marketplace] = result
                    
                    # Track success/failure
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
        else:
            # Sequential scraping (original implementation)
            for marketplace in marketplaces_to_scrape:
                try:
                    logger.info(f"Scraping {marketplace}...")
                    result = await self.scrape_marketplace(
                        marketplace=marketplace,
                        search_query=search_query,
                        event_url=event_url,
                        adaptive=adaptive
                    )
                    
                    per_marketplace_results[marketplace] = result
                    
                    # Track success/failure
                    if result.get('status') == 'success':
                        successful_count += 1
                        # Add listings to combined array
                        marketplace_listings = result.get('listings', [])
                        all_listings.extend(marketplace_listings)
                        logger.info(f"✅ {marketplace}: {len(marketplace_listings)} listings")
                    else:
                        failed_count += 1
                        error_msg = result.get('error', 'Unknown error')
                        errors.append(f"{marketplace}: {error_msg}")
                        logger.warning(f"❌ {marketplace}: {error_msg}")
                        
                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    errors.append(f"{marketplace}: {error_msg}")
                    logger.error(f"Exception scraping {marketplace}: {e}", exc_info=True)
                    
                    # Store error result
                    per_marketplace_results[marketplace] = {
                        'status': 'error',
                        'platform': marketplace.lower(),
                        'listings': [],
                        'error': error_msg,
                        'timestamp': datetime.now().isoformat()
                    }
        
        # Determine overall status
        total_marketplaces = len(marketplaces_to_scrape)
        if successful_count == 0:
            overall_status = 'error'
        elif failed_count == 0:
            overall_status = 'success'
        else:
            overall_status = 'partial'
        
        # Build aggregated result
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
                'concurrent': concurrent
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Multi-marketplace scrape complete ({'concurrent' if concurrent else 'sequential'}): {successful_count}/{total_marketplaces} successful, {len(all_listings)} total listings")
        
        return result
    
    async def cleanup(self):
        """Clean up resources"""
        if self.scraper and hasattr(self.scraper, 'cleanup'):
            try:
                await self.scraper.cleanup()
                logger.info("Scraper cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        self.initialized = False
        self.scraper = None
        self.scraper_type = None
    
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
            'adaptive_tracking',      # Survives website changes!
            'cloudflare_bypass',      # Built-in Cloudflare bypass
            'tls_fingerprinting',     # Browser impersonation
            'fast_parsing',           # 685x faster than BeautifulSoup
            'javascript_rendering',
            'anti_detection',
            'human_simulation'
        ]


# Global instance
_scraping_service = None


async def get_scraping_service() -> ScrapingService:
    """Get or create the global scraping service instance"""
    global _scraping_service
    
    if _scraping_service is None:
        _scraping_service = ScrapingService()
        await _scraping_service.initialize()
    
    return _scraping_service


async def scrape_tickets(
    marketplace: Optional[str] = None,
    search_query: Optional[str] = None,
    event_url: Optional[str] = None,
    adaptive: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for quick scraping with Scrapling
    
    Args:
        marketplace: Marketplace name (stubhub, seatgeek, ticketmaster, vividseats).
                    Pass None, "all", or "*" to scrape all marketplaces.
        search_query: Search query string
        event_url: Direct event URL
        adaptive: Use adaptive element tracking (True if website structure changed)
        
    Returns:
        Scraping results dictionary. For multi-marketplace, includes per_marketplace breakdown.
    """
    service = await get_scraping_service()
    
    # Check if we should scrape all marketplaces
    if marketplace is None or marketplace.lower() in ("all", "*"):
        return await service.scrape_all_marketplaces(
            search_query=search_query,
            event_url=event_url,
            adaptive=adaptive
        )
    else:
        # Single marketplace scrape
        return await service.scrape_marketplace(
            marketplace=marketplace,
            search_query=search_query,
            event_url=event_url,
            adaptive=adaptive
        )
