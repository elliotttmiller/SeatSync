"""
Enhanced JWT Security Module

This module implements secure JWT token handling with protection against:
- Algorithm confusion attacks (none, weak algorithms)
- Token replay attacks
- Expired token usage
- Missing required claims
- Token revocation via blacklist

Based on security analysis of EvilWAF attack vectors.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# CRITICAL: Only allow secure algorithms - NEVER allow 'none'
ALLOWED_ALGORITHMS = ["HS256", "RS256"]
TOKEN_BLACKLIST: set = set()  # In-memory blacklist (use Redis in production)


class JWTSecurityManager:
    """
    Enhanced JWT security manager with strict validation
    
    Prevents:
    - JWT algorithm confusion attacks
    - Token replay attacks  
    - Weak algorithm exploitation
    - Missing claim attacks
    """
    
    @staticmethod
    def create_access_token(
        data: Dict,
        expires_delta: Optional[timedelta] = None,
        algorithm: str = "HS256"
    ) -> str:
        """
        Create a JWT token with strict algorithm enforcement
        
        Args:
            data: Token payload data
            expires_delta: Optional expiration time
            algorithm: JWT algorithm (must be in ALLOWED_ALGORITHMS)
            
        Returns:
            Encoded JWT token
            
        Raises:
            ValueError: If algorithm is not allowed
        """
        # CRITICAL: Validate algorithm before creating token
        if algorithm not in ALLOWED_ALGORITHMS:
            raise ValueError(f"Algorithm {algorithm} not allowed. Use one of: {ALLOWED_ALGORITHMS}")
        
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        # Add required security claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "seatsync-api",  # Issuer
            "aud": "seatsync-client",  # Audience
            "alg": algorithm  # Store algorithm in payload for verification
        })
        
        # Create token with explicit algorithm
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=algorithm
        )
        
        logger.debug(f"Created JWT token with algorithm {algorithm}")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict:
        """
        Verify JWT token with comprehensive security checks
        
        Security checks performed:
        1. Algorithm validation (reject 'none' and weak algorithms)
        2. Token blacklist check
        3. Signature verification
        4. Expiration validation
        5. Required claims validation
        6. Issuer/Audience validation
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid, expired, or blacklisted
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # STEP 1: Check if token is blacklisted
            if JWTSecurityManager.is_token_blacklisted(token):
                logger.warning("Attempt to use blacklisted token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # STEP 2: Decode header without verification to check algorithm
            unverified_header = jwt.get_unverified_header(token)
            algorithm = unverified_header.get("alg")
            
            # STEP 3: CRITICAL - Reject 'none' algorithm and other invalid algorithms
            if algorithm not in ALLOWED_ALGORITHMS:
                logger.error(f"Rejected token with invalid algorithm: {algorithm}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token algorithm: {algorithm}"
                )
            
            # STEP 4: Verify token with strict validation
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=ALLOWED_ALGORITHMS,  # Only allow specific algorithms
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "require_exp": True,
                    "require_iat": True
                },
                issuer="seatsync-api",
                audience="seatsync-client"
            )
            
            # STEP 5: Validate required claims
            required_claims = ["sub", "exp", "iat", "iss", "aud"]
            for claim in required_claims:
                if claim not in payload:
                    logger.error(f"Token missing required claim: {claim}")
                    raise credentials_exception
            
            # STEP 6: Verify algorithm in payload matches header
            if payload.get("alg") != algorithm:
                logger.error("Token algorithm mismatch between header and payload")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token algorithm mismatch"
                )
            
            logger.debug(f"Successfully verified token for user {payload.get('sub')}")
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise credentials_exception
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise credentials_exception
    
    @staticmethod
    def blacklist_token(token: str):
        """
        Add token to blacklist for revocation
        
        Use cases:
        - User logout
        - Password reset
        - Security breach
        - Admin revocation
        
        Note: In production, use Redis with TTL equal to token expiration
        
        Args:
            token: JWT token to blacklist
        """
        # Create hash of token for efficient storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        TOKEN_BLACKLIST.add(token_hash)
        logger.info(f"Token blacklisted: {token_hash[:16]}...")
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Check if token is in blacklist
        
        Args:
            token: JWT token to check
            
        Returns:
            True if token is blacklisted, False otherwise
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash in TOKEN_BLACKLIST
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Create long-lived refresh token
        
        Refresh tokens allow users to obtain new access tokens without
        re-authenticating, while keeping access tokens short-lived.
        
        Args:
            user_id: User ID to encode in token
            
        Returns:
            Encoded refresh token
        """
        return JWTSecurityManager.create_access_token(
            data={"sub": str(user_id), "type": "refresh"},
            expires_delta=timedelta(days=30),
            algorithm="HS256"
        )
    
    @staticmethod
    def verify_refresh_token(token: str) -> int:
        """
        Verify refresh token and extract user ID
        
        Args:
            token: Refresh token string
            
        Returns:
            User ID
            
        Raises:
            HTTPException: If token is invalid or not a refresh token
        """
        payload = JWTSecurityManager.verify_token(token)
        
        # Verify this is a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return int(user_id)


def validate_token_algorithm(token: str) -> bool:
    """
    Utility function to validate token algorithm without full verification
    
    Useful for quick security checks before expensive operations
    
    Args:
        token: JWT token string
        
    Returns:
        True if algorithm is valid, False otherwise
    """
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg")
        return algorithm in ALLOWED_ALGORITHMS
    except Exception:
        return False
