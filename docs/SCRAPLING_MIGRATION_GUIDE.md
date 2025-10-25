# Scrapling Migration Guide

**Version:** 1.0  
**Date:** October 23, 2025  
**Status:** Implementation Ready

This guide provides step-by-step instructions for migrating from the current Playwright-based web scraping implementation to Scrapling.

---

## Prerequisites

Before starting the migration:

1. **Python 3.10+** (Scrapling requirement)
2. **Backup current implementation** (already done via git)
3. **Review analysis document** (`SCRAPLING_ANALYSIS.md`)
4. **Team alignment** on migration decision

---

## Phase 1: Parallel Implementation (Week 1-2)

This phase allows running both implementations side-by-side with minimal risk.

### Step 1: Install Scrapling

```bash
# Option A: Install as optional dependency (recommended for testing)
pip install "scrapling[all]>=0.3.7"

# Option B: Add to requirements.txt (for production)
echo "scrapling[all]>=0.3.7" >> backend/requirements.txt
pip install -r backend/requirements.txt

# Install browsers (required)
scrapling install
```

**Verification:**
```bash
python -c "from scrapling.fetchers import StealthyFetcher; print('✅ Scrapling installed')"
```

### Step 2: Enable Feature Flag

```bash
# Development/Testing
export USE_SCRAPLING=true

# Or in .env file
echo "USE_SCRAPLING=true" >> .env

# Production (when ready)
# Set in your deployment configuration
```

### Step 3: Run Tests

```bash
# Run both test suites
pytest backend/tests/test_scraping_service.py -v
pytest backend/tests/test_scrapling_service.py -v
```

**Expected Results:**
- ✅ Old tests still pass
- ✅ New Scrapling tests pass (or skip if not installed)
- ✅ No breaking changes

### Step 4: Test Single Marketplace

Start with ONE marketplace to validate the implementation:

```python
# Test script: test_scrapling_stubhub.py
import asyncio
from backend.app.services.scrapling_service import scrape_tickets_scrapling

async def test():
    result = await scrape_tickets_scrapling(
        marketplace="stubhub",
        search_query="Lakers tickets"
    )
    
    print(f"Status: {result['status']}")
    print(f"Listings found: {result['count']}")
    print(f"Platform: {result['platform']}")
    print(f"Scraper: {result.get('scraper', 'unknown')}")
    
    if result['listings']:
        print(f"Sample listing: {result['listings'][0]}")

asyncio.run(test())
```

**Run it:**
```bash
cd /home/runner/work/SeatSync/SeatSync
python test_scrapling_stubhub.py
```

**Validation Checklist:**
- [ ] Script runs without errors
- [ ] Returns valid data structure
- [ ] Listings extracted correctly
- [ ] Performance is acceptable
- [ ] No asyncio warnings (compared to old implementation)

### Step 5: Compare Performance

Create a comparison script:

```python
# compare_scrapers.py
import asyncio
import time
from backend.app.services.scraping_service import scrape_tickets
from backend.app.services.scrapling_service import scrape_tickets_scrapling

async def benchmark_scraper(scraper_func, name):
    start = time.time()
    result = await scraper_func(
        marketplace="stubhub",
        search_query="Lakers tickets"
    )
    elapsed = time.time() - start
    
    print(f"\n{name} Results:")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Status: {result['status']}")
    print(f"  Listings: {result.get('count', 0)}")
    return elapsed, result

async def main():
    print("=== Scraper Performance Comparison ===\n")
    
    # Test old implementation
    old_time, old_result = await benchmark_scraper(scrape_tickets, "OLD (Playwright)")
    
    # Test new implementation
    new_time, new_result = await benchmark_scraper(scrape_tickets_scrapling, "NEW (Scrapling)")
    
    # Compare
    print(f"\n=== Comparison ===")
    print(f"Speed improvement: {old_time/new_time:.2f}x faster" if new_time < old_time else f"{new_time/old_time:.2f}x slower")
    print(f"Old success: {old_result['status'] == 'success'}")
    print(f"New success: {new_result['status'] == 'success'}")

asyncio.run(main())
```

**Run comparison:**
```bash
python compare_scrapers.py
```

### Step 6: Test All Marketplaces

Once StubHub works, test others:

```python
# test_all_marketplaces.py
import asyncio
from backend.app.services.scrapling_service import scrape_tickets_scrapling

async def test_marketplace(name):
    print(f"\nTesting {name}...")
    result = await scrape_tickets_scrapling(
        marketplace=name,
        search_query="concert tickets"
    )
    print(f"  Status: {result['status']}")
    print(f"  Listings: {result.get('count', 0)}")
    return result

async def main():
    marketplaces = ["stubhub", "seatgeek", "ticketmaster", "vividseats"]
    
    for marketplace in marketplaces:
        try:
            await test_marketplace(marketplace)
        except Exception as e:
            print(f"  ❌ Error: {e}")

asyncio.run(main())
```

