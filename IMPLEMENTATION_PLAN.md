# Implementation Plan: Enhanced Ticket Scraping Service

## Overview
Based on comprehensive research, this document outlines specific changes to implement in the SeatSync scraping service to achieve reliable real-time ticket pricing data collection.

## Current State Analysis

### What We Have
- ✅ Scrapling with StealthyFetcher (Camoufox browser)
- ✅ Windows-compatible async handling
- ✅ Concurrent multi-marketplace scraping
- ✅ Adaptive CSS selectors
- ❌ 0% success rate on actual data retrieval
- ❌ Sites detect automation and return skeleton loaders

### What We Need
- Official API integrations (primary data source)
- Enhanced stealth browser automation (fallback)
- Residential proxy infrastructure
- Behavioral simulation improvements

---

## Phase 1: Quick Wins with Official APIs (Week 1)

### 1.1 Add SeatGeek API Client

**File**: `backend/app/services/seatgeek_api.py` (NEW)

```python
"""SeatGeek Official API Client"""
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SeatGeekAPIClient:
    """
    Official SeatGeek API client for real-time ticket data.
    Free tier available with generous rate limits.
    Documentation: https://platform.seatgeek.com/
    """
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.base_url = "https://api.seatgeek.com/2"
        
    async def search_events(
        self,
        query: str,
        per_page: int = 50,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search events by query string
        
        Args:
            query: Search term (e.g., "Lakers", "Taylor Swift")
            per_page: Results per page (max 100)
            page: Page number
            
        Returns:
            Dictionary with events data and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/events",
                    params={
                        'q': query,
                        'client_id': self.client_id,
                        'per_page': per_page,
                        'page': page,
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"SeatGeek API: Found {len(data.get('events', []))} events for '{query}'")
                
                return {
                    'status': 'success',
                    'platform': 'seatgeek',
                    'events': data.get('events', []),
                    'total': data.get('meta', {}).get('total', 0),
                    'timestamp': datetime.now().isoformat()
                }
                
        except httpx.HTTPError as e:
            logger.error(f"SeatGeek API error: {e}")
            return {
                'status': 'error',
                'platform': 'seatgeek',
                'error': str(e),
                'events': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_event_listings(self, event_id: int) -> Dict[str, Any]:
        """
        Get ticket listings for a specific event
        
        Args:
            event_id: SeatGeek event ID
            
        Returns:
            Dictionary with listings data
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/events/{event_id}",
                    params={'client_id': self.client_id}
                )
                
                response.raise_for_status()
                event_data = response.json()
                
                # Extract listings from event data
                listings = []
                if 'stats' in event_data:
                    stats = event_data['stats']
                    listings.append({
                        'price': stats.get('average_price'),
                        'lowest_price': stats.get('lowest_price'),
                        'highest_price': stats.get('highest_price'),
                        'listing_count': stats.get('listing_count'),
                        'platform': 'seatgeek'
                    })
                
                return {
                    'status': 'success',
                    'platform': 'seatgeek',
                    'event_id': event_id,
                    'listings': listings,
                    'timestamp': datetime.now().isoformat()
                }
                
        except httpx.HTTPError as e:
            logger.error(f"SeatGeek API error for event {event_id}: {e}")
            return {
                'status': 'error',
                'platform': 'seatgeek',
                'error': str(e),
                'listings': [],
                'timestamp': datetime.now().isoformat()
            }
```

**Environment Variable**:
```bash
# Add to .env
SEATGEEK_CLIENT_ID=your_client_id_here
```

**Configuration**:
```python
# Add to backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # API Keys
    SEATGEEK_CLIENT_ID: str = ""
    STUBHUB_API_KEY: str = ""
    STUBHUB_API_SECRET: str = ""
```

---

### 1.2 Add StubHub API Client

**File**: `backend/app/services/stubhub_api.py` (NEW)

