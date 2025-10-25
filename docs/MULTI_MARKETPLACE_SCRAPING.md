# Multi-Marketplace Scraping Guide

## Overview

SeatSync now supports scraping multiple ticket marketplaces simultaneously, providing comprehensive price comparison across all major platforms.

## Supported Marketplaces

- **StubHub**
- **SeatGeek**
- **Ticketmaster**
- **VividSeats**

## Features

### 1. Concurrent Scraping
By default, all marketplaces are scraped concurrently using `asyncio.gather()` with a semaphore to limit parallel requests (max 4 concurrent).

**Benefits:**
- Faster results (up to 4x speedup for 4 marketplaces)
- Controlled resource usage
- Graceful handling of partial failures

### 2. Marketplace Selection
Users can opt-out of specific marketplaces using checkboxes in the UI.

### 3. Aggregate Results
Results include:
- Total listings across all marketplaces
- Per-marketplace breakdown
- Success/failure counts
- Combined price distribution
- Detailed error reporting

## Usage

### Backend API

#### Scrape All Marketplaces (Default)
```python
from app.services.scraping_service import scrape_tickets

# Scrape all marketplaces concurrently
result = await scrape_tickets(
    marketplace=None,  # or "all" or "*"
    search_query="Lakers",
    adaptive=False
)

# Result structure:
# {
#     'status': 'success' | 'partial' | 'error',
#     'total_listings': 150,
#     'listings': [...],  # Combined list
#     'per_marketplace': {
#         'stubhub': {...},
#         'seatgeek': {...},
#         'ticketmaster': {...},
#         'vividseats': {...}
#     },
#     'summary': {
#         'successful': 3,
#         'failed': 1,
#         'total': 4,
#         'errors': [...],
#         'concurrent': True
#     }
# }
```

#### Scrape Specific Marketplaces
```python
# Scrape only selected marketplaces
service = await get_scraping_service()
result = await service.scrape_all_marketplaces(
    search_query="Lakers",
    marketplaces=["stubhub", "seatgeek"],  # Only these two
    concurrent=True
)
```

#### Sequential Scraping (Conservative Mode)
```python
# Scrape sequentially instead of concurrently
result = await service.scrape_all_marketplaces(
    search_query="Lakers",
    concurrent=False  # One at a time
)
```

#### Single Marketplace (Backward Compatible)
```python
# Still works as before
result = await scrape_tickets(
    marketplace="stubhub",
    search_query="Lakers"
)

# Result structure (single marketplace):
# {
#     'status': 'success' | 'error',
#     'platform': 'stubhub',
#     'listings': [...],
#     'url': '...',
#     'count': 50,
#     'timestamp': '...'
# }
```

### Streamlit UI

1. **Enter Search Query**: Team name or event (e.g., "Lakers")
2. **Select Marketplaces**: Check/uncheck marketplaces to include
3. **Choose Scraping Mode**:
   - ✅ Concurrent (default, faster)
   - ❌ Sequential (slower, more conservative)
4. **Enable Adaptive Tracking** (optional): For websites with changed structure
5. **Click "🚀 Start Scraping All Marketplaces"**

### Results Display

The UI shows:
- **Aggregate Metrics**: Total listings, success rate, average price
- **Per-Marketplace Breakdown**: Expandable sections for each marketplace
- **Error Details**: If any marketplace fails, detailed error messages and recommendations
- **Price Distribution Chart**: Combined histogram across all marketplaces
- **Session History**: Track all scraping sessions with marketplace breakdown

## Performance

### Concurrent Mode (Default)
- Scrapes 4 marketplaces in ~30-60 seconds
- Uses semaphore to limit concurrent requests (max 4)
- Best for quick price comparisons

### Sequential Mode
- Scrapes 4 marketplaces in ~90-150 seconds
- One marketplace at a time
- Best for avoiding rate limits or debugging

## Error Handling

The system handles partial failures gracefully:
- If 3/4 marketplaces succeed, status is "partial"
- Per-marketplace errors are tracked and reported
- Users see which marketplaces succeeded and which failed
- Failed marketplaces don't block successful ones

## Best Practices

