"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Request model for user signup."""
    email: str = Field(..., description="User email address")


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    api_key: str
    tier: str
    monthly_usage: int
    usage_reset_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessImageRequest(BaseModel):
    """Request model for image processing."""
    pass  # File data comes via multipart/form-data


class ProcessImageResponse(BaseModel):
    """Response model for image processing."""
    success: bool
    message: str
    upload_id: str = Optional[str]
    remaining_quota: int
    tier: str


class ImageStatusResponse(BaseModel):
    """Response model for image status."""
    id: str
    status: str  # processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class UpgradeRequest(BaseModel):
    """Request model for upgrading to pro."""
    stripe_token: str = Field(..., description="Stripe payment token")


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics."""
    tier: str
    monthly_usage: int
    monthly_limit: int
    remaining_quota: int
    usage_reset_date: datetime
    stripe_subscription_active: bool
