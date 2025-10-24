"""
Unified Scraping Service
Provides a clean, simple interface for all ticket scraping operations

This service:
- Auto-detects available scraping methods (Playwright vs HTTP vs Scrapling)
- Provides graceful fallbacks
- Handles initialization automatically
- Manages resource cleanup
- Provides consistent error handling
- Handles Windows-specific asyncio issues
- Supports feature flag for Scrapling (modern, adaptive scraping)
"""

import logging
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Feature flag for Scrapling - can be controlled via environment variable
USE_SCRAPLING = os.getenv('USE_SCRAPLING', 'false').lower() == 'true'


# Fix Windows asyncio issue with Playwright
if sys.platform == 'win32':
    try:
        # Set event loop policy for Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        logger.info("Windows asyncio policy set for Playwright compatibility")
    except Exception as e:
        logger.warning(f"Could not set Windows asyncio policy: {e}")


class ScrapingService:
    """
    Unified scraping service with automatic fallbacks
    """
    
    def __init__(self):
        self.scraper = None
        self.scraper_type = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the best available scraper
        Priority: Scrapling (if enabled) > Playwright > HTTP
        """
        if self.initialized:
            return True
        
        # Try Scrapling first if feature flag is enabled
        if USE_SCRAPLING:
            try:
                from .scrapling_service import get_scrapling_service, SCRAPLING_AVAILABLE
                
                if SCRAPLING_AVAILABLE:
                    logger.info("Initializing Scrapling-based scraper (modern, adaptive)...")
                    self.scraper = await get_scrapling_service()
                    self.scraper_type = "scrapling"
                    self.initialized = True
                    logger.info("✅ Scrapling scraper initialized successfully")
                    return True
                else:
                    logger.warning("Scrapling not available, falling back to Playwright")
            except Exception as e:
                logger.warning(f"Could not initialize Scrapling scraper: {e}")
        
        # Try Playwright-based scraper
        try:
            from .advanced_ticket_scraper import AdvancedTicketScraper, PLAYWRIGHT_AVAILABLE
            
            if PLAYWRIGHT_AVAILABLE:
                logger.info("Initializing Playwright-based scraper...")
                self.scraper = AdvancedTicketScraper()
                success = await self.scraper.initialize()
                
                if success:
                    self.scraper_type = "playwright"
                    self.initialized = True
                    logger.info("✅ Playwright scraper initialized successfully")
                    return True
                else:
                    logger.warning("Playwright scraper initialization failed")
        except Exception as e:
            logger.warning(f"Could not initialize Playwright scraper: {e}")
        
        # Fallback: Use HTTP-based scraper
        logger.info("Falling back to HTTP-based scraper...")
        try:
            from .enhanced_scraping import get_scraping_engine
            
            self.scraper = await get_scraping_engine()
            self.scraper_type = "http"
            self.initialized = True
            logger.info("✅ HTTP scraper initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize any scraper: {e}")
            return False
    
    async def scrape_marketplace(
        self,
        marketplace: str,
        search_query: Optional[str] = None,
        event_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape a marketplace with automatic fallback
        
        Args:
            marketplace: Name of marketplace (stubhub, seatgeek, etc)
            search_query: Search term for events
            event_url: Direct URL to event page
            
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
                'error': 'Failed to initialize any scraping method. Please install Playwright: pip install playwright && playwright install chromium',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            marketplace_lower = marketplace.lower()
            
            # Route to appropriate scraper method
            if self.scraper_type == "playwright":
                if marketplace_lower == 'stubhub':
                    result = await self.scraper.scrape_stubhub(
                        event_url=event_url,
                        search_query=search_query
                    )
                elif marketplace_lower == 'seatgeek':
                    result = await self.scraper.scrape_seatgeek(
                        event_url=event_url,
                        search_query=search_query
                    )
                elif marketplace_lower == 'ticketmaster':
                    result = await self.scraper.scrape_ticketmaster(
                        event_url=event_url,
                        search_query=search_query
                    )
                else:
                    result = {
                        'status': 'error',
                        'error': f'Unsupported marketplace: {marketplace}'
                    }
            else:
                # HTTP-based scraper
                # Note: HTTP scraper might have different capabilities
                result = {
                    'status': 'warning',
                    'platform': marketplace_lower,
                    'listings': [],
                    'message': 'HTTP scraper has limited capabilities. Install Playwright for full functionality.',
                    'timestamp': datetime.now().isoformat()
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
        
        if self.scraper_type == "playwright":
            return [
                'stubhub',
                'seatgeek',
                'ticketmaster',
                'javascript_rendering',
                'anti_detection',
                'human_simulation'
            ]
        else:
            return [
                'basic_http',
                'static_content'
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
    event_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for quick scraping
    
    Args:
        marketplace: Marketplace name (stubhub, seatgeek, ticketmaster)
        search_query: Search query string
        event_url: Direct event URL
        
    Returns:
        Scraping results dictionary
    """
    service = await get_scraping_service()
    return await service.scrape_marketplace(
        marketplace=marketplace,
        search_query=search_query,
        event_url=event_url
    )
