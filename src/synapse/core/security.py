"""
API Key Security Functions

This module provides API key generation, hashing, and verification functions.
All password verification and JWT functions have been moved to their dedicated modules:
- Password verification: User.verify_password() method
- JWT operations: synapse.core.auth.jwt.JWTManager
"""

import secrets
import hashlib
from passlib.context import CryptContext

# Password context for API key hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt"""
    return pwd_context.hash(api_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return pwd_context.verify(plain_key, hashed_key)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token using SHA-256"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify a token against its SHA-256 hash"""
    return hash_token(token) == token_hash
