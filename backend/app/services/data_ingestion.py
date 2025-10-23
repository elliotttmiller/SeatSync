"""
Advanced Data Ingestion Pipeline for SeatSync Phase 1
AI Foundation & Data Pipeline Implementation

This service provides comprehensive data acquisition and processing capabilities including:
- Real-time marketplace data collection
- Sports data integration
- External context data (weather, news, social media)
- High-frequency data ingestion and processing
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
    """High-performance data ingestion and processing pipeline"""
    
    def __init__(self):
        self.marketplace_scrapers = {
            'stubhub': StubHubScraper(),
            'seatgeek': SeatGeekScraper(),
            'ticketmaster': TicketmasterScraper(),
            'vivid_seats': VividSeatsScraper()
        }
        self.sports_apis = {
            'sportradar': SportradarAPI(),
            'espn': ESPNAPI(),
            'nba': NBAAPI(),
            'nfl': NFLAPI(),
            'mlb': MLBAPI()
        }
        self.sentiment_analyzers = {
            'twitter': TwitterSentimentAnalyzer(),
            'reddit': RedditSentimentAnalyzer(),
            'news': NewsAnalyzer()
        }
        self.feature_engineers = {
            'market': MarketFeatureEngineer(),
            'team': TeamFeatureEngineer(),
            'temporal': TemporalFeatureEngineer(),
            'external': ExternalFeatureEngineer()
        }
        
    async def real_time_data_stream(self, db: AsyncSession) -> AsyncGenerator[Dict[str, Any], None]:
        """
        High-frequency data ingestion with parallel collection
        Yields processed data in real-time for immediate use
        """
        while True:
            try:
                # Parallel data collection from multiple sources
                tasks = [
                    self._collect_marketplace_data(),
                    self._collect_sports_data(),
                    self._collect_sentiment_data(),
                    self._collect_external_context()
                ]
                
                # Execute all data collection tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process and yield data
                for result in results:
                    if not isinstance(result, Exception) and result:
                        # Real-time feature engineering
                        features = await self._engineer_features(result)
                        
                        # Store in TimescaleDB with bulk inserts
                        await self._bulk_insert_data(db, features)
                        
                        yield {
                            'timestamp': datetime.utcnow().isoformat(),
                            'data_type': result.get('type', 'unknown'),
                            'features': features,
                            'status': 'processed'
                        }
                
                # Cache invalidation strategies
                await self._invalidate_stale_cache()
                
                # Sleep before next iteration (configurable)
                await asyncio.sleep(getattr(settings, 'DATA_COLLECTION_INTERVAL', 30))
                
            except Exception as e:
                logger.error(f"Error in data stream: {e}")
                yield {
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': str(e),
                    'status': 'error'
                }
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_marketplace_data(self) -> Dict[str, Any]:
        """Collect data from all marketplace APIs in parallel"""
        try:
            tasks = []
            for platform, scraper in self.marketplace_scrapers.items():
                if scraper.is_enabled():
                    tasks.append(scraper.collect_listings())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            marketplace_data = {
                'type': 'marketplace',
                'timestamp': datetime.utcnow(),
                'platforms': {}
            }
            
            for i, (platform, scraper) in enumerate(self.marketplace_scrapers.items()):
                if i < len(results) and not isinstance(results[i], Exception):
                    marketplace_data['platforms'][platform] = results[i]
            
            return marketplace_data
            
        except Exception as e:
            logger.error(f"Marketplace data collection error: {e}")
            return {'type': 'marketplace', 'error': str(e)}
    
    async def _collect_sports_data(self) -> Dict[str, Any]:
        """Collect comprehensive sports data from multiple APIs"""
        try:
            sports_data = {
                'type': 'sports',
                'timestamp': datetime.utcnow(),
                'leagues': {}
            }
            
            # Collect data for each league
            for league in ['NBA', 'NFL', 'MLB', 'NHL']:
                league_data = await self._collect_league_data(league.lower())
                if league_data:
                    sports_data['leagues'][league] = league_data
            
            return sports_data
            
        except Exception as e:
            logger.error(f"Sports data collection error: {e}")
            return {'type': 'sports', 'error': str(e)}
    
    async def _collect_sentiment_data(self) -> Dict[str, Any]:
        """Collect and analyze sentiment from multiple sources"""
        try:
            sentiment_data = {
                'type': 'sentiment',
                'timestamp': datetime.utcnow(),
                'sources': {}
            }
            
            # Collect sentiment from each source
            for source, analyzer in self.sentiment_analyzers.items():
                if analyzer.is_enabled():
                    source_sentiment = await analyzer.collect_sentiment()
                    if source_sentiment:
                        sentiment_data['sources'][source] = source_sentiment
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Sentiment data collection error: {e}")
            return {'type': 'sentiment', 'error': str(e)}
    
    async def _collect_external_context(self) -> Dict[str, Any]:
        """Collect external context data (weather, events, etc.)"""
        try:
            context_data = {
                'type': 'external',
                'timestamp': datetime.utcnow(),
                'weather': await self._get_weather_data(),
                'events': await self._get_competing_events(),
                'news': await self._get_relevant_news(),
                'market_indicators': await self._get_market_indicators()
            }
            
            return context_data
            
        except Exception as e:
            logger.error(f"External context collection error: {e}")
            return {'type': 'external', 'error': str(e)}
    
    async def _engineer_features(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply feature engineering to raw data"""
        try:
            features = {}
            data_type = raw_data.get('type', 'unknown')
            
            # Apply appropriate feature engineering based on data type
            if data_type == 'marketplace':
                features.update(await self.feature_engineers['market'].process(raw_data))
            elif data_type == 'sports':
                features.update(await self.feature_engineers['team'].process(raw_data))
            elif data_type in ['sentiment', 'external']:
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
    
    async def _collect_league_data(self, league: str) -> Dict[str, Any]:
        """Collect data for a specific league"""
        if league in self.sports_apis:
            return await self.sports_apis[league].get_current_data()
        return {}
    
    async def _get_weather_data(self) -> Dict[str, Any]:
        """Get weather data for relevant venues"""
        # Implement weather API integration
        return {}
    
    async def _get_competing_events(self) -> Dict[str, Any]:
        """Get competing events that might affect demand"""
        # Implement events API integration
        return {}
    
    async def _get_relevant_news(self) -> Dict[str, Any]:
        """Get relevant news articles"""
        # Implement news API integration
        return {}
    
    async def _get_market_indicators(self) -> Dict[str, Any]:
        """Get relevant market indicators"""
        # Implement market data integration
        return {}


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