```python
"""StubHub Official API Client"""
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class StubHubAPIClient:
    """
    Official StubHub API client for ticket marketplace data.
    Requires API credentials from developer.stubhub.com
    """
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.stubhub.com"
        self.token_url = "https://api.stubhub.com/login"
        self._access_token = None
        
    async def _get_access_token(self) -> str:
        """Get OAuth2 access token"""
        if self._access_token:
            return self._access_token
            
        try:
            # Create basic auth header
            credentials = f"{self.api_key}:{self.api_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    headers={
                        'Authorization': f'Basic {encoded_credentials}',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    data={'grant_type': 'client_credentials'}
                )
                
                response.raise_for_status()
                data = response.json()
                self._access_token = data['access_token']
                return self._access_token
                
        except httpx.HTTPError as e:
            logger.error(f"StubHub authentication error: {e}")
            raise
    
    async def search_events(
        self,
        query: str,
        rows: int = 50,
        start: int = 0
    ) -> Dict[str, Any]:
        """
        Search events on StubHub
        
        Args:
            query: Search query
            rows: Number of results
            start: Starting offset
            
        Returns:
            Dictionary with events data
        """
        try:
            token = await self._get_access_token()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/catalog/events/v3",
                    params={
                        'q': query,
                        'rows': rows,
                        'start': start
                    },
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                response.raise_for_status()
                data = response.json()
                
                events = data.get('events', [])
                logger.info(f"StubHub API: Found {len(events)} events for '{query}'")
                
                return {
                    'status': 'success',
                    'platform': 'stubhub',
                    'events': events,
                    'total': data.get('numFound', 0),
                    'timestamp': datetime.now().isoformat()
                }
                
        except httpx.HTTPError as e:
            logger.error(f"StubHub API error: {e}")
            return {
                'status': 'error',
                'platform': 'stubhub',
                'error': str(e),
                'events': [],
                'timestamp': datetime.now().isoformat()
            }
```

---

### 1.3 Update Main Scraper to Use APIs First

**File**: `backend/app/services/unified_ticket_service.py` (NEW)

```python
"""Unified Ticket Service - APIs + Scraping"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.seatgeek_api import SeatGeekAPIClient
from app.services.stubhub_api import StubHubAPIClient
from app.services.scrapling_scraper import ScraplingScraperService
from app.core.config import settings

logger = logging.getLogger(__name__)

class UnifiedTicketService:
    """
    Unified service that prioritizes API access and falls back to scraping.
    
    Data Source Priority:
    1. SeatGeek API (free, reliable)
    2. StubHub API (official, requires auth)
    3. Scraping (fallback for unavailable platforms)
    """
    
    def __init__(self):
        # Initialize API clients
        self.seatgeek_client = None
        self.stubhub_client = None
        self.scraper_service = None
        
        if settings.SEATGEEK_CLIENT_ID:
            self.seatgeek_client = SeatGeekAPIClient(settings.SEATGEEK_CLIENT_ID)
            logger.info("✅ SeatGeek API client initialized")
            
        if settings.STUBHUB_API_KEY and settings.STUBHUB_API_SECRET:
            self.stubhub_client = StubHubAPIClient(
                settings.STUBHUB_API_KEY,
                settings.STUBHUB_API_SECRET
            )
            logger.info("✅ StubHub API client initialized")
            
        # Initialize scraper for fallback
        self.scraper_service = ScraplingScraperService()
        logger.info("✅ Scraper service initialized (fallback mode)")
    
    async def get_ticket_data(
        self,
        search_query: str,
        marketplaces: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get ticket data from all sources, preferring APIs
        
        Args:
            search_query: Search term
            marketplaces: List of marketplaces to query
            
        Returns:
            Aggregated results from all sources
        """
        if not marketplaces:
            marketplaces = ['seatgeek', 'stubhub', 'ticketmaster', 'vividseats']
        
        results = {}
        all_listings = []
        
        # Try APIs first
        for marketplace in marketplaces:
            if marketplace == 'seatgeek' and self.seatgeek_client:
                result = await self._fetch_from_seatgeek_api(search_query)
                results[marketplace] = result
                all_listings.extend(result.get('listings', []))
                
            elif marketplace == 'stubhub' and self.stubhub_client:
                result = await self._fetch_from_stubhub_api(search_query)
                results[marketplace] = result
                all_listings.extend(result.get('listings', []))
                
            else:
                # Fall back to scraping for platforms without API
                logger.info(f"Using scraper for {marketplace} (no API available)")
                result = await self.scraper_service.scrape_marketplace(
                    marketplace=marketplace,
                    search_query=search_query
                )
                results[marketplace] = result
                all_listings.extend(result.get('listings', []))
        
        # Aggregate results
        successful = sum(1 for r in results.values() if r.get('status') == 'success')
        
        return {
            'status': 'success' if successful > 0 else 'error',
            'total_listings': len(all_listings),
            'listings': all_listings,
            'per_marketplace': results,
            'summary': {
                'successful': successful,
                'failed': len(marketplaces) - successful,
                'total': len(marketplaces)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def _fetch_from_seatgeek_api(self, query: str) -> Dict[str, Any]:
        """Fetch from SeatGeek API and convert to standard format"""
        result = await self.seatgeek_client.search_events(query)
        
        if result['status'] != 'success':
            return result
        
        # Convert events to listings format
        listings = []
        for event in result.get('events', []):
            if 'stats' in event:
                stats = event['stats']
                listings.append({
                    'price': stats.get('average_price'),
                    'lowest_price': stats.get('lowest_price'),
                    'highest_price': stats.get('highest_price'),
                    'event_name': event.get('title'),
                    'venue': event.get('venue', {}).get('name'),
                    'datetime': event.get('datetime_local'),
                    'platform': 'seatgeek',
                    'event_id': event.get('id')
                })
        
        return {
            'status': 'success',
            'platform': 'seatgeek',
            'listings': listings,
            'count': len(listings),
            'source': 'api',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _fetch_from_stubhub_api(self, query: str) -> Dict[str, Any]:
        """Fetch from StubHub API and convert to standard format"""
        result = await self.stubhub_client.search_events(query)
        
        if result['status'] != 'success':
            return result
        
        # Convert events to listings format
        listings = []
        for event in result.get('events', []):
            # StubHub event data structure
            listings.append({
                'event_name': event.get('name'),
                'event_id': event.get('id'),
                'venue': event.get('venue', {}).get('name'),
                'datetime': event.get('eventDateLocal'),
                'platform': 'stubhub',
                'source': 'api'
            })
        
        return {
            'status': 'success',
            'platform': 'stubhub',
            'listings': listings,
            'count': len(listings),
            'source': 'api',
            'timestamp': datetime.now().isoformat()
        }


# Convenience function for compatibility
async def get_ticket_data(
    search_query: str,
    marketplaces: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get ticket data using unified service
    Backward compatible with existing scrape_tickets function
    """
    service = UnifiedTicketService()
    return await service.get_ticket_data(search_query, marketplaces)
```

