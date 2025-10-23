# SeatSync Scraping System Documentation

## Overview

The SeatSync scraping system has been refactored to provide a clean, efficient, and robust ticket price collection system with automatic fallbacks and improved error handling.

## Key Improvements

### 1. **Unified Scraping Interface**
   - Single entry point: `scrape_tickets()` function
   - Automatic detection of best available scraping method
   - Graceful fallback from Playwright to HTTP when needed
   - Consistent API regardless of underlying implementation

### 2. **Type Safety Improvements**
   - Fixed `BrowserContext`, `Page`, and `Browser` type hint issues
   - Proper handling when Playwright is not installed
   - No more `NameError` exceptions at import time

### 3. **Enhanced Error Handling**
   - Better initialization checks
   - Clear error messages with actionable guidance
   - Automatic cleanup of resources
   - Proper exception handling throughout

### 4. **Streamlit Integration**
   - Updated to use latest Streamlit API (`width` instead of deprecated `use_container_width`)
   - Improved error display
   - Better initialization feedback

## Quick Start

### Installation

```bash
# Basic installation
pip install -r backend/requirements.txt

# For full scraping capabilities (recommended)
pip install playwright
playwright install chromium
```

### Usage in Code

```python
from backend.app.services import scrape_tickets

# Simple scraping
result = await scrape_tickets(
    marketplace="stubhub",
    search_query="Lakers"
)

if result['status'] == 'success':
    listings = result['listings']
    print(f"Found {len(listings)} listings")
```

### Usage with Streamlit

```bash
# Run the development dashboard
streamlit run streamlit_app.py
```

## Architecture

### Scraping Service Hierarchy

```
scraping_service.py (Unified Interface)
    ├── advanced_ticket_scraper.py (Playwright-based)
    │   ├── Supports: StubHub, SeatGeek, Ticketmaster
    │   ├── Features: JS rendering, anti-detection, human simulation
    │   └── Requires: Playwright installed
    │
    └── enhanced_scraping.py (HTTP-based fallback)
        ├── Supports: Basic HTTP requests
        ├── Features: Proxy rotation, rate limiting
        └── Requires: httpx, beautifulsoup4
```

### Automatic Fallback Logic

1. **Try Playwright Scraper**: Full JavaScript support, anti-detection
2. **Fall back to HTTP**: If Playwright unavailable
3. **Clear Error Messages**: If neither works, provides installation instructions

## API Reference

### `scrape_tickets()`

Convenience function for quick scraping operations.

```python
async def scrape_tickets(
    marketplace: str,
    search_query: Optional[str] = None,
    event_url: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `marketplace`: Name of marketplace ("stubhub", "seatgeek", "ticketmaster")
- `search_query`: Search term for events (e.g., "Lakers", "Taylor Swift")
- `event_url`: Direct URL to specific event page (optional)

**Returns:**
```python
{
    'status': 'success',  # or 'error', 'warning'
    'platform': 'stubhub',
    'listings': [
        {
            'price': 150.00,
            'section': '200',
            'row': '15',
            'quantity': 2,
            'platform': 'stubhub'
        },
        # ... more listings
    ],
    'timestamp': '2025-10-23T15:30:00',
    'url': 'https://...',
    'metadata': { ... }
}
```

### `ScrapingService` Class

For more control and persistent scraping sessions:

```python
from backend.app.services import get_scraping_service

# Get service instance (singleton)
service = await get_scraping_service()

# Check status
status = service.get_status()
print(f"Scraper type: {status['scraper_type']}")
print(f"Capabilities: {status['capabilities']}")

# Scrape multiple marketplaces
for marketplace in ['stubhub', 'seatgeek']:
    result = await service.scrape_marketplace(
        marketplace=marketplace,
        search_query="Lakers"
    )
    print(f"{marketplace}: {len(result['listings'])} listings")

# Cleanup when done
await service.cleanup()
```

## Troubleshooting

### "Failed to initialize scraper"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### "Playwright not available"

The system will automatically fall back to HTTP scraping. For full functionality:
```bash
pip install playwright
playwright install chromium
```

### Streamlit Deprecation Warnings

These have been fixed in the latest version. If you see them, update:
```bash
git pull origin main
```

### Import Errors

Ensure you're importing from the correct location:
```python
# ✅ Correct
from backend.app.services import scrape_tickets

# ❌ Wrong
from app.services.advanced_ticket_scraper import AdvancedTicketScraper
```

## Performance Optimization

### Rate Limiting

The scraper automatically rate limits to 30 requests/minute by default. Adjust if needed:

```python
service = await get_scraping_service()
# Rate limiting is handled automatically
```

### Concurrent Scraping

For scraping multiple marketplaces concurrently:

```python
import asyncio

async def scrape_all():
    tasks = [
        scrape_tickets("stubhub", "Lakers"),
        scrape_tickets("seatgeek", "Lakers"),
        scrape_tickets("ticketmaster", "Lakers")
    ]
    results = await asyncio.gather(*tasks)
    return results

results = asyncio.run(scrape_all())
```

### Resource Management

The service automatically manages browser instances and connections. For long-running processes:

```python
# Use context manager pattern
service = await get_scraping_service()
try:
    # Your scraping logic
    result = await service.scrape_marketplace(...)
finally:
    await service.cleanup()
```

## Best Practices

1. **Always use the unified interface** (`scrape_tickets()` or `ScrapingService`)
2. **Handle errors gracefully** - Check `status` field in results
3. **Clean up resources** - Call `cleanup()` when done with service
4. **Respect rate limits** - Don't override the built-in rate limiting
5. **Use search queries** - More reliable than direct URLs for testing
6. **Monitor initialization** - Check service status before scraping

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run scraping tests
pytest backend/tests/test_scraping.py -v
```

### Adding New Marketplaces

To add support for a new marketplace:

1. Add scraping method to `advanced_ticket_scraper.py`:
```python
async def scrape_newsite(self, event_url=None, search_query=None):
    # Implementation
    pass
```

2. Update routing in `scraping_service.py`:
```python
elif marketplace_lower == 'newsite':
    result = await self.scraper.scrape_newsite(...)
```

3. Update capabilities list in `_get_capabilities()`:
```python
return [
    'stubhub',
    'seatgeek',
    'ticketmaster',
    'newsite',  # Add here
    ...
]
```

## Migration Guide

### From Old API to New API

**Before:**
```python
from app.services.advanced_ticket_scraper import AdvancedTicketScraper

scraper = AdvancedTicketScraper()
await scraper.initialize()
result = await scraper.scrape_stubhub(search_query="Lakers")
await scraper.cleanup()
```

**After:**
```python
from backend.app.services import scrape_tickets

result = await scrape_tickets(
    marketplace="stubhub",
    search_query="Lakers"
)
# Cleanup handled automatically
```

## Support

For issues or questions:
1. Check this documentation
2. Review error messages (they include solutions)
3. Check logs for detailed debugging information
4. Open an issue on GitHub with error details

## Changelog

### Version 2.0 (Current)
- ✅ Unified scraping interface
- ✅ Automatic fallback system
- ✅ Fixed type hint issues
- ✅ Improved error handling
- ✅ Updated Streamlit integration
- ✅ Better resource management

### Version 1.0 (Legacy)
- Individual scraper implementations
- Manual initialization required
- Type hint issues with Playwright
- Complex error handling
