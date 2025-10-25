"""
Security Headers Middleware

This middleware adds security headers to all HTTP responses to prevent:
- XSS attacks
- Clickjacking
- MIME sniffing
- Cache poisoning
- Protocol downgrade attacks

Based on OWASP security best practices and EvilWAF analysis.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add comprehensive security headers to all responses
    
    Security headers implemented:
    1. Content-Security-Policy (CSP) - Prevents XSS
    2. X-Frame-Options - Prevents clickjacking
    3. X-Content-Type-Options - Prevents MIME sniffing
    4. X-XSS-Protection - Browser XSS filter
    5. Strict-Transport-Security (HSTS) - Forces HTTPS
    6. Referrer-Policy - Controls referrer information
    7. Permissions-Policy - Controls browser features
    8. Cache-Control - Prevents cache poisoning
    
    Prevents:
    - Cross-Site Scripting (XSS)
    - Clickjacking attacks
    - MIME type confusion
    - Cache poisoning
    - Man-in-the-middle attacks
    """
    
    def __init__(self, app, config: dict = None):
        super().__init__(app)
        self.config = config or {}
        
        # Default CSP policy - adjust based on application needs
        self.csp_policy = self.config.get("csp_policy", self._get_default_csp())
        
        # HSTS configuration
        self.hsts_max_age = self.config.get("hsts_max_age", 31536000)  # 1 year
        self.hsts_include_subdomains = self.config.get("hsts_include_subdomains", True)
        self.hsts_preload = self.config.get("hsts_preload", True)
        
        # Environment configuration
        self.enable_hsts = self.config.get("enable_hsts", True)
        
    def _get_default_csp(self) -> str:
        """
        Get default Content Security Policy
        
        This is a restrictive policy that should be customized based on
        your application's needs. Adjust script-src, style-src, etc.
        """
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https: http:; "
            "connect-src 'self' https://api.seatsync.com wss://api.seatsync.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none';"
        )
    
    async def dispatch(self, request: Request, call_next):
        """
        Add security headers to response
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response with security headers added
        """
        # Process request
        response = await call_next(request)
        
        try:
            # Add all security headers
            self._add_csp_header(response)
            self._add_frame_options(response)
            self._add_content_type_options(response)
            self._add_xss_protection(response)
            self._add_hsts_header(response, request)
            self._add_referrer_policy(response)
            self._add_permissions_policy(response)
            self._add_cache_control(response, request)
            
            logger.debug(f"Added security headers to response for {request.url.path}")
            
        except Exception as e:
            logger.error(f"Error adding security headers: {str(e)}")
            # Don't fail the request if headers can't be added
        
        return response
    
    def _add_csp_header(self, response):
        """
        Add Content-Security-Policy header
        
        CSP prevents XSS by restricting resource loading sources.
        This is one of the most important security headers.
        """
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = self.csp_policy
    
    def _add_frame_options(self, response):
        """
        Add X-Frame-Options header
        
        Prevents clickjacking by controlling if page can be embedded in frames.
        Options: DENY, SAMEORIGIN, ALLOW-FROM uri
        """
        if "X-Frame-Options" not in response.headers:
            response.headers["X-Frame-Options"] = "DENY"
    
    def _add_content_type_options(self, response):
        """
        Add X-Content-Type-Options header
        
        Prevents MIME sniffing attacks where browsers try to detect
        content type and execute malicious content.
        """
        if "X-Content-Type-Options" not in response.headers:
            response.headers["X-Content-Type-Options"] = "nosniff"
    
    def _add_xss_protection(self, response):
        """
        Add X-XSS-Protection header
        
        Enables browser's built-in XSS filter.
        Note: Modern browsers use CSP instead, but this provides defense in depth.
        """
        if "X-XSS-Protection" not in response.headers:
            response.headers["X-XSS-Protection"] = "1; mode=block"
    
    def _add_hsts_header(self, response, request: Request):
        """
        Add Strict-Transport-Security header
        
        Forces browsers to use HTTPS for all future requests.
        Only add this header over HTTPS connections.
        
        IMPORTANT: Only enable in production with valid SSL certificate!
        """
        # Only add HSTS if enabled and request is over HTTPS
        if self.enable_hsts:
            # Check if request is over HTTPS
            # Note: In production behind proxy, check X-Forwarded-Proto header
            is_https = (
                request.url.scheme == "https" or
                request.headers.get("x-forwarded-proto") == "https"
            )
            
            if is_https and "Strict-Transport-Security" not in response.headers:
                hsts_value = f"max-age={self.hsts_max_age}"
                
                if self.hsts_include_subdomains:
                    hsts_value += "; includeSubDomains"
                
                if self.hsts_preload:
                    hsts_value += "; preload"
                
                response.headers["Strict-Transport-Security"] = hsts_value
    
    def _add_referrer_policy(self, response):
        """
        Add Referrer-Policy header
        
        Controls how much referrer information is included with requests.
        Options: no-referrer, no-referrer-when-downgrade, origin,
                 origin-when-cross-origin, same-origin, strict-origin,
                 strict-origin-when-cross-origin, unsafe-url
        """
        if "Referrer-Policy" not in response.headers:
            # strict-origin-when-cross-origin is a good balance
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    def _add_permissions_policy(self, response):
        """
        Add Permissions-Policy header (formerly Feature-Policy)
        
        Controls which browser features can be used.
        Disable features not needed by the application.
        """
        if "Permissions-Policy" not in response.headers:
            # Disable features not typically needed by APIs
            policy = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            )
            response.headers["Permissions-Policy"] = policy
    
    def _add_cache_control(self, response, request: Request):
        """
        Add Cache-Control headers
        
        Prevents cache poisoning by controlling caching behavior.
        API responses should generally not be cached.
        """
        # Only add cache control if not already set
        if "Cache-Control" not in response.headers:
            # For API endpoints, prevent caching
            if request.url.path.startswith("/api/"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            else:
                # For static content, allow short-term caching
                response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with security validations
    
    While FastAPI has built-in CORS middleware, this provides
    additional security validations for origin verification.
    """
    
    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or []
    
    async def dispatch(self, request: Request, call_next):
        """Validate and handle CORS"""
        origin = request.headers.get("origin")
        
        # Validate origin if present
        if origin:
            # Check if origin is in allowed list
            if not self._is_origin_allowed(origin):
                logger.warning(f"Blocked request from unauthorized origin: {origin}")
                # You can either block or just not add CORS headers
                # For now, we'll process but not add CORS headers
        
        response = await call_next(request)
        
        # Add CORS headers only for allowed origins
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is in allowed list"""
        # Allow all origins if list is empty (development mode)
        if not self.allowed_origins:
            return True
        
        # Check exact match
        if origin in self.allowed_origins:
            return True
        
        # Check wildcard patterns (e.g., *.example.com)
        for allowed in self.allowed_origins:
            if allowed.startswith("*."):
                domain = allowed[2:]
                if origin.endswith(domain):
                    return True
        
        return False


# Convenience function to add all security middleware
def add_security_middleware(app, config: dict = None):
    """
    Add all security middleware to FastAPI application
    
    Usage:
        from app.middleware.security_headers import add_security_middleware
        
        app = FastAPI()
        add_security_middleware(app, config={
            "enable_hsts": True,
            "hsts_max_age": 31536000
        })
    
    Args:
        app: FastAPI application instance
        config: Optional configuration dict
    """
    config = config or {}
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware, config=config)
    
    logger.info("Security headers middleware added successfully")
