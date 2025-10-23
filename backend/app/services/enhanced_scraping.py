"""
Enhanced Web Scraping Implementation
State-of-the-Art Ticket Data Collection System

Based on comprehensive research from:
- Marketscrape web scraping best practices
- CS109 SeatGeek data collection methodologies
- Industry-leading anti-detection techniques

Features:
- Advanced proxy rotation with residential/datacenter proxies
- Browser fingerprint randomization
- Intelligent CAPTCHA detection and handling
- Adaptive rate limiting based on response patterns
- Distributed scraping architecture
- Data validation and quality assurance
"""

import asyncio
import logging
import random
import hashlib
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Define stub types for type hints when Playwright is not available
    Browser = None  # type: ignore
    Page = None  # type: ignore
    BrowserContext = None  # type: ignore

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    """Structured result from scraping operation"""
    platform: str
    status: str
    listings: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'platform': self.platform,
            'status': self.status,
            'listings': self.listings,
            'count': len(self.listings),
            'metadata': self.metadata,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat()
        }


class ProxyRotator:
    """
    Advanced proxy rotation system
    Supports multiple proxy types and automatic failure handling
    """
    
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_stats = {}
        
    def add_proxy(self, proxy: str, proxy_type: str = 'http'):
        """Add a proxy to the pool"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.proxy_stats[proxy] = {
                'type': proxy_type,
                'success_count': 0,
                'failure_count': 0,
                'last_used': None,
                'avg_response_time': 0
            }
    
    def get_next(self) -> Optional[Dict[str, str]]:
        """Get next available proxy"""
        if not self.proxies:
            return None
        
        # Filter out failed proxies
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available_proxies:
            # Reset if all proxies have failed
            self.failed_proxies.clear()
            available_proxies = self.proxies
        
        # Select proxy (weighted by success rate)
        proxy = self._select_best_proxy(available_proxies)
        
        if proxy:
            return {
                'server': proxy,
                'username': None,  # Add if needed
                'password': None   # Add if needed
            }
        return None
    
    def _select_best_proxy(self, proxies: List[str]) -> Optional[str]:
        """Select best performing proxy"""
        if not proxies:
            return None
        
        # Calculate scores for each proxy
        scored_proxies = []
        for proxy in proxies:
            stats = self.proxy_stats.get(proxy, {})
            success = stats.get('success_count', 0)
            failure = stats.get('failure_count', 0)
            total = success + failure
            
            if total == 0:
                score = 1.0  # Untested proxy gets default score
            else:
                score = success / total
            
            scored_proxies.append((proxy, score))
        
        # Sort by score and select top one
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        return scored_proxies[0][0]
    
    def mark_success(self, proxy: str, response_time: float = 0):
        """Mark proxy as successful"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats['success_count'] += 1
            stats['last_used'] = datetime.utcnow()
            
            # Update average response time
            if stats['avg_response_time'] == 0:
                stats['avg_response_time'] = response_time
            else:
                stats['avg_response_time'] = (stats['avg_response_time'] + response_time) / 2
    
    def mark_failure(self, proxy: str):
        """Mark proxy as failed"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats['failure_count'] += 1
            
            # Remove from pool if too many failures
            if stats['failure_count'] > 5:
                self.failed_proxies.add(proxy)


class BrowserFingerprintRandomizer:
    """
    Randomize browser fingerprints to avoid detection
    Based on research from anti-bot detection systems
    """
    
    SCREEN_RESOLUTIONS = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900},
        {'width': 2560, 'height': 1440}
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    PLATFORMS = ['Win32', 'MacIntel', 'Linux x86_64']
    
    LANGUAGES = ['en-US', 'en-GB', 'en-CA']
    
    TIMEZONES = [
        'America/New_York',
        'America/Chicago', 
        'America/Denver',
        'America/Los_Angeles',
        'America/Toronto'
    ]
    
    @classmethod
    def get_random_fingerprint(cls) -> Dict[str, Any]:
        """Generate a random but realistic browser fingerprint"""
        screen = random.choice(cls.SCREEN_RESOLUTIONS)
        
        return {
            'user_agent': random.choice(cls.USER_AGENTS),
            'viewport': screen,
            'screen': screen,
            'platform': random.choice(cls.PLATFORMS),
            'locale': random.choice(cls.LANGUAGES),
            'timezone': random.choice(cls.TIMEZONES),
            'color_depth': random.choice([24, 32]),
            'device_memory': random.choice([4, 8, 16]),
            'hardware_concurrency': random.choice([4, 8, 12, 16])
        }


class AdaptiveRateLimiter:
    """
    Intelligent rate limiting that adapts to server responses
    Implements exponential backoff and traffic shaping
    """
    
    def __init__(
        self, 
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        requests_per_minute: int = 30
    ):
        self.base_delay = base_delay
        self.current_delay = base_delay
        self.max_delay = max_delay
        self.requests_per_minute = requests_per_minute
        self.last_request_time = None
        self.request_times = []
        self.consecutive_errors = 0
        
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.utcnow()
        
        # Clean up old request times (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        self.request_times = [t for t in self.request_times if t > cutoff]
        
        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_minute:
            # Wait until oldest request is > 1 minute old
            oldest = min(self.request_times)
            wait_time = 60 - (now - oldest).total_seconds()
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Add jitter to avoid thundering herd
        jitter = random.uniform(0, self.current_delay * 0.2)
        await asyncio.sleep(self.current_delay + jitter)
        
        # Record this request
        self.request_times.append(datetime.utcnow())
        self.last_request_time = datetime.utcnow()
    
    def on_success(self):
        """Called when request succeeds - decrease delay"""
        self.consecutive_errors = 0
        # Gradually reduce delay back to base
        self.current_delay = max(
            self.base_delay,
            self.current_delay * 0.9
        )
    
    def on_error(self, status_code: Optional[int] = None):
        """Called when request fails - increase delay"""
        self.consecutive_errors += 1
        
        # Exponential backoff
        if status_code == 429:  # Rate limited
            self.current_delay = min(
                self.max_delay,
                self.current_delay * 2
            )
        elif status_code and status_code >= 500:  # Server error
            self.current_delay = min(
                self.max_delay,
                self.current_delay * 1.5
            )
        else:  # Other error
            self.current_delay = min(
                self.max_delay,
                self.current_delay * 1.2
            )
        
        logger.warning(
            f"Error detected, increased delay to {self.current_delay:.2f}s "
            f"(consecutive errors: {self.consecutive_errors})"
        )


class CaptchaDetector:
    """
    Detect CAPTCHA challenges on pages
    """
    
    CAPTCHA_INDICATORS = [
        'captcha',
        'recaptcha',
        'hcaptcha',
        'challenge',
        'robot',
        'verify you are human',
        'security check'
    ]
    
    @classmethod
    async def detect_captcha(cls, page: Page) -> bool:
        """Detect if page contains a CAPTCHA"""
        try:
            # Check page title
            title = await page.title()
            if any(indicator in title.lower() for indicator in cls.CAPTCHA_INDICATORS):
                return True
            
            # Check page content
            content = await page.content()
            content_lower = content.lower()
            if any(indicator in content_lower for indicator in cls.CAPTCHA_INDICATORS):
                return True
            
            # Check for common CAPTCHA elements
            captcha_elements = await page.query_selector_all(
                'iframe[src*="captcha"], iframe[src*="recaptcha"], div[id*="captcha"]'
            )
            if captcha_elements:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return False


class DataValidator:
    """
    Validate and sanitize scraped data
    Ensure data quality and consistency
    """
    
    @staticmethod
    def validate_price(price: Any) -> Optional[float]:
        """Validate and normalize price"""
        try:
            if price is None:
                return None
            
            # Convert to float
            if isinstance(price, str):
                # Remove currency symbols and commas
                price = price.replace('$', '').replace(',', '').replace('€', '').replace('£', '')
                price = float(price)
            else:
                price = float(price)
            
            # Validate range (tickets typically $1 - $10,000)
            if 1 <= price <= 10000:
                return round(price, 2)
            
            return None
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_listing(listing: Dict[str, Any]) -> bool:
        """Validate a listing has required fields"""
        required_fields = ['price', 'platform']
        
        # Check required fields
        for field in required_fields:
            if field not in listing:
                return False
        
        # Validate price
        price = DataValidator.validate_price(listing.get('price'))
        if price is None:
            return False
        
        listing['price'] = price
        return True
    
    @staticmethod
    def normalize_listing(listing: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize listing data to standard format"""
        normalized = {
            'price': DataValidator.validate_price(listing.get('price')),
            'platform': listing.get('platform', 'unknown').lower(),
            'section': listing.get('section', '').strip(),
            'row': listing.get('row', '').strip(),
            'seat': listing.get('seat', '').strip(),
            'quantity': int(listing.get('quantity', 1)),
            'currency': listing.get('currency', 'USD'),
            'listing_id': listing.get('listing_id', ''),
            'url': listing.get('url', ''),
            'timestamp': listing.get('timestamp', datetime.utcnow().isoformat())
        }
        
        # Calculate a unique hash for deduplication
        hash_input = f"{normalized['platform']}_{normalized['price']}_{normalized['section']}_{normalized['row']}"
        normalized['hash'] = hashlib.md5(hash_input.encode()).hexdigest()
        
        return normalized


