"""API key authentication and authorization."""

import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Header, Depends
from typing import Optional
from db import User, SessionLocal, get_db


def generate_api_key() -> str:
    """Generate a random API key."""
    return secrets.token_urlsafe(32)


def get_user_by_api_key(db: Session, api_key: str) -> Optional[User]:
    """Retrieve user by API key."""
    return db.query(User).filter(User.api_key == api_key).first()


def verify_api_key(x_api_key: str = Header(None), db: Session = Depends(get_db)) -> User:
    """Verify API key from request header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    user = get_user_by_api_key(db, x_api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def check_usage_limit(user: User) -> bool:
    """Check if user has exceeded their monthly limit."""
    tier_limits = {
        "free": 10,
        "pro": 500,
        "enterprise": float("inf"),
    }
    limit = tier_limits.get(user.tier, 10)
    return user.monthly_usage < limit


def get_remaining_quota(user: User) -> int:
    """Get remaining quota for user."""
    tier_limits = {
        "free": 10,
        "pro": 500,
        "enterprise": 999999,
    }
    limit = tier_limits.get(user.tier, 10)
    return max(0, limit - user.monthly_usage)
