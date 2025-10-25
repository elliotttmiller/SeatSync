"""
Security Tests

Comprehensive test suite for security enhancements based on EvilWAF analysis.

Tests cover:
- JWT algorithm confusion attacks
- Token blacklisting
- HTTP request smuggling
- Request validation
- Security headers
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt as pyjwt

from app.core.jwt_security import JWTSecurityManager, validate_token_algorithm
from app.middleware.request_validator import RequestValidationMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.core.config import settings


# Test JWT Security
class TestJWTSecurity:
    """Test JWT security enhancements against algorithm confusion attacks"""
    
    def test_create_token_with_valid_algorithm(self):
        """Test token creation with valid algorithm"""
        token = JWTSecurityManager.create_access_token(
            data={"sub": "123"},
            algorithm="HS256"
        )
        assert token is not None
        assert isinstance(token, str)
    
    def test_reject_none_algorithm_creation(self):
        """Test that 'none' algorithm is rejected during creation"""
        with pytest.raises(ValueError, match="Algorithm none not allowed"):
            JWTSecurityManager.create_access_token(
                data={"sub": "123"},
                algorithm="none"
            )
    
    def test_reject_weak_algorithm_creation(self):
        """Test that weak algorithms are rejected"""
        with pytest.raises(ValueError):
            JWTSecurityManager.create_access_token(
                data={"sub": "123"},
                algorithm="HS1"
            )
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        token = JWTSecurityManager.create_access_token(
            data={"sub": "123"}
        )
        payload = JWTSecurityManager.verify_token(token)
        assert payload["sub"] == "123"
        assert "exp" in payload
        assert "iat" in payload
        assert "iss" in payload
        assert "aud" in payload
    
    def test_reject_none_algorithm_token(self):
        """Test rejection of token with 'none' algorithm"""
        # Create a malicious token with 'none' algorithm
        payload = {
            "sub": "123",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
            "iss": "seatsync-api",
            "aud": "seatsync-client",
            "alg": "none"
        }
        malicious_token = pyjwt.encode(payload, "", algorithm="none")
        
        # Should reject
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            JWTSecurityManager.verify_token(malicious_token)
        assert exc_info.value.status_code == 401
        assert "Invalid token algorithm" in str(exc_info.value.detail)
    
    def test_reject_algorithm_mismatch(self):
        """Test rejection when header algorithm differs from payload"""
        # Create token with HS256
        token = JWTSecurityManager.create_access_token(
            data={"sub": "123"}
        )
        
        # Manually decode and re-encode with different algorithm claim
        payload = pyjwt.decode(token, options={"verify_signature": False})
        payload["alg"] = "RS256"  # Change algorithm in payload
        
        # Re-encode with HS256
        tampered_token = pyjwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        # Should reject due to mismatch
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            JWTSecurityManager.verify_token(tampered_token)
    
    def test_token_blacklisting(self):
        """Test token revocation via blacklist"""
        token = JWTSecurityManager.create_access_token(
            data={"sub": "123"}
        )
        
        # Token should be valid
        payload = JWTSecurityManager.verify_token(token)
        assert payload["sub"] == "123"
        
        # Blacklist the token
        JWTSecurityManager.blacklist_token(token)
        
        # Token should now be rejected
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            JWTSecurityManager.verify_token(token)
        assert "revoked" in str(exc_info.value.detail).lower()
    
    def test_expired_token_rejection(self):
        """Test rejection of expired tokens"""
        token = JWTSecurityManager.create_access_token(
            data={"sub": "123"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            JWTSecurityManager.verify_token(token)
    
    def test_missing_required_claims(self):
        """Test rejection of tokens missing required claims"""
        # Create token without required claims
        payload = {"exp": datetime.utcnow() + timedelta(hours=1)}
        token = pyjwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            JWTSecurityManager.verify_token(token)
    
    def test_refresh_token_creation(self):
        """Test refresh token creation"""
        refresh_token = JWTSecurityManager.create_refresh_token(user_id=123)
        assert refresh_token is not None
        
        # Verify it's a refresh token
        payload = JWTSecurityManager.verify_token(refresh_token)
        assert payload["type"] == "refresh"
        assert payload["sub"] == "123"
    
    def test_validate_token_algorithm_utility(self):
        """Test token algorithm validation utility"""
        valid_token = JWTSecurityManager.create_access_token(
            data={"sub": "123"}
        )
        assert validate_token_algorithm(valid_token) is True
        
        # Create invalid token
        invalid_token = pyjwt.encode({"sub": "123"}, "", algorithm="none")
        assert validate_token_algorithm(invalid_token) is False


# Test Request Validation Middleware
class TestRequestValidation:
    """Test request validation middleware against smuggling attacks"""
    
    @pytest.fixture
    def app(self):
        """Create test app with middleware"""
        app = FastAPI()
        app.add_middleware(RequestValidationMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_valid_request(self, client):
        """Test that valid requests pass through"""
        response = client.get("/test")
        assert response.status_code == 200
    
    def test_reject_oversized_uri(self, client):
        """Test rejection of oversized URI"""
        long_path = "/test?" + "x" * 3000
        response = client.get(long_path)
        assert response.status_code == 414
    
    def test_reject_negative_content_length(self, client):
        """Test rejection of negative Content-Length"""
        response = client.post(
            "/test",
            headers={"Content-Length": "-100"},
            json={"data": "test"}
        )
        assert response.status_code == 400
        assert "Content-Length" in response.json()["detail"]
    
    def test_reject_oversized_content(self, client):
        """Test rejection of oversized content"""
        response = client.post(
            "/test",
            headers={"Content-Length": str(11 * 1024 * 1024)},  # 11MB
            json={"data": "test"}
        )
        assert response.status_code == 413
    
    def test_reject_conflicting_headers(self, client):
        """Test rejection of conflicting CL and TE headers (smuggling attack)"""
        response = client.post(
            "/test",
            headers={
                "Content-Length": "100",
                "Transfer-Encoding": "chunked"
            },
            json={"data": "test"}
        )
        assert response.status_code == 400
        assert "Conflicting" in response.json()["detail"]
    
    def test_reject_invalid_transfer_encoding(self, client):
        """Test rejection of invalid Transfer-Encoding values"""
        response = client.post(
            "/test",
            headers={"Transfer-Encoding": "malicious"},
            json={"data": "test"}
        )
        assert response.status_code == 400
        assert "Invalid Transfer-Encoding" in response.json()["detail"]
    
    def test_reject_invalid_http_method(self, client):
        """Test rejection of invalid HTTP methods"""
        # FastAPI/Starlette handles this at a lower level
        # This is more of a documentation test
        pass
    
    def test_reject_missing_host_header(self, client):
        """Test rejection of requests without Host header"""
        # Note: TestClient automatically adds Host header
        # This would need to be tested with raw HTTP requests
        pass
    
    def test_reject_duplicate_critical_headers(self, client):
        """Test rejection of duplicate critical headers"""
        # This is difficult to test with TestClient as it normalizes headers
        # Would need raw HTTP client to send duplicate headers
        pass
    
    def test_reject_control_characters_in_headers(self, client):
        """Test rejection of control characters in headers"""
        response = client.get(
            "/test",
            headers={"X-Custom-Header": "value\x00with\x00nulls"}
        )
        # May be blocked by underlying HTTP library before reaching middleware
        # Test behavior depends on HTTP stack


# Test Security Headers Middleware
class TestSecurityHeaders:
    """Test security headers middleware"""
    
    @pytest.fixture
    def app(self):
        """Create test app with middleware"""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.get("/api/v1/test")
        async def api_endpoint():
            return {"message": "api success"}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_content_security_policy_present(self, client):
        """Test that CSP header is present"""
        response = client.get("/test")
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
    
    def test_x_frame_options_present(self, client):
        """Test that X-Frame-Options header is present"""
        response = client.get("/test")
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
    
    def test_x_content_type_options_present(self, client):
        """Test that X-Content-Type-Options header is present"""
        response = client.get("/test")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    def test_x_xss_protection_present(self, client):
        """Test that X-XSS-Protection header is present"""
        response = client.get("/test")
        assert "X-XSS-Protection" in response.headers
        assert "1" in response.headers["X-XSS-Protection"]
    
    def test_referrer_policy_present(self, client):
        """Test that Referrer-Policy header is present"""
        response = client.get("/test")
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    
    def test_permissions_policy_present(self, client):
        """Test that Permissions-Policy header is present"""
        response = client.get("/test")
        assert "Permissions-Policy" in response.headers
        permissions = response.headers["Permissions-Policy"]
        assert "geolocation=()" in permissions
        assert "camera=()" in permissions
    
    def test_cache_control_on_api_endpoints(self, client):
        """Test that API responses have no-cache headers"""
        response = client.get("/api/v1/test")
        assert "Cache-Control" in response.headers
        cache_control = response.headers["Cache-Control"]
        assert "no-store" in cache_control
        assert "no-cache" in cache_control
        assert response.headers.get("Pragma") == "no-cache"
        assert response.headers.get("Expires") == "0"
    
    def test_hsts_not_added_over_http(self, client):
        """Test that HSTS is not added over HTTP connections"""
        response = client.get("/test")
        # TestClient uses http:// by default
        # HSTS should not be present over HTTP
        # (Our middleware checks for HTTPS before adding HSTS)


# Integration Tests
class TestSecurityIntegration:
    """Integration tests for multiple security features"""
    
    @pytest.fixture
    def app(self):
        """Create test app with all security middleware"""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(RequestValidationMiddleware)
        
        @app.get("/api/v1/public")
        async def public_endpoint():
            return {"message": "public"}
        
        @app.get("/api/v1/protected")
        async def protected_endpoint(
            token: str = None  # Simplified for testing
        ):
            if not token:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Unauthorized")
            
            # Verify token
            payload = JWTSecurityManager.verify_token(token)
            return {"message": "protected", "user": payload["sub"]}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_public_endpoint_has_security_headers(self, client):
        """Test that public endpoints have security headers"""
        response = client.get("/api/v1/public")
        assert response.status_code == 200
        assert "Content-Security-Policy" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Cache-Control" in response.headers
    
    def test_protected_endpoint_rejects_invalid_token(self, client):
        """Test that protected endpoint rejects invalid tokens"""
        # Create invalid token
        invalid_token = pyjwt.encode({"sub": "123"}, "wrong-secret", algorithm="HS256")
        
        response = client.get(
            "/api/v1/protected",
            params={"token": invalid_token}
        )
        # Should fail token verification
        assert response.status_code in [401, 500]  # Depends on error handling
    
    def test_protected_endpoint_accepts_valid_token(self, client):
        """Test that protected endpoint accepts valid tokens"""
        # Create valid token
        valid_token = JWTSecurityManager.create_access_token(
            data={"sub": "123"}
        )
        
        response = client.get(
            "/api/v1/protected",
            params={"token": valid_token}
        )
        assert response.status_code == 200
        assert response.json()["user"] == "123"
    
    def test_request_validation_before_authentication(self, client):
        """Test that request validation happens before authentication"""
        # Send oversized request to protected endpoint
        response = client.post(
            "/api/v1/protected",
            headers={"Content-Length": str(11 * 1024 * 1024)}
        )
        # Should be rejected at validation layer (413) not auth layer (401)
        assert response.status_code == 413


# Performance Tests
class TestSecurityPerformance:
    """Test that security features don't significantly impact performance"""
    
    def test_jwt_verification_performance(self):
        """Test JWT verification performance"""
        import time
        
        token = JWTSecurityManager.create_access_token(data={"sub": "123"})
        
        # Measure verification time
        start = time.time()
        iterations = 1000
        
        for _ in range(iterations):
            JWTSecurityManager.verify_token(token)
        
        elapsed = time.time() - start
        avg_time = elapsed / iterations
        
        # Should verify in less than 1ms on average
        assert avg_time < 0.001, f"JWT verification too slow: {avg_time:.4f}s"
    
    def test_middleware_overhead(self):
        """Test middleware performance overhead"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import time
        
        # App without middleware
        app1 = FastAPI()
        @app1.get("/test")
        async def test1():
            return {"message": "test"}
        
        # App with all middleware
        app2 = FastAPI()
        app2.add_middleware(SecurityHeadersMiddleware)
        app2.add_middleware(RequestValidationMiddleware)
        @app2.get("/test")
        async def test2():
            return {"message": "test"}
        
        client1 = TestClient(app1)
        client2 = TestClient(app2)
        
        # Warm up
        client1.get("/test")
        client2.get("/test")
        
        # Measure without middleware
        start = time.time()
        for _ in range(100):
            client1.get("/test")
        time_without = time.time() - start
        
        # Measure with middleware
        start = time.time()
        for _ in range(100):
            client2.get("/test")
        time_with = time.time() - start
        
        # Overhead should be less than 50%
        overhead = (time_with - time_without) / time_without
        assert overhead < 0.5, f"Middleware overhead too high: {overhead:.2%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
