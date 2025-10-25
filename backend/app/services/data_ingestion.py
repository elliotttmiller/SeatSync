"""
Advanced Data Ingestion Pipeline for SeatSync
Ticket Price Scraping & Collection Focus

This service provides sophisticated web scraping capabilities for real-time
ticket price collection from major marketplaces without relying on APIs.

Primary Focus:
- Advanced web scraping from ticket marketplaces
- Real-time price data collection and normalization
- Intelligent scraping with anti-bot detection bypassing
- High-frequency data ingestion and processing

Secondary (Minimal):
- Basic context data for predictions (optional)
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import json
import aiohttp
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, and_, desc, text

from app.core.config import settings
from app.models.database import MarketData, SentimentData, SeasonTicket, Listing

logger = logging.getLogger(__name__)

class AdvancedDataPipeline:
    """
    High-performance data ingestion pipeline focused on ticket price scraping
    
    Uses advanced web scraping techniques to collect real-time ticket prices
    from all major marketplaces without relying on public APIs.
    """
    
    def __init__(self):
        # Initialize advanced web scraper (lazy loading)
        self._advanced_scraper = None
        
        # Keep minimal API-based scrapers as fallback (deprecated in favor of web scraping)
        self.marketplace_scrapers = {
            'seatgeek': SeatGeekScraper(),
            'ticketmaster': TicketmasterScraper(),
            'vivid_seats': VividSeatsScraper()
        }
        
        # Feature engineers for processing scraped data
        self.feature_engineers = {
            'market': MarketFeatureEngineer(),
            'temporal': TemporalFeatureEngineer(),
            'external': ExternalFeatureEngineer()
        }
    
    async def get_advanced_scraper(self):
        """Get or initialize the advanced web scraper"""
        if self._advanced_scraper is None:
            try:
                from app.services.advanced_ticket_scraper import get_advanced_scraper
                self._advanced_scraper = await get_advanced_scraper()
            except Exception as e:
                logger.warning(f"Advanced scraper not available: {e}")
                self._advanced_scraper = None
        return self._advanced_scraper
        
    async def real_time_data_stream(self, db: AsyncSession) -> AsyncGenerator[Dict[str, Any], None]:
        """
        High-frequency data ingestion with focus on ticket price scraping
        Yields processed data in real-time for immediate use
        """
        while True:
            try:
                # PRIMARY: Advanced web scraping from marketplaces
                primary_task = self._collect_marketplace_data_advanced()
                
                # SECONDARY: Minimal context data (optional)
                # Only collect if needed for predictions
                secondary_tasks = []
                if getattr(settings, 'ENABLE_CONTEXT_DATA', False):
                    secondary_tasks.append(self._collect_minimal_context())
                
                # Execute primary scraping task
                primary_result = await primary_task
                
                # Process and yield primary data
                if primary_result and not isinstance(primary_result, Exception):
                    # Real-time feature engineering focused on price data
                    features = await self._engineer_features(primary_result)
                    
                    # Store in database
                    await self._bulk_insert_data(db, features)
                    
                    yield {
                        'timestamp': datetime.utcnow().isoformat(),
                        'data_type': 'marketplace_scraped',
                        'features': features,
                        'status': 'processed',
                        'listings_count': len(primary_result.get('listings', []))
                    }
                
                # Process secondary data if available
                if secondary_tasks:
                    secondary_results = await asyncio.gather(*secondary_tasks, return_exceptions=True)
                    for result in secondary_results:
                        if result and not isinstance(result, Exception):
                            features = await self._engineer_features(result)
                            await self._bulk_insert_data(db, features)
                
                # Sleep before next scraping iteration
                await asyncio.sleep(getattr(settings, 'SCRAPING_INTERVAL', 60))
                
            except Exception as e:
                logger.error(f"Error in data stream: {e}")
                yield {
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': str(e),
                    'status': 'error'
                }
                await asyncio.sleep(120)  # Wait longer on error
    
    async def _collect_marketplace_data_advanced(self) -> Dict[str, Any]:
        """
        PRIMARY DATA COLLECTION: Advanced web scraping from all marketplaces
        
        Uses sophisticated scraping techniques to extract real-time ticket prices
        from marketplace websites without relying on APIs.
        """
        try:
            # Try to use advanced Playwright-based scraper first
            advanced_scraper = await self.get_advanced_scraper()
            
            if advanced_scraper:
                logger.info("Using advanced web scraper for marketplace data")
                
                # Scrape all marketplaces
                result = await advanced_scraper.scrape_all_marketplaces(
                    search_query=getattr(settings, 'DEFAULT_SEARCH_QUERY', 'sports')
                )
                
                return {
                    'type': 'marketplace',
                    'method': 'advanced_scraping',
                    'timestamp': datetime.utcnow(),
                    'platforms': result.get('platforms', {}),
                    'listings': result.get('listings', []),
                    'total_count': result.get('total_listings', 0)
                }
            else:
                # Fallback to API-based scrapers (legacy)
                logger.info("Advanced scraper not available, using fallback API scrapers")
                return await self._collect_marketplace_data_fallback()
                
        except Exception as e:
            logger.error(f"Advanced marketplace scraping error: {e}")
            # Try fallback
            return await self._collect_marketplace_data_fallback()
    
    async def _collect_marketplace_data_fallback(self) -> Dict[str, Any]:
        """Fallback: Use API-based scrapers if advanced scraping fails"""
        try:
            tasks = []
            for platform, scraper in self.marketplace_scrapers.items():
                if scraper.is_enabled():
                    tasks.append(scraper.collect_listings())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            marketplace_data = {
                'type': 'marketplace',
                'method': 'api_fallback',
                'timestamp': datetime.utcnow(),
                'platforms': {}
            }
            
            for i, (platform, scraper) in enumerate(self.marketplace_scrapers.items()):
                if i < len(results) and not isinstance(results[i], Exception):
                    marketplace_data['platforms'][platform] = results[i]
            
            return marketplace_data
            
        except Exception as e:
            logger.error(f"Marketplace fallback collection error: {e}")
            return {'type': 'marketplace', 'error': str(e)}
    
    async def _collect_minimal_context(self) -> Dict[str, Any]:
        """
        SECONDARY: Collect minimal context data for predictions
        
        Only basic data needed to enhance price predictions.
        NOT focused on team stats or detailed sports data.
        """
        try:
            context_data = {
                'type': 'context',
                'timestamp': datetime.utcnow(),
                'data': {}
            }
            
            # Only collect what's absolutely necessary for price prediction
            # - Basic event timing info
            # - Minimal external factors
            
            return context_data
            
        except Exception as e:
            logger.error(f"Context data collection error: {e}")
            return {'type': 'context', 'error': str(e)}
    
    async def _engineer_features(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply feature engineering to raw data focused on marketplace prices"""
        try:
            features = {}
            data_type = raw_data.get('type', 'unknown')
            
            # Apply appropriate feature engineering based on data type
            if data_type == 'marketplace':
                features.update(await self.feature_engineers['market'].process(raw_data))
            elif data_type in ['context', 'external']:
                features.update(await self.feature_engineers['external'].process(raw_data))
            
            # Always apply temporal features
            features.update(await self.feature_engineers['temporal'].process(raw_data))
            
            return features
            
        except Exception as e:
            logger.error(f"Feature engineering error: {e}")
            return {}
    
    async def _bulk_insert_data(self, db: AsyncSession, features: Dict[str, Any]) -> None:
        """Efficient bulk insertion into TimescaleDB"""
        try:
            # Prepare data for bulk insert
            insert_data = {
                'id': features.get('id', str(datetime.utcnow().timestamp())),
                'team': features.get('team', ''),
                'opponent': features.get('opponent', ''),
                'game_date': features.get('game_date', datetime.utcnow()),
                'data_type': features.get('data_type', 'processed'),
                'data': features,
                'created_at': datetime.utcnow()
            }
            
            # Use bulk insert for performance
            await db.execute(
                insert(MarketData).values(insert_data)
            )
            await db.commit()
            
        except Exception as e:
            logger.error(f"Bulk insert error: {e}")
            await db.rollback()
    
    async def _invalidate_stale_cache(self) -> None:
        """Invalidate stale cache entries"""
        # Implement cache invalidation logic
        pass


