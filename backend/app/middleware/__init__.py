"""
Security Middleware Package

This package contains middleware components for securing the SeatSync API.

Components:
- jwt_security: Enhanced JWT token validation
- request_validator: HTTP request validation and smuggling prevention
- security_headers: Security headers for all responses

Based on security analysis of EvilWAF attack vectors.
"""

from .request_validator import RequestValidationMiddleware, RequestSizeLimiter
from .security_headers import SecurityHeadersMiddleware, CORSSecurityMiddleware, add_security_middleware

__all__ = [
    "RequestValidationMiddleware",
    "RequestSizeLimiter",
    "SecurityHeadersMiddleware",
    "CORSSecurityMiddleware",
    "add_security_middleware",
]