class EnhancedScrapingEngine:
    """
    State-of-the-art web scraping engine
    Combines all advanced techniques for optimal data collection
    """
    
    def __init__(self):
        self.proxy_rotator = ProxyRotator()
        self.fingerprint_randomizer = BrowserFingerprintRandomizer()
        self.rate_limiter = AdaptiveRateLimiter(
            base_delay=2.0,
            requests_per_minute=30
        )
        self.captcha_detector = CaptchaDetector()
        self.data_validator = DataValidator()
        
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.scraping_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'captcha_encounters': 0,
            'total_listings': 0
        }
    
    async def initialize(self) -> bool:
        """Initialize the scraping engine"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return False
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with anti-detection settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            logger.info("Enhanced scraping engine initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize scraping engine: {e}")
            return False
    
    async def create_stealth_context(self) -> Optional[BrowserContext]:
        """Create a browser context with stealth settings"""
        if not self.browser:
            return None
        
        try:
            # Get random fingerprint
            fingerprint = self.fingerprint_randomizer.get_random_fingerprint()
            
            # Get proxy if available
            proxy = self.proxy_rotator.get_next()
            
            # Create context
            context = await self.browser.new_context(
                user_agent=fingerprint['user_agent'],
                viewport=fingerprint['viewport'],
                screen=fingerprint['screen'],
                locale=fingerprint['locale'],
                timezone_id=fingerprint['timezone'],
                proxy=proxy
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Add chrome object
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create stealth context: {e}")
            return None
    
    async def scrape_with_retry(
        self,
        scraper_func: Callable,
        max_retries: int = 3,
        *args,
        **kwargs
    ) -> ScrapingResult:
        """
        Execute scraper with retry logic and error handling
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self.scraping_stats['total_requests'] += 1
                
                # Rate limiting
                await self.rate_limiter.wait_if_needed()
                
                # Execute scraper
                result = await scraper_func(*args, **kwargs)
                
                # Update stats
                if result.status == 'success':
                    self.scraping_stats['successful_requests'] += 1
                    self.scraping_stats['total_listings'] += len(result.listings)
                    self.rate_limiter.on_success()
                    return result
                else:
                    self.scraping_stats['failed_requests'] += 1
                    self.rate_limiter.on_error()
                    last_error = result.errors
                
            except Exception as e:
                logger.error(f"Scraping attempt {attempt + 1} failed: {e}")
                last_error = str(e)
                self.scraping_stats['failed_requests'] += 1
                self.rate_limiter.on_error()
                
                # Wait before retry with exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        
        # All retries failed
        return ScrapingResult(
            platform='unknown',
            status='error',
            listings=[],
            errors=[f"All {max_retries} attempts failed: {last_error}"]
        )
    
    async def close(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        logger.info(f"Scraping engine closed. Stats: {self.scraping_stats}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        total = self.scraping_stats['total_requests']
        success_rate = (
            self.scraping_stats['successful_requests'] / total * 100
            if total > 0 else 0
        )
        
        return {
            **self.scraping_stats,
            'success_rate': round(success_rate, 2)
        }


# Global instance
_scraping_engine = None

async def get_scraping_engine() -> EnhancedScrapingEngine:
    """Get or create the global scraping engine instance"""
    global _scraping_engine
    
    if _scraping_engine is None:
        _scraping_engine = EnhancedScrapingEngine()
        await _scraping_engine.initialize()
    
    return _scraping_engine