class BaseScraper:
    """Base class for marketplace scrapers"""
    
    def __init__(self):
        self.enabled = True
        self.rate_limit = 10  # requests per minute
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    async def collect_listings(self) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError


class SeatGeekScraper(BaseScraper):
    """
    SeatGeek API integration for real-time ticket data collection
    Uses SeatGeek's public API for event and pricing data
    """
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('SEATGEEK_CLIENT_ID', '')
        self.client_secret = os.getenv('SEATGEEK_CLIENT_SECRET', '')
        self.base_url = 'https://api.seatgeek.com/2'
        self.enabled = bool(self.client_id)
    
    async def collect_listings(self) -> Dict[str, Any]:
        """
        Collect real-time ticket listings from SeatGeek
        Returns event data with comprehensive pricing information
        """
        try:
            if not self.enabled:
                logger.info("SeatGeek scraper not enabled - API credentials not configured")
                return {
                    'platform': 'seatgeek',
                    'listings': [],
                    'timestamp': datetime.utcnow(),
                    'status': 'disabled'
                }
            
            async with httpx.AsyncClient() as client:
                # Search for sports events
                params = {
                    'client_id': self.client_id,
                    'type': 'sports',  # Focus on sports events
                    'per_page': 100,
                    'datetime_utc.gte': datetime.utcnow().isoformat(),  # Future events
                    'sort': 'datetime_utc.asc'
                }
                
                response = await client.get(
                    f'{self.base_url}/events',
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    events = data.get('events', [])
                    
                    # Parse listings from events
                    listings = []
                    for event in events:
                        listing = self._parse_seatgeek_event(event)
                        if listing:
                            listings.append(listing)
                    
                    logger.info(f"SeatGeek: Collected {len(listings)} listings from {len(events)} events")
                    
                    return {
                        'platform': 'seatgeek',
                        'listings': listings,
                        'event_count': len(events),
                        'timestamp': datetime.utcnow(),
                        'status': 'success',
                        'meta': data.get('meta', {})
                    }
                else:
                    logger.warning(f"SeatGeek API returned status {response.status_code}")
                    return {
                        'platform': 'seatgeek',
                        'listings': [],
                        'timestamp': datetime.utcnow(),
                        'status': 'api_error',
                        'error_code': response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"SeatGeek scraper error: {e}")
            return {
                'platform': 'seatgeek',
                'listings': [],
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }
    
    def _parse_seatgeek_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a SeatGeek event into normalized listing format"""
        try:
            stats = event.get('stats', {})
            
            return {
                'event_id': event.get('id'),
                'title': event.get('title'),
                'datetime': event.get('datetime_utc'),
                'venue': event.get('venue', {}).get('name'),
                'city': event.get('venue', {}).get('city'),
                'state': event.get('venue', {}).get('state'),
                'performers': [p.get('name') for p in event.get('performers', [])],
                'price_lowest': float(stats.get('lowest_price', 0)),
                'price_average': float(stats.get('average_price', 0)),
                'price_highest': float(stats.get('highest_price', 0)),
                'listing_count': int(stats.get('listing_count', 0)),
                'median_price': float(stats.get('median_price', 0)),
                'score': float(event.get('score', 0)),
                'popularity': float(event.get('popularity', 0)),
                'timestamp': datetime.utcnow().isoformat(),
                'url': event.get('url')
            }
        except Exception as e:
            logger.debug(f"Error parsing SeatGeek event: {e}")
            return None


class TicketmasterScraper(BaseScraper):
    """
    Ticketmaster API integration for real-time ticket data collection
    Uses Ticketmaster's Discovery API for comprehensive event data
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('TICKETMASTER_API_KEY', '')
        self.base_url = 'https://app.ticketmaster.com/discovery/v2'
        self.enabled = bool(self.api_key)
    
    async def collect_listings(self) -> Dict[str, Any]:
        """
        Collect real-time event and pricing data from Ticketmaster
        Returns comprehensive event information with pricing
        """
        try:
            if not self.enabled:
                logger.info("Ticketmaster scraper not enabled - API key not configured")
                return {
                    'platform': 'ticketmaster',
                    'listings': [],
                    'timestamp': datetime.utcnow(),
                    'status': 'disabled'
                }
            
            async with httpx.AsyncClient() as client:
                # Search for sports events
                params = {
                    'apikey': self.api_key,
                    'classificationName': 'Sports',
                    'size': 100,
                    'sort': 'date,asc'
                }
                
                response = await client.get(
                    f'{self.base_url}/events.json',
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    embedded = data.get('_embedded', {})
                    events = embedded.get('events', [])
                    
                    # Parse events into listings
                    listings = []
                    for event in events:
                        listing = self._parse_ticketmaster_event(event)
                        if listing:
                            listings.append(listing)
                    
                    logger.info(f"Ticketmaster: Collected {len(listings)} listings from {len(events)} events")
                    
                    return {
                        'platform': 'ticketmaster',
                        'listings': listings,
                        'event_count': len(events),
                        'timestamp': datetime.utcnow(),
                        'status': 'success',
                        'page': data.get('page', {})
                    }
                else:
                    logger.warning(f"Ticketmaster API returned status {response.status_code}")
                    return {
                        'platform': 'ticketmaster',
                        'listings': [],
                        'timestamp': datetime.utcnow(),
                        'status': 'api_error',
                        'error_code': response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"Ticketmaster scraper error: {e}")
            return {
                'platform': 'ticketmaster',
                'listings': [],
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }
    
    def _parse_ticketmaster_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a Ticketmaster event into normalized listing format"""
        try:
            # Extract pricing information
            price_ranges = event.get('priceRanges', [{}])[0]
            
            # Extract venue information
            venues = event.get('_embedded', {}).get('venues', [{}])
            venue = venues[0] if venues else {}
            
            # Extract classification
            classifications = event.get('classifications', [{}])
            classification = classifications[0] if classifications else {}
            
            return {
                'event_id': event.get('id'),
                'name': event.get('name'),
                'date': event.get('dates', {}).get('start', {}).get('dateTime'),
                'venue_name': venue.get('name'),
                'city': venue.get('city', {}).get('name'),
                'state': venue.get('state', {}).get('stateCode'),
                'country': venue.get('country', {}).get('countryCode'),
                'sport': classification.get('segment', {}).get('name'),
                'genre': classification.get('genre', {}).get('name'),
                'price_min': float(price_ranges.get('min', 0)),
                'price_max': float(price_ranges.get('max', 0)),
                'currency': price_ranges.get('currency', 'USD'),
                'status': event.get('dates', {}).get('status', {}).get('code'),
                'sales_start': event.get('sales', {}).get('public', {}).get('startDateTime'),
                'sales_end': event.get('sales', {}).get('public', {}).get('endDateTime'),
                'timestamp': datetime.utcnow().isoformat(),
                'url': event.get('url')
            }
        except Exception as e:
            logger.debug(f"Error parsing Ticketmaster event: {e}")
            return None


class VividSeatsScraper(BaseScraper):
    """
    Vivid Seats scraping integration
    Note: Vivid Seats doesn't have a public API, so this uses web scraping
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.vividseats.com'
        self.enabled = os.getenv('ENABLE_VIVIDSEATS_SCRAPING', 'false').lower() == 'true'
    
    async def collect_listings(self) -> Dict[str, Any]:
        """
        Collect ticket listings from Vivid Seats
        Uses web scraping as no public API is available
        """
        try:
            if not self.enabled:
                logger.info("Vivid Seats scraper not enabled")
                return {
                    'platform': 'vivid_seats',
                    'listings': [],
                    'timestamp': datetime.utcnow(),
                    'status': 'disabled',
                    'note': 'Web scraping requires explicit enablement'
                }
            
            # For MVP, return placeholder
            # In production, implement with Playwright/Selenium for JS-heavy site
            logger.info("Vivid Seats: Placeholder implementation")
            
            return {
                'platform': 'vivid_seats',
                'listings': [],
                'timestamp': datetime.utcnow(),
                'status': 'not_implemented',
                'note': 'Requires browser automation (Playwright/Selenium) for full implementation'
            }
            
        except Exception as e:
            logger.error(f"Vivid Seats scraper error: {e}")
            return {
                'platform': 'vivid_seats',
                'listings': [],
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }


class BaseAPI:
    """Base class for sports APIs"""
    
    def __init__(self):
        self.enabled = True
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError


class SportradarAPI(BaseAPI):
    """
    Sportradar API integration for professional sports data
    Provides comprehensive coverage of major sports leagues
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('SPORTRADAR_API_KEY', '')
        self.base_url = 'https://api.sportradar.us'
        self.enabled = bool(self.api_key)
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current sports data from Sportradar"""
        try:
            if not self.enabled:
                logger.info("Sportradar API not enabled - API key not configured")
                return {
                    'source': 'sportradar',
                    'data': {},
                    'timestamp': datetime.utcnow(),
                    'status': 'disabled'
                }
            
            # Get data from multiple sports
            data = {}
            sports = ['nba', 'nfl', 'mlb', 'nhl']
            
            async with httpx.AsyncClient() as client:
                for sport in sports:
                    try:
                        sport_data = await self._get_sport_data(client, sport)
                        if sport_data:
                            data[sport] = sport_data
                    except Exception as e:
                        logger.debug(f"Failed to get {sport} data: {e}")
            
            return {
                'source': 'sportradar',
                'data': data,
                'timestamp': datetime.utcnow(),
                'status': 'success' if data else 'no_data'
            }
        except Exception as e:
            logger.error(f"Sportradar API error: {e}")
            return {
                'source': 'sportradar',
                'data': {},
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_sport_data(self, client: httpx.AsyncClient, sport: str) -> Dict[str, Any]:
        """Get data for a specific sport"""
        # Sportradar endpoints vary by sport
        endpoints = {
            'nba': f'{self.base_url}/nba/trial/v8/en/games/schedule.json',
            'nfl': f'{self.base_url}/nfl/official/trial/v7/en/games/schedule.json',
            'mlb': f'{self.base_url}/mlb/trial/v7/en/games/schedule.json',
            'nhl': f'{self.base_url}/nhl/trial/v8/en/games/schedule.json'
        }
        
        url = endpoints.get(sport)
        if not url:
            return {}
        
        params = {'api_key': self.api_key}
        
        response = await client.get(url, params=params, timeout=15.0)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.debug(f"Sportradar {sport} API error: {response.status_code}")
            return {}


class ESPNAPI(BaseAPI):
    """
    ESPN API integration for sports scores and team data
    Uses ESPN's public API (no key required for basic access)
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://site.api.espn.com/apis/site/v2/sports'
        self.enabled = True  # Public API, always available
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current sports data from ESPN"""
        try:
            data = {}
            
            # Sports endpoints in ESPN API
            sports = {
                'basketball/nba': 'nba',
                'football/nfl': 'nfl',
                'baseball/mlb': 'mlb',
                'hockey/nhl': 'nhl'
            }
            
            async with httpx.AsyncClient() as client:
                for espn_path, sport_key in sports.items():
                    try:
                        sport_data = await self._get_sport_scoreboard(client, espn_path)
                        if sport_data:
                            data[sport_key] = sport_data
                    except Exception as e:
                        logger.debug(f"Failed to get ESPN {sport_key} data: {e}")
            
            logger.info(f"ESPN: Collected data for {len(data)} sports")
            
            return {
                'source': 'espn',
                'data': data,
                'timestamp': datetime.utcnow(),
                'status': 'success' if data else 'no_data'
            }
        except Exception as e:
            logger.error(f"ESPN API error: {e}")
            return {
                'source': 'espn',
                'data': {},
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_sport_scoreboard(self, client: httpx.AsyncClient, sport_path: str) -> Dict[str, Any]:
        """Get scoreboard data for a specific sport"""
        try:
            url = f'{self.base_url}/{sport_path}/scoreboard'
            
            response = await client.get(url, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse and normalize the data
                events = data.get('events', [])
                
                return {
                    'events': events,
                    'leagues': data.get('leagues', []),
                    'season': data.get('season', {}),
                    'event_count': len(events)
                }
            else:
                logger.debug(f"ESPN {sport_path} API error: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.debug(f"Error getting ESPN scoreboard: {e}")
            return {}


class NBAAPI(BaseAPI):
    """
    NBA Official API integration using balldontlie or NBA stats API
    Provides detailed NBA statistics and game data
    """
    
    def __init__(self):
        super().__init__()
        # Using balldontlie.io as it's free and doesn't require key
        self.base_url = 'https://api.balldontlie.io/v1'
        self.api_key = os.getenv('BALLDONTLIE_API_KEY', '')
        self.enabled = True  # Free tier available
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current NBA data"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if self.api_key:
                    headers['Authorization'] = self.api_key
                
                # Get games
                games_url = f'{self.base_url}/games'
                params = {
                    'per_page': 100,
                    'start_date': datetime.utcnow().strftime('%Y-%m-%d')
                }
                
                response = await client.get(
                    games_url,
                    headers=headers,
                    params=params,
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    games_data = response.json()
                    
                    # Get teams data
                    teams_url = f'{self.base_url}/teams'
                    teams_response = await client.get(teams_url, headers=headers, timeout=15.0)
                    teams_data = teams_response.json() if teams_response.status_code == 200 else {}
                    
                    logger.info(f"NBA: Collected {len(games_data.get('data', []))} games")
                    
                    return {
                        'source': 'nba',
                        'data': {
                            'games': games_data.get('data', []),
                            'teams': teams_data.get('data', []),
                            'meta': games_data.get('meta', {})
                        },
                        'timestamp': datetime.utcnow(),
                        'status': 'success'
                    }
                else:
                    logger.debug(f"NBA API error: {response.status_code}")
                    return {
                        'source': 'nba',
                        'data': {},
                        'timestamp': datetime.utcnow(),
                        'status': 'api_error',
                        'error_code': response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"NBA API error: {e}")
            return {
                'source': 'nba',
                'data': {},
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }


class NFLAPI(BaseAPI):
    """
    NFL data integration using TheSportsDB or ESPN
    Provides NFL game schedules and team information
    """
    
    def __init__(self):
        super().__init__()
        # Using TheSportsDB free API
        self.base_url = 'https://www.thesportsdb.com/api/v1/json'
        self.api_key = os.getenv('THESPORTSDB_API_KEY', '3')  # Free tier key
        self.enabled = True
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current NFL data"""
        try:
            async with httpx.AsyncClient() as client:
                # Get NFL events
                events_url = f'{self.base_url}/{self.api_key}/eventsnextleague.php'
                params = {'id': '4391'}  # NFL league ID
                
                response = await client.get(events_url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    events_data = response.json()
                    events = events_data.get('events', [])
                    
                    logger.info(f"NFL: Collected {len(events)} upcoming games")
                    
                    return {
                        'source': 'nfl',
                        'data': {
                            'events': events,
                            'event_count': len(events)
                        },
                        'timestamp': datetime.utcnow(),
                        'status': 'success'
                    }
                else:
                    logger.debug(f"NFL API error: {response.status_code}")
                    return {
                        'source': 'nfl',
                        'data': {},
                        'timestamp': datetime.utcnow(),
                        'status': 'api_error'
                    }
                    
        except Exception as e:
            logger.error(f"NFL API error: {e}")
            return {
                'source': 'nfl',
                'data': {},
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }


class MLBAPI(BaseAPI):
    """
    MLB Official API integration
    Provides comprehensive MLB game and statistics data
    """
    
    def __init__(self):
        super().__init__()
        # MLB StatsAPI is free and public
        self.base_url = 'https://statsapi.mlb.com/api/v1'
        self.enabled = True
    
    async def get_current_data(self) -> Dict[str, Any]:
        """Get current MLB data"""
        try:
            async with httpx.AsyncClient() as client:
                # Get today's schedule
                schedule_url = f'{self.base_url}/schedule'
                params = {
                    'sportId': 1,  # MLB
                    'date': datetime.utcnow().strftime('%Y-%m-%d')
                }
                
                response = await client.get(schedule_url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    schedule_data = response.json()
                    dates = schedule_data.get('dates', [])
                    
                    games = []
                    for date_entry in dates:
                        games.extend(date_entry.get('games', []))
                    
                    # Get teams
                    teams_url = f'{self.base_url}/teams'
                    teams_response = await client.get(teams_url, params={'sportId': 1}, timeout=15.0)
                    teams_data = teams_response.json() if teams_response.status_code == 200 else {}
                    
                    logger.info(f"MLB: Collected {len(games)} games")
                    
                    return {
                        'source': 'mlb',
                        'data': {
                            'games': games,
                            'teams': teams_data.get('teams', []),
                            'schedule': schedule_data
                        },
                        'timestamp': datetime.utcnow(),
                        'status': 'success'
                    }
                else:
                    logger.debug(f"MLB API error: {response.status_code}")
                    return {
                        'source': 'mlb',
                        'data': {},
                        'timestamp': datetime.utcnow(),
                        'status': 'api_error'
                    }
                    
        except Exception as e:
            logger.error(f"MLB API error: {e}")
            return {
                'source': 'mlb',
                'data': {},
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }


class BaseSentimentAnalyzer:
    """Base class for sentiment analyzers"""
    
    def __init__(self):
        self.enabled = True
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    async def collect_sentiment(self) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError


class TwitterSentimentAnalyzer(BaseSentimentAnalyzer):
    """Twitter sentiment analysis"""
    
    async def collect_sentiment(self) -> Dict[str, Any]:
        try:
            # Implement Twitter API integration
            return {
                'source': 'twitter',
                'sentiment_data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Twitter sentiment error: {e}")
            return {}


class RedditSentimentAnalyzer(BaseSentimentAnalyzer):
    """Reddit sentiment analysis"""
    
    async def collect_sentiment(self) -> Dict[str, Any]:
        try:
            # Implement Reddit API integration
            return {
                'source': 'reddit',
                'sentiment_data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Reddit sentiment error: {e}")
            return {}


class NewsAnalyzer(BaseSentimentAnalyzer):
    """News sentiment analysis"""
    
    async def collect_sentiment(self) -> Dict[str, Any]:
        try:
            # Implement news API integration
            return {
                'source': 'news',
                'sentiment_data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"News sentiment error: {e}")
            return {}


class BaseFeatureEngineer:
    """Base class for feature engineers"""
    
    async def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError


class MarketFeatureEngineer(BaseFeatureEngineer):
    """Market-based feature engineering"""
    
    async def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process marketplace data into features"""
        try:
            features = {}
            
            if raw_data.get('type') != 'marketplace':
                return features
            
            platforms = raw_data.get('platforms', {})
            
            # Calculate aggregate market features
            all_listings = []
            for platform, data in platforms.items():
                listings = data.get('listings', [])
                all_listings.extend(listings)
            
            if all_listings:
                prices = [l.get('price', 0) for l in all_listings if l.get('price')]
                if prices:
                    features['market_avg_price'] = sum(prices) / len(prices)
                    features['market_min_price'] = min(prices)
                    features['market_max_price'] = max(prices)
                    features['market_price_std'] = (sum((p - features['market_avg_price'])**2 for p in prices) / len(prices)) ** 0.5
                    features['market_listing_count'] = len(all_listings)
                    features['market_price_range'] = features['market_max_price'] - features['market_min_price']
            
            return features
            
        except Exception as e:
            logger.error(f"Market feature engineering error: {e}")
            return {}


class TeamFeatureEngineer(BaseFeatureEngineer):
    """Team and sports-based feature engineering"""
    
    async def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sports data into features"""
        try:
            features = {}
            
            if raw_data.get('type') != 'sports':
                return features
            
            leagues = raw_data.get('leagues', {})
            
            # Process team performance data
            for league, data in leagues.items():
                league_data = data.get('data', {})
                
                # Extract team metrics
                if 'team_stats' in league_data:
                    features[f'{league.lower()}_team_rank'] = league_data['team_stats'].get('rank', 0)
                    features[f'{league.lower()}_win_rate'] = league_data['team_stats'].get('win_rate', 0.5)
                    features[f'{league.lower()}_recent_form'] = league_data['team_stats'].get('recent_form', 0)
            
            return features
            
        except Exception as e:
            logger.error(f"Team feature engineering error: {e}")
            return {}


class TemporalFeatureEngineer(BaseFeatureEngineer):
    """Time-based feature engineering"""
    
    async def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process temporal features"""
        try:
            features = {}
            
            timestamp = raw_data.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Extract temporal features
            features['hour_of_day'] = timestamp.hour
            features['day_of_week'] = timestamp.weekday()
            features['day_of_month'] = timestamp.day
            features['month'] = timestamp.month
            features['is_weekend'] = 1 if timestamp.weekday() >= 5 else 0
            features['is_business_hours'] = 1 if 9 <= timestamp.hour <= 17 else 0
            
            return features
            
        except Exception as e:
            logger.error(f"Temporal feature engineering error: {e}")
            return {}


class ExternalFeatureEngineer(BaseFeatureEngineer):
    """External context feature engineering"""
    
    async def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process external context data into features"""
        try:
            features = {}
            
            data_type = raw_data.get('type')
            
            if data_type == 'sentiment':
                # Process sentiment data
                sources = raw_data.get('sources', {})
                sentiments = []
                for source, data in sources.items():
                    sentiment_data = data.get('sentiment_data', {})
                    if 'score' in sentiment_data:
                        sentiments.append(sentiment_data['score'])
                
                if sentiments:
                    features['avg_sentiment'] = sum(sentiments) / len(sentiments)
                    features['sentiment_volatility'] = (sum((s - features['avg_sentiment'])**2 for s in sentiments) / len(sentiments)) ** 0.5
            
            elif data_type == 'external':
                # Process weather data
                weather = raw_data.get('weather', {})
                if weather:
                    features['weather_score'] = weather.get('score', 0.5)
                    features['temperature'] = weather.get('temperature', 70)
                
                # Process competing events
                events = raw_data.get('events', {})
                if events:
                    features['competing_events_count'] = events.get('count', 0)
                
                # Process news
                news = raw_data.get('news', {})
                if news:
                    features['news_mentions'] = news.get('mentions', 0)
            
            return features
            
        except Exception as e:
            logger.error(f"External feature engineering error: {e}")
            return {}