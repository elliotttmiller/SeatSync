# SeatSync Marketplace Integration Guide

## Overview

SeatSync now supports real-time ticket price collection from multiple marketplace platforms through official APIs and web scraping. This document explains how to configure and use these integrations.

## Supported Marketplaces

### 1. StubHub API Integration

**Status**: ✅ Fully Implemented

**Configuration**:
```bash
# Add to your .env file
STUBHUB_API_KEY=your_stubhub_api_key_here
```

**How to Get API Key**:
1. Visit [StubHub Developer Portal](https://developer.stubhub.com/)
2. Create a developer account
3. Register your application
4. Copy your API key

**Features**:
- Real-time event discovery
- Detailed ticket inventory
- Section, row, and seat-level pricing
- Multiple delivery type options
- Up to 100 events per query

**API Endpoints Used**:
- `/catalog/events/v3` - Event discovery
- `/search/inventory/v2` - Ticket listings

---

### 2. SeatGeek API Integration

**Status**: ✅ Fully Implemented

**Configuration**:
```bash
# Add to your .env file
SEATGEEK_CLIENT_ID=your_seatgeek_client_id
SEATGEEK_CLIENT_SECRET=your_seatgeek_client_secret
```

**How to Get API Credentials**:
1. Visit [SeatGeek Platform](https://platform.seatgeek.com/)
2. Create an account
3. Register your application
4. Get your Client ID and Client Secret

**Features**:
- Comprehensive event search
- Price statistics (lowest, average, highest, median)
- Listing counts
- Event popularity scores
- Venue information
- Real-time pricing updates

**API Endpoints Used**:
- `/2/events` - Event search with filters

---

### 3. Ticketmaster API Integration

**Status**: ✅ Fully Implemented

**Configuration**:
```bash
# Add to your .env file
TICKETMASTER_API_KEY=your_ticketmaster_api_key
```

**How to Get API Key**:
1. Visit [Ticketmaster Developer Portal](https://developer.ticketmaster.com/)
2. Create an account
3. Register your application
4. Get your API key (Consumer Key)

**Features**:
- Comprehensive sports event discovery
- Price range information (min/max)
- Venue details
- Event classifications (sport, genre)
- Sales period information
- Event status tracking

**API Endpoints Used**:
- `/discovery/v2/events.json` - Event discovery

---

### 4. Vivid Seats Integration

**Status**: ⚠️ Placeholder (Requires Browser Automation)

**Configuration**:
```bash
# Add to your .env file
ENABLE_VIVIDSEATS_SCRAPING=true
```

**Note**: Vivid Seats does not provide a public API. Full implementation requires:
- Browser automation (Playwright or Selenium)
- JavaScript rendering
- CAPTCHA handling
- Proxy rotation (optional)

**Future Implementation**:
- [ ] Playwright browser automation
- [ ] Event discovery scraping
- [ ] Price extraction
- [ ] Anti-bot detection handling

---

## Data Collection Architecture

### Parallel Data Collection

All enabled marketplace scrapers run in parallel for maximum efficiency:

```python
from app.services.data_ingestion import AdvancedDataPipeline

pipeline = AdvancedDataPipeline()

# Start real-time data collection
async for data in pipeline.real_time_data_stream(db):
    # Process marketplace data
    if data.get('type') == 'marketplace':
        platforms = data.get('platforms', {})
        
        # Access data from each platform
        stubhub_data = platforms.get('stubhub', {})
        seatgeek_data = platforms.get('seatgeek', {})
        ticketmaster_data = platforms.get('ticketmaster', {})
```

### Rate Limiting

Each scraper implements rate limiting to respect API limits:
- Default: 10 requests per minute per platform
- Configurable via scraper initialization

### Error Handling

Graceful fallback when platforms are unavailable:
- Continues collecting from other platforms
- Logs errors without stopping pipeline
- Returns status codes for monitoring

---

## Data Structure

### Normalized Listing Format

All marketplace data is normalized into a consistent format:

```python
{
    'event_id': str,           # Platform-specific event ID
    'title/name': str,         # Event name
    'datetime': str,           # ISO 8601 datetime
    'venue': str,              # Venue name
    'city': str,               # City
    'state': str,              # State/Province code
    'section': str,            # Section (if available)
    'row': str,                # Row (if available)
    'price': float,            # Price in USD
    'price_min': float,        # Minimum price
    'price_max': float,        # Maximum price
    'price_average': float,    # Average price (SeatGeek)
    'listing_count': int,      # Number of listings
    'timestamp': str,          # Collection timestamp
    'platform': str,           # Source platform
    'url': str                 # Direct link to event
}
```

---

## Usage Examples

### Example 1: Collect Data from All Platforms

```python
from app.services.data_ingestion import AdvancedDataPipeline
from app.db.session import get_db

async def collect_marketplace_data():
    pipeline = AdvancedDataPipeline()
    db = await get_db()
    
    # Collect from all platforms
    marketplace_data = await pipeline._collect_marketplace_data()
    
    print(f"StubHub listings: {len(marketplace_data['platforms']['stubhub']['listings'])}")
    print(f"SeatGeek listings: {len(marketplace_data['platforms']['seatgeek']['listings'])}")
    print(f"Ticketmaster listings: {len(marketplace_data['platforms']['ticketmaster']['listings'])}")
```

### Example 2: Filter by Sport

```python
async def get_nba_events():
    pipeline = AdvancedDataPipeline()
    
    # SeatGeek supports filtering by type
    seatgeek = pipeline.marketplace_scrapers['seatgeek']
    data = await seatgeek.collect_listings()
    
    # Filter NBA events
    nba_events = [
        listing for listing in data['listings']
        if 'NBA' in listing.get('title', '')
    ]
    
    return nba_events
```

### Example 3: Price Comparison

```python
async def compare_prices_across_platforms(event_name: str):
    pipeline = AdvancedDataPipeline()
    marketplace_data = await pipeline._collect_marketplace_data()
    
    prices = {}
    for platform, data in marketplace_data['platforms'].items():
        for listing in data['listings']:
            if event_name.lower() in listing.get('title', '').lower():
                prices[platform] = {
                    'min': listing.get('price_min', listing.get('price', 0)),
                    'max': listing.get('price_max', listing.get('price', 0)),
                    'avg': listing.get('price_average', listing.get('price', 0))
                }
    
    return prices
```

---

## Performance Considerations

### API Rate Limits

| Platform | Rate Limit | Notes |
|----------|------------|-------|
| StubHub | ~40 requests/min | Varies by endpoint |
| SeatGeek | 5,000 requests/day | Free tier limit |
| Ticketmaster | 5,000 requests/day | Rate limit quota |
| Vivid Seats | N/A | Web scraping (use caution) |

### Caching Strategy

To minimize API calls:
- Cache event data for 30 minutes
- Cache pricing data for 5 minutes
- Invalidate cache on explicit refresh

### Parallel Collection

All platforms are queried in parallel using `asyncio.gather()`:
- Average collection time: 3-5 seconds for all platforms
- Timeout per platform: 30 seconds
- Failures don't block other platforms

---

## Monitoring and Debugging

### Check Platform Status

```python
from app.services.data_ingestion import AdvancedDataPipeline

pipeline = AdvancedDataPipeline()

for platform, scraper in pipeline.marketplace_scrapers.items():
    is_enabled = scraper.is_enabled()
    print(f"{platform}: {'✅ Enabled' if is_enabled else '❌ Disabled'}")
```

### View Collection Logs

```bash
# Set log level to DEBUG to see detailed scraper activity
export LOG_LEVEL=debug

# Or in your .env file
LOG_LEVEL=debug
```

### API Response Status Codes

All scrapers return status information:
- `success`: Data collected successfully
- `disabled`: API credentials not configured
- `api_error`: API returned error (check error_code)
- `error`: Exception occurred (check error message)

---

## Best Practices

### 1. API Key Security

```bash
# Never commit API keys to git
echo ".env" >> .gitignore

# Use environment variables in production
export STUBHUB_API_KEY="..."
export SEATGEEK_CLIENT_ID="..."
```

### 2. Respect Rate Limits

```python
# Configure custom rate limits if needed
scraper = StubHubScraper()
scraper.rate_limit = 20  # requests per minute
```

### 3. Error Handling

```python
try:
    data = await pipeline._collect_marketplace_data()
    
    # Check for errors
    for platform, platform_data in data['platforms'].items():
        if platform_data.get('status') != 'success':
            logger.warning(f"{platform} failed: {platform_data.get('error')}")
            
except Exception as e:
    logger.error(f"Marketplace collection failed: {e}")
```

### 4. Data Validation

```python
# Validate listing data before processing
def is_valid_listing(listing: dict) -> bool:
    required_fields = ['event_id', 'price', 'timestamp']
    return all(field in listing for field in required_fields)

valid_listings = [
    listing for listing in data['listings']
    if is_valid_listing(listing)
]
```

---

## Troubleshooting

### Issue: No data returned from platform

**Solution**:
1. Verify API credentials are correct
2. Check API key has necessary permissions
3. Verify platform API is operational
4. Check rate limits haven't been exceeded

### Issue: Timeout errors

**Solution**:
1. Increase timeout in scraper configuration
2. Check network connectivity
3. Verify API endpoint URLs are correct

### Issue: Authentication errors

**Solution**:
1. Regenerate API keys
2. Check API key format (some require 'Bearer' prefix)
3. Verify account is active and in good standing

---

## Future Enhancements

- [ ] Add AXS (formerly AEG) integration
- [ ] Add TickPick integration
- [ ] Add Gametime integration
- [ ] Implement Vivid Seats browser automation
- [ ] Add webhook support for real-time updates
- [ ] Implement intelligent rate limit management
- [ ] Add data deduplication across platforms
- [ ] Create unified event matching system

---

## API Documentation Links

- **StubHub**: https://developer.stubhub.com/
- **SeatGeek**: https://platform.seatgeek.com/
- **Ticketmaster**: https://developer.ticketmaster.com/
- **Vivid Seats**: No public API (web scraping required)

---

## Support

For issues or questions about marketplace integration:
1. Check logs for detailed error messages
2. Review API provider documentation
3. Open an issue in the repository
4. Contact support with platform-specific questions

---

**Last Updated**: 2024-01-20
**Version**: 1.0.0