---

## Phase 2: A/B Testing (Week 2-3)

Monitor both implementations in production to validate the migration.

### Step 1: Deploy with Feature Flag

```yaml
# docker-compose.yml or kubernetes config
environment:
  - USE_SCRAPLING=true  # Enable for canary deployment
```

### Step 2: Monitor Metrics

Track these metrics for comparison:

```python
# Add to scraping service
class ScrapingMetrics:
    def __init__(self):
        self.metrics = {
            'old': {'success': 0, 'failure': 0, 'avg_time': 0},
            'new': {'success': 0, 'failure': 0, 'avg_time': 0}
        }
    
    def record(self, scraper_type, success, duration):
        m = self.metrics[scraper_type]
        if success:
            m['success'] += 1
        else:
            m['failure'] += 1
        m['avg_time'] = (m['avg_time'] + duration) / 2
    
    def get_report(self):
        return self.metrics
```

**Key Metrics to Track:**
1. **Success Rate**: % of successful scrapes
2. **Performance**: Average response time
3. **Error Rate**: % of failures
4. **Data Quality**: Completeness of extracted data
5. **Maintenance**: Time spent fixing issues

### Step 3: Gradual Rollout

```python
# Gradually increase Scrapling usage
import random

# Week 1: 10% of traffic
USE_SCRAPLING = random.random() < 0.10

# Week 2: 50% of traffic
USE_SCRAPLING = random.random() < 0.50

# Week 3: 100% of traffic
USE_SCRAPLING = True
```

---

## Phase 3: Full Migration (Week 4-6)

Once A/B testing shows positive results, proceed with full migration.

### Step 1: Update Default Configuration

```python
# .env.production
USE_SCRAPLING=true
```

### Step 2: Remove Old Code (Optional)

**Only do this after 2-4 weeks of stable operation!**

```bash
# Backup first
git checkout -b backup-old-scrapers

# Remove old implementations
rm backend/app/services/enhanced_scraping.py
rm backend/app/services/advanced_ticket_scraper.py

# Update imports in scraping_service.py
# Remove fallback logic if desired
```

### Step 3: Update Documentation

Update these files:
- [x] `README.md` - Mention Scrapling
- [x] `SCRAPING_GUIDE.md` - Update with Scrapling instructions
- [ ] API documentation - Update scraping endpoints
- [ ] Team wiki - Add Scrapling usage guide

### Step 4: Optimize for Scrapling

Take advantage of Scrapling's unique features:

#### Enable Adaptive Tracking

```python
# In production scraping
result = await scrape_tickets_scrapling(
    marketplace="stubhub",
    search_query="Lakers",
    adaptive=False  # First scrape - save selectors
)

# When website structure changes
result = await scrape_tickets_scrapling(
    marketplace="stubhub",
    search_query="Lakers",
    adaptive=True  # Find elements automatically!
)
```

#### Use Session for Multiple Requests

```python
from scrapling.fetchers import StealthySession

async with StealthySession(headless=True) as session:
    # Reuse browser session for multiple requests
    for url in urls:
        page = session.fetch(url)
        # Process page...
```

#### Enable Advanced Features

```python
# Cloudflare bypass
page = StealthyFetcher.fetch(
    url,
    solve_cloudflare=True,  # Auto-bypass!
    headless=True
)

# TLS fingerprinting
page = Fetcher.get(
    url,
    impersonate='chrome',  # Impersonate Chrome's TLS fingerprint
    stealthy_headers=True
)
```

---

## Phase 4: Advanced Features (Week 6+)

Leverage Scrapling's unique capabilities.

### Adaptive Element Tracking

Implement a monitoring system to detect when websites change:

```python
class AdaptiveScrapingMonitor:
    def __init__(self):
        self.failed_selectors = {}
    
    async def scrape_with_adaptation(self, marketplace, query):
        # Try normal scraping first
        result = await scrape_tickets_scrapling(
            marketplace=marketplace,
            search_query=query,
            adaptive=False
        )
        
        # If no results or low count, try adaptive
        if result['count'] < 5:
            result = await scrape_tickets_scrapling(
                marketplace=marketplace,
                search_query=query,
                adaptive=True  # Adapt to changes!
            )
            
            if result['count'] > 5:
                # Adaptive mode found results!
                # Log for investigation
                logger.warning(f"{marketplace} structure may have changed")
                self.failed_selectors[marketplace] = datetime.now()
        
        return result
```

### Interactive Development Shell

Use Scrapling's built-in shell for development:

