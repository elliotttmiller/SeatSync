# Development Workarounds for API Requirements

## Problem
Marketplace APIs (StubHub, SeatGeek) require approval/partnership which can take time. During development, we need alternatives to test and validate our scraping logic.

## Scrapling's Anti-Bot Capabilities

✅ **What Scrapling Provides** (from [docs](https://scrapling.readthedocs.io/en/latest/)):
- Modified Firefox browser with fingerprint spoofing
- Automatic Cloudflare Turnstile/Interstitial bypass
- AWS WAF challenge solving capabilities
- TLS fingerprint randomization
- Realistic browser behavior simulation
- Humanized cursor movement

✅ **Features We're Using**:
```python
StealthyFetcher.fetch(
    url,
    headless=True,              # Run in background
    solve_cloudflare=True,      # Auto-solve Cloudflare & AWS WAF challenges
    network_idle=True,          # Wait for all network requests
    wait=3000-5000,             # Wait for dynamic content (milliseconds)
    humanize=True,              # Realistic cursor movement
    disable_resources=False,    # Load all page resources
    os_randomize=False          # Match OS fingerprints
)
```

## Current Status

### What Works ✅
1. **Two-Step Workflow**: Search → Find Event → Navigate → Scrape
2. **Multiple URL Fallbacks**: Tries different URL formats
3. **Event URL Discovery**: Automatically finds event pages
4. **AWS WAF Detection**: Logs when challenges are encountered
5. **Enhanced Stealth**: Full Scrapling capabilities enabled

### Known Challenges ⚠️
1. **AWS WAF Still Active**: StubHub returns HTTP 202 (challenge pages)
2. **Challenge Solving**: Even with `solve_cloudflare=True`, AWS WAF may not be fully bypassed
3. **Off-Season**: No current games = 0 listings (expected behavior)

## Development Workarounds

### Option 1: Use Direct Event URLs (✅ Recommended for Dev)

Instead of searching, provide the exact event page URL:

```python
from backend.app.services.scraping_service import scrape_tickets

# Direct URL (bypasses search-based discovery)
result = await scrape_tickets(
    marketplace="StubHub",
    event_url="https://www.stubhub.com/minnesota-timberwolves-tickets/performer/2986"
)

print(f"Found {len(result['listings'])} tickets")
```

**Pros:**
- Skips search phase entirely
- No search-based discovery needed
- Works immediately
- Tests the core scraping logic

**Cons:**
- Requires knowing the event URL
- Still subject to AWS WAF on event pages
- Not fully automated

**How to Get URLs:**
1. Visit marketplace website manually
2. Search for your event
3. Copy the event page URL
4. Use it in your code

### Option 2: Enhanced Scraping Setup (Better Results)

If you need search-based discovery to work:

**A. Use Residential IP**
```bash
# AWS WAF is more lenient with residential IPs
# Run from home network, not datacenter/cloud
# Or use residential proxy service
```

**B. Add Delays**
```python
# Add random delays between requests
import random
await asyncio.sleep(random.uniform(2, 5))
```

**C. Run During Off-Peak Hours**
```python
# AWS WAF may be less aggressive during off-peak hours
# Try early morning or late night
```

**D. Use Proxy Rotation**
```python
# Install scrapling with proxy support
pip install 'scrapling[all]'

# Use with proxy
result = StealthyFetcher.fetch(
    url,
    proxy="http://your-proxy:port",
    # ... other params
)
```

### Option 3: Alternative Data Sources (No Scraping)

**A. Use Public APIs**
- **SeatGeek API**: Public, free tier, no approval needed
  ```python
  import requests
  
  # Get events
  response = requests.get(
      "https://api.seatgeek.com/2/events",
      params={
          "performers.slug": "minnesota-timberwolves",
          "client_id": "YOUR_CLIENT_ID"  # Get from seatgeek.com/account
      }
  )
  ```

- **Ticketmaster Discovery API**: Public, free tier
  ```python
  response = requests.get(
      "https://app.ticketmaster.com/discovery/v2/events.json",
      params={
          "keyword": "Minnesota Timberwolves",
          "apikey": "YOUR_API_KEY"  # Get from developer.ticketmaster.com
      }
  )
  ```

**B. Use Mock Data for Development**
```python
# Create realistic mock data for testing
mock_listings = [
    {'price': 150.0, 'section': '200', 'row': '15', 'quantity': 2},
    {'price': 200.0, 'section': '100', 'row': '10', 'quantity': 2},
    # ... more listings
]

# Test your logic with mock data
# Switch to real scraping when ready
```

### Option 4: Hybrid Approach (Best of Both)

```python
async def get_tickets(marketplace, search_query=None, event_url=None):
    """
    Try multiple approaches in order of preference
    """
    # 1. Try official API first (if available)
    if marketplace.lower() == 'seatgeek':
        try:
            result = await fetch_seatgeek_api(search_query)
            if result['listings']:
                return result
        except:
            pass
    
    # 2. Try direct URL if provided
    if event_url:
        try:
            result = await scrape_tickets(
                marketplace=marketplace,
                event_url=event_url
            )
            if result['listings']:
                return result
        except:
            pass
    
    # 3. Try search-based scraping
    if search_query:
        result = await scrape_tickets(
            marketplace=marketplace,
            search_query=search_query
        )
        return result
    
    # 4. Fall back to mock data
    return {'status': 'mock', 'listings': generate_mock_listings()}
```

## Testing Your Setup

### Test 1: Validate Logic (No Network)
```bash
python test_scraping_logic.py
# ✅ Should pass - validates code structure
```

### Test 2: Test with Direct URL
```bash
python test_improved_scraping.py
# Tests with actual Minnesota Timberwolves URL
```

### Test 3: Test in Streamlit App
```bash
streamlit run streamlit_app.py
# Navigate to: 🕷️ Data Collection & Scraping
# Try both search query and direct URL
```

## Understanding HTTP Status Codes

| Code | Meaning | What to Do |
|------|---------|------------|
| 200 OK | Success | Page loaded correctly |
| 202 Accepted | Challenge page | AWS WAF challenge - Scrapling should solve |
| 301 Moved | Redirect | Follow redirect |
| 404 Not Found | Page doesn't exist | Try different URL format |
| 403 Forbidden | Blocked | Use proxy or residential IP |

## Debugging Tips

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Page Content
```python
# Add to scrapling_service.py for debugging
page_html = page.html if hasattr(page, 'html') else str(page)
logger.debug(f"Page content (first 1000 chars): {page_html[:1000]}")
```

### Test Individual Components
```python
# Test just URL discovery
search_url = "https://www.stubhub.com/minnesota-timberwolves-tickets"
page = StealthyFetcher.fetch(search_url, solve_cloudflare=True, wait=5000)
links = page.css('a[href*="/event/"]')
print(f"Found {len(links)} event links")
```

## When to Use What

| Scenario | Recommended Approach |
|----------|---------------------|
| Quick development testing | Direct URLs + Mock data |
| Testing scraping logic | Direct URLs (actual events) |
| Testing search discovery | Enhanced setup with delays |
| Production deployment | Official APIs |
| No API available | Enhanced scraping + proxy |
| Proof of concept | Mock data first, then real |

## Summary

**For Development Phase:**
1. ✅ **Use direct event URLs** - Fastest, most reliable
2. ✅ **Use public APIs when available** - SeatGeek, Ticketmaster
3. ✅ **Use mock data** - Test logic without network calls
4. ⚠️ **Enhanced scraping as fallback** - When above options not available

**The scraping logic is solid and working.** The main challenge is anti-bot protection during the search phase. By using direct URLs during development, you can validate all the ticket extraction logic without needing to bypass AWS WAF challenges.

**For Production:**
- Official APIs strongly recommended
- If scraping required: residential proxies + proper rate limiting
- Hybrid approach: API primary, scraping fallback
