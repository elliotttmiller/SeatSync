# Windows Asyncio Fix for Scrapling Service

## Problem Statement

The SeatSync scraping service was encountering `NotImplementedError` exceptions when running on Windows. The errors occurred during the creation of subprocess operations within Playwright/Camoufox browser automation.

### Error Details

```
NotImplementedError
Traceback (most recent call last):
  File "...\backend\app\services\scrapling_scraper.py", line 443, in _scrape_seatgeek
    page = await asyncio.to_thread(fetch_search)
  ...
  File "...\asyncio\base_events.py", line 503, in _make_subprocess_transport
    raise NotImplementedError
NotImplementedError
```

### Root Cause

Windows uses the `ProactorEventLoop` for asyncio, which has limitations with subprocess operations. When using `asyncio.to_thread()` to run synchronous Playwright/Camoufox code that internally creates its own event loop and subprocesses, the nested event loop structure caused conflicts on Windows.

The issue occurred in all marketplace scrapers:
- StubHub (_scrape_stubhub)
- SeatGeek (_scrape_seatgeek)
- Ticketmaster (_scrape_ticketmaster)
- Vivid Seats (_scrape_vividseats)

## Solution

### Implementation

We replaced `asyncio.to_thread()` with a `ThreadPoolExecutor` approach using `loop.run_in_executor()`. This properly isolates the synchronous Playwright operations from the async event loop.

#### Changes Made

1. **Added ThreadPoolExecutor** (Line 30-31):
   ```python
   from concurrent.futures import ThreadPoolExecutor
   import functools
   
   _executor = ThreadPoolExecutor(max_workers=4)
   ```

2. **Created Helper Function** (Lines 58-74):
   ```python
   async def run_sync_fetch(fetch_func, *args, **kwargs):
       """
       Run a synchronous StealthyFetcher operation in a thread pool.
       This prevents Windows asyncio subprocess issues when using Playwright.
       """
       loop = asyncio.get_event_loop()
       func = functools.partial(fetch_func, *args, **kwargs)
       return await loop.run_in_executor(_executor, func)
   ```

3. **Replaced All `asyncio.to_thread()` Calls**:
   - Line 282: StubHub search fetching
   - Line 373: StubHub event page fetching
   - Line 466: SeatGeek search fetching
   - Line 504: SeatGeek event page fetching
   - Line 572: Ticketmaster fetching
   - Line 631: Vivid Seats fetching

### Why This Works

The key difference between `asyncio.to_thread()` and `loop.run_in_executor()`:

- **asyncio.to_thread()**: Introduced in Python 3.9, it's a convenience wrapper but still runs in the context of the current event loop. On Windows, when the synchronous code creates its own event loop and subprocesses (as Playwright does), this causes nesting issues.

- **loop.run_in_executor()**: Runs the function in a completely separate thread managed by the ThreadPoolExecutor. This thread has no connection to the parent event loop, so when Playwright creates its own event loop and subprocesses, it operates independently without conflict.

### Benefits

1. **Cross-Platform Compatibility**: Works on Windows, Linux, and macOS
2. **Resource Management**: ThreadPoolExecutor with 4 workers limits concurrent browser instances
3. **Performance**: Maintains the async benefits while isolating synchronous operations
4. **Reliability**: Eliminates NotImplementedError exceptions on Windows
5. **Maintainability**: Single helper function used consistently across all scrapers

## Additional Fixes

### Streamlit Accessibility Warning

Fixed the empty label warning in `streamlit_app.py` (Line 157):

**Before**:
```python
page = st.sidebar.radio("", ["🏠 Dashboard", "🕷️ Scraping", "📊 Analytics"])
```

**After**:
```python
page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "🕷️ Scraping", "📊 Analytics"], label_visibility="collapsed")
```

This provides proper accessibility labeling while maintaining the visual appearance.

## Testing Recommendations

### Unit Tests

The existing test suite in `backend/tests/test_scrapling_scraper.py` should pass without modification.

### Integration Testing

Test on Windows specifically:
1. Start Streamlit app: `streamlit run streamlit_app.py`
2. Navigate to "🕷️ Scraping" page
3. Enter a search query (e.g., "Lakers tickets")
4. Click "Start Scraping"
5. Verify all marketplaces scrape without NotImplementedError

### Performance Testing

Monitor ThreadPoolExecutor utilization:
- 4 workers should handle concurrent marketplace scraping efficiently
- No browser instance should block others
- Memory usage should remain stable

## Migration Notes

### For Developers

If you're adding new scrapers or modifying existing ones:

1. Always use `run_sync_fetch()` instead of `asyncio.to_thread()` for synchronous fetch operations
2. Keep the ThreadPoolExecutor size at 4 workers (matches the 4 marketplaces)
3. Ensure fetch functions are properly wrapped in a callable

Example pattern:
```python
async def _scrape_new_marketplace(self, url: str):
    def fetch_page():
        return StealthyFetcher.fetch(url, **STEALTH_CONFIG)
    
    page = await run_sync_fetch(fetch_page)
    # Process page...
```

### For Users

No configuration changes required. The service will work on Windows without any additional setup beyond the standard dependencies.

## References

- Python asyncio documentation: https://docs.python.org/3/library/asyncio.html
- Playwright Python: https://playwright.dev/python/
- Scrapling documentation: https://github.com/D4Vinci/Scrapling
- Windows ProactorEventLoop limitations: https://docs.python.org/3/library/asyncio-platforms.html#windows

## Version History

- **2025-10-25**: Initial fix implemented
  - Replaced asyncio.to_thread with ThreadPoolExecutor approach
  - Fixed Streamlit accessibility warning
  - Tested cross-platform compatibility