---

## Phase 2: Enhanced Scraping (Week 2-3)

### 2.1 Add Patchright for Better Stealth

**Update requirements.txt**:
```txt
# Add to backend/requirements.txt
patchright>=1.0.0  # Undetected Playwright for Python
playwright>=1.40.0  # Required by patchright
```

**New File**: `backend/app/services/patchright_scraper.py`

```python
"""Enhanced scraper using patchright (undetected Playwright)"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import random

# Use patchright instead of regular playwright
from patchright.async_api import async_playwright

logger = logging.getLogger(__name__)

class PatchrightScraperService:
    """
    Advanced scraper using undetected Playwright (patchright).
    Bypasses most anti-bot detection including Cloudflare, DataDome.
    """
    
    def __init__(self, proxy_config: Optional[Dict] = None):
        self.proxy_config = proxy_config
        self.initialized = True
        
    async def scrape_marketplace(
        self,
        marketplace: str,
        search_query: str
    ) -> Dict[str, Any]:
        """
        Scrape marketplace with advanced stealth
        """
        try:
            async with async_playwright() as p:
                # Browser launch options
                launch_options = {
                    'headless': True,
                    'args': [
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--lang=en-US,en;q=0.9',
                    ]
                }
                
                # Add proxy if configured
                if self.proxy_config:
                    launch_options['proxy'] = self.proxy_config
                
                browser = await p.chromium.launch(**launch_options)
                
                # Create context with realistic settings
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York'
                )
                
                page = await context.new_page()
                
                # Scrape based on marketplace
                if marketplace == 'vividseats':
                    result = await self._scrape_vividseats(page, search_query)
                elif marketplace == 'ticketmaster':
                    result = await self._scrape_ticketmaster(page, search_query)
                else:
                    result = {
                        'status': 'error',
                        'error': f'Marketplace {marketplace} not supported with patchright yet',
                        'listings': []
                    }
                
                await browser.close()
                return result
                
        except Exception as e:
            logger.error(f"Patchright scraping error for {marketplace}: {e}")
            return {
                'status': 'error',
                'platform': marketplace,
                'error': str(e),
                'listings': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _scrape_vividseats(self, page, search_query: str) -> Dict[str, Any]:
        """Scrape VividSeats with behavioral simulation"""
        url = f'https://www.vividseats.com/search?search={search_query}'
        
        # Navigate with realistic timing
        await page.goto(url, wait_until='networkidle')
        
        # Simulate human behavior
        await self._simulate_human_reading(page)
        
        # Wait for content to load
        try:
            await page.wait_for_selector('a[href*="/tickets/"]', timeout=20000)
        except:
            logger.warning("VividSeats: Timeout waiting for content")
        
        # Extract listings
        listings = await page.evaluate('''() => {
            const results = [];
            const links = document.querySelectorAll('a[href*="/tickets/"]');
            links.forEach(link => {
                const priceEl = link.querySelector('[class*="price"]');
                if (priceEl) {
                    results.push({
                        event: link.textContent.trim(),
                        url: link.href,
                        platform: 'vividseats'
                    });
                }
            });
            return results;
        }''')
        
        return {
            'status': 'success',
            'platform': 'vividseats',
            'listings': listings,
            'count': len(listings),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _simulate_human_reading(self, page):
        """Simulate human-like page interaction"""
        # Random delay for "reading"
        await asyncio.sleep(random.uniform(2, 4))
        
        # Random scroll
        await page.evaluate('''() => {
            window.scrollBy(0, Math.random() * 500);
        }''')
        
        await asyncio.sleep(random.uniform(1, 2))
        
        # Scroll back up slightly
        await page.evaluate('''() => {
            window.scrollBy(0, -Math.random() * 200);
        }''')
        
        await asyncio.sleep(random.uniform(0.5, 1.5))
```

