"""
Request Validation Middleware

This middleware implements comprehensive HTTP request validation to prevent:
- HTTP request smuggling attacks
- Malformed requests
- Oversized requests
- Header injection attacks
- Suspicious patterns

Based on security analysis of EvilWAF attack vectors.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates HTTP requests to prevent smuggling and malformed requests
    
    Security validations performed:
    1. URI length validation
    2. Content-Length validation
    3. Transfer-Encoding validation
    4. Conflicting header detection
    5. HTTP method validation
    6. Header size limits
    7. Suspicious pattern detection
    8. Host header validation
    9. Duplicate header detection
    
    Prevents:
    - HTTP request smuggling (CL.TE, TE.CL attacks)
    - Header injection attacks
    - Oversized request attacks
    - Protocol confusion attacks
    """
    
    # Configuration - adjust based on application needs
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    MAX_HEADER_SIZE = 8 * 1024  # 8KB per header
    MAX_TOTAL_HEADER_SIZE = 32 * 1024  # 32KB total headers
    MAX_URI_LENGTH = 2048
    
    # Suspicious patterns that may indicate attacks
    SUSPICIOUS_PATTERNS = [
        r"[\x00-\x08\x0B\x0C\x0E-\x1F]",  # Control characters (except \t, \n, \r)
        r"\r\n\s+\r\n",  # Request smuggling pattern
        r"Transfer-Encoding:.*Transfer-Encoding:",  # Duplicate Transfer-Encoding
        r"Content-Length:.*Content-Length:",  # Duplicate Content-Length
    ]
    
    # Allowed HTTP methods
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    
    # Valid Transfer-Encoding values
    VALID_ENCODINGS = ["chunked", "compress", "deflate", "gzip", "identity"]
    
    async def dispatch(self, request: Request, call_next):
        """
        Validate request before processing
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response from next middleware
            
        Raises:
            HTTPException: If validation fails
        """
        try:
            # VALIDATION 1: URI Length
            self._validate_uri_length(request)
            
            # VALIDATION 2: Content-Length
            self._validate_content_length(request)
            
            # VALIDATION 3: Check for conflicting headers (CL.TE attack)
            self._validate_conflicting_headers(request)
            
            # VALIDATION 4: Transfer-Encoding validation
            self._validate_transfer_encoding(request)
            
            # VALIDATION 5: HTTP Method
            self._validate_http_method(request)
            
            # VALIDATION 6: Header sizes
            self._validate_header_sizes(request)
            
            # VALIDATION 7: Suspicious patterns
            self._detect_suspicious_patterns(request)
            
            # VALIDATION 8: Host header
            self._validate_host_header(request)
            
            # VALIDATION 9: Duplicate critical headers
            self._validate_duplicate_headers(request)
            
            # All validations passed
            logger.debug(f"Request validated: {request.method} {request.url.path}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request validation error"
            )
        
        # Process request
        response = await call_next(request)
        return response
    
    def _validate_uri_length(self, request: Request):
        """Validate URI length to prevent buffer overflow attacks"""
        uri = str(request.url)
        if len(uri) > self.MAX_URI_LENGTH:
            logger.warning(f"URI too long: {len(uri)} bytes")
            raise HTTPException(
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                detail=f"URI exceeds maximum length of {self.MAX_URI_LENGTH} characters"
            )
    
    def _validate_content_length(self, request: Request):
        """
        Validate Content-Length header
        
        Prevents: Oversized request attacks, negative length attacks
        """
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                length = int(content_length)
                
                # Check for negative values
                if length < 0:
                    logger.warning(f"Negative Content-Length: {length}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Content-Length: negative value"
                    )
                
                # Check maximum size
                if length > self.MAX_CONTENT_LENGTH:
                    logger.warning(f"Content-Length too large: {length} bytes")
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request body exceeds maximum size of {self.MAX_CONTENT_LENGTH} bytes"
                    )
                    
            except ValueError:
                logger.warning(f"Invalid Content-Length value: {content_length}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Content-Length: not a number"
                )
    
    def _validate_conflicting_headers(self, request: Request):
        """
        Check for conflicting Transfer-Encoding and Content-Length headers
        
        Prevents: HTTP request smuggling (CL.TE and TE.CL attacks)
        
        RFC 7230 Section 3.3.3: If both headers are present, the request
        is likely malicious and should be rejected.
        """
        transfer_encoding = request.headers.get("transfer-encoding")
        content_length = request.headers.get("content-length")
        
        if transfer_encoding and content_length:
            logger.error("Conflicting Transfer-Encoding and Content-Length headers detected")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conflicting Transfer-Encoding and Content-Length headers. Possible smuggling attack."
            )
    
    def _validate_transfer_encoding(self, request: Request):
        """
        Validate Transfer-Encoding header values
        
        Prevents: Invalid encoding attacks, protocol confusion
        """
        transfer_encoding = request.headers.get("transfer-encoding")
        
        if transfer_encoding:
            # Parse comma-separated encodings
            encodings = [e.strip().lower() for e in transfer_encoding.split(",")]
            
            # Validate each encoding
            for encoding in encodings:
                if encoding not in self.VALID_ENCODINGS:
                    logger.warning(f"Invalid Transfer-Encoding: {encoding}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid Transfer-Encoding value: {encoding}"
                    )
            
            # 'chunked' must be the last encoding if present
            if "chunked" in encodings and encodings[-1] != "chunked":
                logger.warning("Invalid Transfer-Encoding order: chunked not last")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Transfer-Encoding: 'chunked' must be the final encoding"
                )
    
    def _validate_http_method(self, request: Request):
        """
        Validate HTTP method
        
        Prevents: Method override attacks, invalid methods
        """
        if request.method not in self.ALLOWED_METHODS:
            logger.warning(f"Invalid HTTP method: {request.method}")
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=f"Method {request.method} not allowed"
            )
    
    def _validate_header_sizes(self, request: Request):
        """
        Validate header sizes to prevent memory exhaustion
        
        Prevents: Header-based DoS attacks, memory exhaustion
        """
        # Check individual header sizes
        for header_name, header_value in request.headers.items():
            header_size = len(header_name) + len(header_value)
            if header_size > self.MAX_HEADER_SIZE:
                logger.warning(f"Header too large: {header_name} ({header_size} bytes)")
                raise HTTPException(
                    status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
                    detail=f"Header '{header_name}' exceeds maximum size"
                )
        
        # Check total header size
        total_header_size = sum(
            len(k) + len(v) for k, v in request.headers.items()
        )
        if total_header_size > self.MAX_TOTAL_HEADER_SIZE:
            logger.warning(f"Total headers too large: {total_header_size} bytes")
            raise HTTPException(
                status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
                detail="Total header size exceeds maximum"
            )
    
    def _detect_suspicious_patterns(self, request: Request):
        """
        Detect suspicious patterns in headers
        
        Prevents: Header injection, CRLF injection, smuggling attempts
        """
        for header_name, header_value in request.headers.items():
            # Check each suspicious pattern
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, header_value, re.IGNORECASE):
                    logger.error(f"Suspicious pattern detected in header {header_name}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Suspicious pattern detected in request headers"
                    )
            
            # Check for CRLF injection specifically
            if "\r" in header_value or "\n" in header_value:
                logger.error(f"CRLF injection attempt in header {header_name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid characters in header value"
                )
    
    def _validate_host_header(self, request: Request):
        """
        Validate Host header presence and format
        
        Prevents: Host header attacks, cache poisoning
        """
        host = request.headers.get("host")
        
        if not host:
            logger.warning("Missing Host header")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required Host header"
            )
        
        # Validate host format (basic check)
        if not re.match(r"^[a-zA-Z0-9\.\-:]+$", host):
            logger.warning(f"Invalid Host header format: {host}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Host header format"
            )
    
    def _validate_duplicate_headers(self, request: Request):
        """
        Check for duplicate critical headers
        
        Prevents: Header confusion attacks, cache poisoning
        
        Critical headers that should not be duplicated:
        - Host
        - Content-Length
        - Transfer-Encoding
        - Authorization
        """
        critical_headers = [
            "host",
            "content-length",
            "transfer-encoding",
            "authorization"
        ]
        
        for header in critical_headers:
            # Get all values for this header (case-insensitive)
            values = [
                v for k, v in request.headers.items()
                if k.lower() == header.lower()
            ]
            
            if len(values) > 1:
                logger.error(f"Duplicate {header} header detected")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate {header} header not allowed"
                )


class RequestSizeLimiter(BaseHTTPMiddleware):
    """
    Simple middleware to enforce request size limits
    
    This is a lightweight alternative to full request validation
    when you only need size limiting.
    """
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        """Enforce request size limit"""
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large (max: {self.max_size} bytes)"
            )
        
        return await call_next(request)
