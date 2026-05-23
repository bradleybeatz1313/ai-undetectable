"""FastAPI application for AI Image Undetectable API."""

import os
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import stripe

from db import SessionLocal, User, Upload, init_db, get_db
from auth import (
    generate_api_key,
    verify_api_key,
    get_user_by_api_key,
    check_usage_limit,
    get_remaining_quota,
)
from models import (
    UserCreate,
    UserResponse,
    ProcessImageResponse,
    ImageStatusResponse,
    UsageStatsResponse,
)
from processor import (
    process_image,
    save_upload,
    get_processed_path,
    cleanup_upload,
    get_file_size_mb,
)

# Initialize database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="AI Image Undetectable API",
    description="Make AI-generated images undetectable",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_dummy")
if STRIPE_SECRET_KEY != "sk_test_dummy":
    stripe.api_key = STRIPE_SECRET_KEY


# ============================================================================
# Health Check
# ============================================================================
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "ai-undetectable"}


# ============================================================================
# User Management
# ============================================================================
@app.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account with free tier."""
    # Check if user already exists
    existing = db.query(User).filter(User.api_key == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user_id = str(uuid.uuid4())
    api_key = generate_api_key()

    user = User(
        id=user_id,
        api_key=api_key,
        tier="free",
        monthly_usage=0,
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.get("/user", response_model=UserResponse)
def get_user(db: Session = Depends(get_db), x_api_key: str = Header(None)):
    """Get current user information."""
    user = verify_api_key(x_api_key, db)
    return user


@app.get("/usage", response_model=UsageStatsResponse)
def get_usage_stats(db: Session = Depends(get_db), x_api_key: str = Header(None)):
    """Get user's usage statistics."""
    user = verify_api_key(x_api_key, db)
    tier_limits = {
        "free": 10,
        "pro": 500,
        "enterprise": 999999,
    }
    limit = tier_limits.get(user.tier, 10)
    remaining = max(0, limit - user.monthly_usage)

    return UsageStatsResponse(
        tier=user.tier,
        monthly_usage=user.monthly_usage,
        monthly_limit=limit,
        remaining_quota=remaining,
        usage_reset_date=user.usage_reset_date,
        stripe_subscription_active=user.stripe_subscription_id is not None,
    )


# ============================================================================
# Image Processing
# ============================================================================
@app.post("/process", response_model=ProcessImageResponse)
async def process_image_endpoint(
    file: UploadFile = File(...),
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Upload and process an image to make it undetectable."""

    # Verify API key
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

    # Check usage limits
    if not check_usage_limit(user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly quota exceeded. Upgrade to Pro for 500 images/month.",
        )

    # Validate file size (max 10MB for MVP, 2MB for free tier)
    max_size = 10 if user.tier in ["pro", "enterprise"] else 2
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)

    if file_size_mb > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {max_size}MB for {user.tier} tier",
        )

    # Validate image format
    valid_formats = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    filename = file.filename or "image.jpg"
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format. Supported: {valid_formats}",
        )

    # Create upload record
    upload_id = str(uuid.uuid4())
    upload = Upload(
        id=upload_id,
        user_id=user.id,
        original_filename=filename,
        status="processing",
    )

    # Save uploaded file
    upload_path = f"uploads/{user.id}/{upload_id}.tmp"
    os.makedirs(f"uploads/{user.id}", exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(file_bytes)

    upload.file_path = upload_path

    # Process image
    output_path = f"processed/{user.id}/{upload_id}.jpg"
    os.makedirs(f"processed/{user.id}", exist_ok=True)

    try:
        success = process_image(upload_path, output_path)

        if success:
            upload.processed_file_path = output_path
            upload.status = "completed"
            upload.completed_at = datetime.now(timezone.utc)

            # Increment usage counter
            user.monthly_usage += 1

            db.add(upload)
            db.add(user)
            db.commit()
            db.refresh(upload)
            db.refresh(user)

            # Clean up original file
            cleanup_upload(upload_path)

            return ProcessImageResponse(
                success=True,
                message="Image processed successfully",
                upload_id=upload_id,
                remaining_quota=get_remaining_quota(user),
                tier=user.tier,
            )
        else:
            upload.status = "failed"
            upload.error_message = "Image processing failed"
            db.add(upload)
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image",
            )

    except Exception as e:
        upload.status = "failed"
        upload.error_message = str(e)
        db.add(upload)
        db.commit()

        cleanup_upload(upload_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}",
        )


@app.get("/result/{upload_id}")
def get_processed_image(
    upload_id: str,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Download processed image."""

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

    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    if upload.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this upload",
        )

    if upload.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image not ready. Status: {upload.status}",
        )

    if not os.path.exists(upload.processed_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed file not found",
        )

    return FileResponse(
        upload.processed_file_path,
        media_type="image/jpeg",
        filename=f"undetectable_{upload.id}.jpg",
    )


@app.get("/status/{upload_id}", response_model=ImageStatusResponse)
def get_upload_status(
    upload_id: str,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get status of an upload."""

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

    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    if upload.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this upload",
        )

    return upload


# ============================================================================
# Billing
# ============================================================================
@app.post("/upgrade-to-pro", response_model=None)
def upgrade_to_pro(db: Session = Depends(get_db), x_api_key: str = Header(None)):
    """
    Placeholder for Stripe integration.
    In production: call Stripe API to create/update subscription.
    """
    user = verify_api_key(x_api_key, db)

    # Placeholder: in production, create Stripe Checkout session
    return {
        "success": True,
        "message": "Upgrade to Pro: pay $9.99/month for 500 images/month",
        "checkout_url": "https://stripe.com/checkout (implement in production)",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