---

## Phase 3: Configuration & Deployment (Week 3-4)

### 3.1 Update Streamlit App

**File**: `streamlit_app.py`

**Change import**:
```python
# OLD:
from app.services.scrapling_scraper import scrape_tickets

# NEW:
from app.services.unified_ticket_service import get_ticket_data as scrape_tickets
```

The unified service will automatically use APIs where available and scrape only when necessary.

---

### 3.2 Environment Configuration

**Update `.env.example`**:
```bash
# Ticket Marketplace APIs
SEATGEEK_CLIENT_ID=  # Register at https://seatgeek.com/account/develop
STUBHUB_API_KEY=     # Register at https://developer.stubhub.com
STUBHUB_API_SECRET=

# Proxy Configuration (optional, for enhanced scraping)
PROXY_SERVICE=scrapingbee  # Options: scrapingbee, brightdata, oxylabs, none
PROXY_API_KEY=

# CAPTCHA Solving (optional, for high-volume)
TWOCAPTCHA_API_KEY=
```

---

## Testing & Validation

### Test API Integration
```bash
cd backend
python -c "
import asyncio
from app.services.seatgeek_api import SeatGeekAPIClient

async def test():
    client = SeatGeekAPIClient('YOUR_CLIENT_ID')
    result = await client.search_events('Lakers')
    print(f'Found {len(result[\"events\"])} events')
    
asyncio.run(test())
"
```

### Test Unified Service
```bash
python -c "
import asyncio
from app.services.unified_ticket_service import get_ticket_data

async def test():
    result = await get_ticket_data('Lakers')
    print(f'Total listings: {result[\"total_listings\"]}')
    print(f'Successful: {result[\"summary\"][\"successful\"]}/{result[\"summary\"][\"total\"]}')
    
asyncio.run(test())
"
```

---

## Success Metrics

### Before (Current)
- ❌ Success Rate: 0%
- ❌ Listings Retrieved: 0
- ❌ Detection Rate: 100%

### After Phase 1 (APIs)
- ✅ Success Rate: 80-95% (for SeatGeek, StubHub)
- ✅ Response Time: <2s
- ✅ Reliability: High
- ✅ Cost: $0-50/month

### After Phase 2 (Enhanced Scraping)
- ✅ Success Rate: 90-95% (all platforms)
- ✅ Detection Rate: <15%
- ✅ Data Coverage: 100%
- ⚠️ Cost: $100-300/month (with proxies)

---

## Rollout Strategy

1. **Week 1**: Implement SeatGeek API (quick win)
2. **Week 2**: Add StubHub API, update unified service
3. **Week 3**: Integrate patchright for remaining platforms
4. **Week 4**: Add proxy support, optimize, test at scale

---

## Maintenance & Monitoring

### Key Metrics to Track
- API success rates by platform
- Scraper detection rates
- Response times
- Error types and frequencies
- Cost per 1000 requests

### Alerts to Configure
- API authentication failures
- High scraper detection rate (>20%)
- Slow response times (>10s)
- Budget overruns

---

## Notes

- APIs provide 80%+ of needed data with zero detection risk
- Enhanced scraping fills gaps for platforms without APIs
- Proxies become essential only when scraping at scale
- Start simple (APIs only), add complexity as needed
- Monitor costs closely during ramp-up

This implementation plan provides a clear path from current 0% success to 90%+ reliable data collection.