class StubHubScraper(BaseScraper):
    """
    StubHub API integration for real-time ticket data collection
    Uses StubHub's Discovery API for event and listing data
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('STUBHUB_API_KEY', '')
        self.base_url = 'https://api.stubhub.com/catalog/events/v3'
        self.enabled = bool(self.api_key)
    
    async def collect_listings(self) -> Dict[str, Any]:
        """
        Collect real-time ticket listings from StubHub
        Returns event data with pricing information
        """
        try:
            if not self.enabled:
                logger.info("StubHub scraper not enabled - API key not configured")
                return {
                    'platform': 'stubhub',
                    'listings': [],
                    'timestamp': datetime.utcnow(),
                    'status': 'disabled'
                }
            
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                
                # Search for events (e.g., NBA, NFL, MLB games)
                params = {
                    'categoryName': 'Sports',
                    'status': 'active',
                    'rows': 100  # Get up to 100 events
                }
                
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract listings from events
                    listings = []
                    events = data.get('events', [])
                    
                    for event in events:
                        # Get ticket listings for each event
                        event_listings = await self._get_event_listings(
                            client, headers, event.get('id')
                        )
                        listings.extend(event_listings)
                    
                    logger.info(f"StubHub: Collected {len(listings)} listings from {len(events)} events")
                    
                    return {
                        'platform': 'stubhub',
                        'listings': listings,
                        'event_count': len(events),
                        'timestamp': datetime.utcnow(),
                        'status': 'success'
                    }
                else:
                    logger.warning(f"StubHub API returned status {response.status_code}")
                    return {
                        'platform': 'stubhub',
                        'listings': [],
                        'timestamp': datetime.utcnow(),
                        'status': 'api_error',
                        'error_code': response.status_code
                    }
                    
        except Exception as e:
            logger.error(f"StubHub scraper error: {e}")
            return {
                'platform': 'stubhub',
                'listings': [],
                'timestamp': datetime.utcnow(),
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_event_listings(
        self, 
        client: httpx.AsyncClient, 
        headers: Dict[str, str], 
        event_id: str
    ) -> List[Dict[str, Any]]:
        """Get ticket listings for a specific event"""
        try:
            # StubHub inventory API endpoint
            inventory_url = f'https://api.stubhub.com/search/inventory/v2'
            
            params = {'eventid': event_id}
            
            response = await client.get(
                inventory_url,
                headers=headers,
                params=params,
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                listings = data.get('listing', [])
                
                # Parse and normalize listing data
                normalized_listings = []
                for listing in listings:
                    normalized_listings.append({
                        'event_id': event_id,
                        'listing_id': listing.get('listingId'),
                        'section': listing.get('sectionName'),
                        'row': listing.get('row'),
                        'quantity': listing.get('quantity'),
                        'price': float(listing.get('currentPrice', {}).get('amount', 0)),
                        'currency': listing.get('currentPrice', {}).get('currency', 'USD'),
                        'delivery_type': listing.get('deliveryTypeList', []),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                return normalized_listings
            else:
                logger.debug(f"Failed to get listings for event {event_id}: {response.status_code}")
                return []
                
        except Exception as e:
            logger.debug(f"Error getting event listings: {e}")
            return []


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
    """Sportradar API integration"""
    
    async def get_current_data(self) -> Dict[str, Any]:
        try:
            # Implement Sportradar API calls
            return {
                'source': 'sportradar',
                'data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Sportradar API error: {e}")
            return {}


class ESPNAPI(BaseAPI):
    """ESPN API integration"""
    
    async def get_current_data(self) -> Dict[str, Any]:
        try:
            # Implement ESPN API calls
            return {
                'source': 'espn',
                'data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"ESPN API error: {e}")
            return {}


class NBAAPI(BaseAPI):
    """NBA Official API integration"""
    
    async def get_current_data(self) -> Dict[str, Any]:
        try:
            # Implement NBA API calls
            return {
                'source': 'nba',
                'data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"NBA API error: {e}")
            return {}


class NFLAPI(BaseAPI):
    """NFL Official API integration"""
    
    async def get_current_data(self) -> Dict[str, Any]:
        try:
            # Implement NFL API calls
            return {
                'source': 'nfl',
                'data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"NFL API error: {e}")
            return {}


class MLBAPI(BaseAPI):
    """MLB Official API integration"""
    
    async def get_current_data(self) -> Dict[str, Any]:
        try:
            # Implement MLB API calls
            return {
                'source': 'mlb',
                'data': {},
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"MLB API error: {e}")
            return {}


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