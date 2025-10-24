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
    service = await get_scraping_service()
    return await service.scrape_marketplace(
        marketplace=marketplace,
        search_query=search_query,
        event_url=event_url,
        adaptive=adaptive
    )