1. **Use Concurrent Mode**: Enabled by default for best performance
2. **Select Needed Marketplaces**: Uncheck marketplaces you don't need
3. **Enable Adaptive Tracking**: If scraping fails due to website changes
4. **Check Error Messages**: For failed marketplaces, review recommendations
5. **Respect Rate Limits**: Don't scrape too frequently (every few minutes is safe)

## Scrapling Integration

All scraping uses [Scrapling](https://scrapling.readthedocs.io/) for:
- 685x faster parsing than BeautifulSoup
- Built-in Cloudflare bypass
- TLS fingerprint impersonation
- Adaptive element tracking (survives website changes)
- Superior anti-bot detection

## Troubleshooting

### "Failed to initialize scraping service"
- Install Scrapling: `pip install 'scrapling[all]>=0.3.7'`
- Run setup: `scrapling install`

### "AWS WAF protection blocked access"
StubHub uses advanced AWS WAF protection. See recommendations in error message:
- Use StubHub Official API (recommended)
- Try residential proxies
- Consider alternative marketplaces
- See `docs/AWS_WAF_LIMITATION.md` for details

### Partial Success (Some Marketplaces Failed)
This is normal! Marketplaces may temporarily block scraping. The system continues with successful marketplaces.

## API Reference

### `MARKETPLACES` Constant
```python
MARKETPLACES = ("stubhub", "seatgeek", "ticketmaster", "vividseats")
```

### `scrape_all_marketplaces()` Method
```python
async def scrape_all_marketplaces(
    search_query: Optional[str] = None,
    event_url: Optional[str] = None,
    adaptive: bool = False,
    marketplaces: Optional[List[str]] = None,
    concurrent: bool = True,
    max_concurrent: int = 4
) -> Dict[str, Any]
```

### `scrape_tickets()` Function
```python
async def scrape_tickets(
    marketplace: Optional[str] = None,  # None/"all"/"*" for multi-marketplace
    search_query: Optional[str] = None,
    event_url: Optional[str] = None,
    adaptive: bool = False
) -> Dict[str, Any]
```

## Examples

### Example 1: Quick Price Comparison
```python
# Get prices for Lakers game from all marketplaces
result = await scrape_tickets(
    marketplace=None,  # All marketplaces
    search_query="Lakers vs Celtics"
)

print(f"Found {result['total_listings']} total listings")
print(f"Success rate: {result['summary']['successful']}/{result['summary']['total']}")

# Get cheapest listing across all marketplaces
all_prices = [l['price'] for l in result['listings'] if 'price' in l]
print(f"Best price: ${min(all_prices)}")
```

### Example 2: Compare Specific Marketplaces
```python
# Compare only StubHub and SeatGeek
service = await get_scraping_service()
result = await service.scrape_all_marketplaces(
    search_query="Warriors",
    marketplaces=["stubhub", "seatgeek"]
)

# Compare average prices
for marketplace, mp_result in result['per_marketplace'].items():
    listings = mp_result.get('listings', [])
    if listings:
        avg_price = sum(l['price'] for l in listings) / len(listings)
        print(f"{marketplace}: ${avg_price:.2f} avg")
```

### Example 3: Sequential Scraping for Debugging
```python
# Scrape one at a time to isolate issues
result = await service.scrape_all_marketplaces(
    search_query="Lakers",
    concurrent=False  # Sequential mode
)

# Check each marketplace individually
for marketplace, mp_result in result['per_marketplace'].items():
    if mp_result['status'] == 'error':
        print(f"❌ {marketplace} failed: {mp_result['error']}")
    else:
        print(f"✅ {marketplace} succeeded: {len(mp_result['listings'])} listings")
```

## Contributing

To add support for a new marketplace:

1. Add marketplace name to `MARKETPLACES` tuple in `scraping_service.py`
2. Implement scraping method in `scrapling_service.py` (e.g., `_scrape_newmarket()`)
3. Add routing in `scrape_marketplace()` method
4. Update UI checkbox options in `streamlit_app.py`
5. Add tests for the new marketplace
6. Update this documentation

## See Also

- [Scrapling Documentation](https://scrapling.readthedocs.io/)
- [Scrapling Stealth Mode](https://scrapling.readthedocs.io/en/latest/fetching/stealthy/)
- [AWS WAF Limitations](./AWS_WAF_LIMITATION.md)
