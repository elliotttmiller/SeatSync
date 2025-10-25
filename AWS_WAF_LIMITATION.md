# StubHub Scraping AWS WAF Challenge - Known Limitation

## Problem
StubHub uses AWS WAF (Web Application Firewall) to protect against automated browsing. This protection actively detects and blocks automated browsers, even those using advanced stealth techniques like Scrapling.

## Symptoms
- "No Cloudflare challenge found" error (misleading - it's actually AWS WAF)
- AWS WAF challenge detected in page HTML
- Page returns 202 status but only contains challenge JavaScript
- Challenge page never resolves to actual content, even with extended wait times

## Technical Details

### What Happens
1. Browser requests StubHub page (e.g., `/minnesota-timberwolves-tickets`)
2. Server redirects to `/minnesota-timberwolves-tickets/performer/2986` (301 -> 202)
3. Server returns AWS WAF challenge page with JavaScript
4. Challenge JavaScript should:
   - Load AWS WAF token script
   - Execute AwsWafIntegration.getToken()
   - Reload the page with token
5. **But** AWS WAF detects automated browser and refuses to provide token

### Why It Happens
AWS WAF uses multiple detection techniques:
- Browser fingerprinting
- JavaScript behavior analysis
- TLS fingerprinting
- Mouse/keyboard interaction patterns
- Headless browser detection
- And more...

Even with Scrapling's advanced stealth features, AWS WAF can detect automation.

## Attempted Solutions

### What We Tried
- ✅ Removed incorrect `solve_cloudflare` usage (only works for Cloudflare)
- ✅ Increased wait times (3s -> 15s -> 20s -> 25s)
- ✅ Increased timeouts (30s -> 60s -> 90s -> 120s)
- ✅ Added `load_dom=True` for full JavaScript execution
- ✅ Used `page_action` callback to wait for page reload
- ✅ Tried `network_idle` to wait for network activity to complete
- ✅ Used stealth mode with humanization
- ✅ Disabled resource filtering to ensure full page load
- ❌ **Result**: AWS WAF still blocks access

### Why They Didn't Work
AWS WAF is specifically designed to detect and block all of these techniques. It's an arms race, and AWS WAF is currently winning.

## Recommended Solutions

### 1. Use Official APIs (RECOMMENDED)
**Best for production:**
- StubHub has official APIs for partners
- Reliable, legal, and supported
- No anti-bot issues
- Better data quality
- https://developer.stubhub.com/

### 2. Official Partnership
**For commercial use:**
- Partner with StubHub directly
- Get official API access
- Ensure compliance with terms of service

### 3. Alternative Marketplaces
**Easier to scrape:**
- SeatGeek (less restrictive)
- Ticketmaster (has API)
- Vivid Seats
- TickPick

### 4. Residential Proxies (Advanced)
**May help but not guaranteed:**
- Use residential IP addresses
- Rotate IPs frequently
- Still may be detected
- Can be expensive
- Check terms of service

### 5. Manual Data Collection
**For testing/development:**
- Use browser extensions
- Manual data export
- One-time data collection

## Current Implementation

### What We Provide
- ✅ Clear error messages explaining the limitation
- ✅ Proper status='error' when AWS WAF blocks
- ✅ Recommendations for alternative approaches
- ✅ Detailed logging for debugging
- ✅ Graceful failure handling

### Error Response
```python
{
    'status': 'error',
    'platform': 'stubhub',
    'error': 'AWS WAF protection blocked access',
    'message': 'StubHub uses AWS WAF which blocks automated browsers...',
    'recommendations': [
        'Use StubHub Official API (recommended)',
        'Try with residential IP addresses',
        'Use official partnership programs',
        'Contact StubHub for API access'
    ]
}
```

## For Developers

### Testing
If you need to test the application without StubHub access:
1. Use mock data for testing
2. Test with other marketplaces (SeatGeek, Ticketmaster)
3. Use VCR.py or similar to record/replay HTTP interactions
4. Create fixtures from manually collected data

### Production
For production use:
1. **DO NOT** rely on web scraping for StubHub
2. Use official APIs when available
3. Have fallback mechanisms
4. Monitor for changes in protection
5. Respect terms of service and robots.txt

## Legal and Ethical Considerations

### Terms of Service
- Web scraping may violate StubHub's terms of service
- Official APIs are the legal way to access data
- Review terms before deploying any solution

### Rate Limiting
- Even if scraping works, respect rate limits
- Avoid overwhelming servers
- Implement exponential backoff

### Robots.txt
- Check https://www.stubhub.com/robots.txt
- Respect the rules defined there

## Conclusion

AWS WAF protection on StubHub is working as intended - it blocks automated browsers. This is a **known limitation**, not a bug in our code. 

For production use, **use official APIs**. For development/testing, use alternative marketplaces or mock data.

## References

- AWS WAF Documentation: https://aws.amazon.com/waf/
- StubHub Developer Portal: https://developer.stubhub.com/
- Web Scraping Legal Guidelines: https://www.eff.org/issues/coders/reverse-engineering-faq
- Scrapling Documentation: https://github.com/D4Vinci/Scrapling

---
Last Updated: 2025-10-25
Status: AWS WAF blocks automated access (Expected Behavior)