```bash
# Launch interactive shell
scrapling shell

# Inside shell:
>>> page = fetch('https://stubhub.com')
>>> listings = page.css('.listing')
>>> print(f"Found {len(listings)} listings")
>>> browser(page)  # View in browser!
```

### CLI for Quick Testing

```bash
# Extract data without writing code
scrapling extract stealthy-fetch 'https://stubhub.com/event/xyz' output.html \
  --css-selector '.listing' \
  --solve-cloudflare

# View results
cat output.html
```

---

## Rollback Plan

If issues arise, rollback is simple:

### Immediate Rollback (< 5 minutes)

```bash
# Disable Scrapling
export USE_SCRAPLING=false

# Or in production config
kubectl set env deployment/seatsync USE_SCRAPLING=false

# Restart services
kubectl rollout restart deployment/seatsync
```

The old implementation remains intact and will take over immediately.

### Code Rollback

```bash
# Revert to previous commit
git revert HEAD

# Or restore from backup branch
git checkout main
git reset --hard backup-old-scrapers
```

---

## Troubleshooting

### Issue: "Scrapling not available"

**Solution:**
```bash
pip install "scrapling[all]>=0.3.7"
scrapling install
```

### Issue: Browser not found

**Solution:**
```bash
scrapling install  # Downloads all browsers
```

### Issue: Cloudflare blocks requests

**Solution:**
```python
# Enable Cloudflare bypass
page = StealthyFetcher.fetch(
    url,
    solve_cloudflare=True,
    google_search=False
)
```

### Issue: Selectors not finding elements

**Solution:**
```python
# Use adaptive mode
elements = page.css('.listing', adaptive=True)

# Or try alternative selectors
elements = page.find_by_text('Buy Tickets', tag='button')
```

### Issue: Performance slower than expected

**Solution:**
```python
# Disable resource loading for faster scraping
page = DynamicFetcher.fetch(
    url,
    headless=True,
    disable_resources=True,  # Skip images/CSS
    network_idle=False  # Don't wait for all resources
)
```

### Issue: Memory usage high

**Solution:**
```python
# Use session pooling
async with StealthySession(max_pages=2) as session:
    # Limits to 2 concurrent pages
    pass
```

---

## Testing Checklist

Before declaring migration complete, verify:

### Functional Testing
- [ ] All marketplaces scrape successfully
- [ ] Data format matches old implementation
- [ ] Error handling works correctly
- [ ] Feature flag switches between implementations
- [ ] Adaptive mode finds elements after website changes

### Performance Testing
- [ ] Response time acceptable (< 10s per scrape)
- [ ] Memory usage stable
- [ ] No asyncio warnings (compared to old)
- [ ] Concurrent scraping works

### Integration Testing
- [ ] API endpoints work with Scrapling
- [ ] Database stores data correctly
- [ ] Frontend displays data properly
- [ ] Analytics pipeline processes data

### Production Readiness
- [ ] Monitoring alerts configured
- [ ] Logging set up properly
- [ ] Error tracking enabled
- [ ] Documentation updated
- [ ] Team trained on Scrapling

---

## Success Criteria

Migration is successful when:

1. ✅ **Success Rate > 95%** for all marketplaces
2. ✅ **Performance improvement** (any improvement is good; 10x+ is excellent)
3. ✅ **Zero critical bugs** in production for 2 weeks
4. ✅ **Reduced maintenance time** (fewer selector updates)
5. ✅ **Team comfortable** with Scrapling API

---

## Timeline Summary

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| **Phase 1: Setup** | Week 1-2 | Install, test single marketplace, validate |
| **Phase 2: A/B Test** | Week 2-3 | Gradual rollout, monitor metrics |
| **Phase 3: Migration** | Week 4-6 | Full rollout, optimize, cleanup |
| **Phase 4: Advanced** | Week 6+ | Leverage unique features |

**Total: 6-8 weeks** for complete migration with low risk

---

## Support Resources

### Documentation
- Scrapling Docs: https://scrapling.readthedocs.io/
- Migration Issues: File in GitHub repo

### Community
- Discord: https://discord.gg/EMgGbDceNQ
- GitHub Issues: https://github.com/D4Vinci/Scrapling/issues

### Internal
- Analysis: `SCRAPLING_ANALYSIS.md`
- Implementation: `backend/app/services/scrapling_service.py`
- Tests: `backend/tests/test_scrapling_service.py`

---

## Next Steps

1. **Review this guide** with the team
2. **Allocate time** for migration (6-8 weeks)
3. **Start Phase 1** when ready
4. **Monitor metrics** throughout
5. **Iterate and improve** based on results

---

**Document Version:** 1.0  
**Last Updated:** October 23, 2025  
**Status:** READY FOR IMPLEMENTATION
