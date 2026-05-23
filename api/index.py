"""Vercel serverless FastAPI handler for AI Image Undetectable API."""

import os
import io
import uuid
import secrets
import tempfile
from datetime import datetime, timezone
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Header
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

app = FastAPI(
    title="AI Image Undetectable API",
    description="Make AI-generated images undetectable",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory user store for serverless (replace with external DB in production)
# For a real deployment, use Supabase/Neon Postgres via DATABASE_URL env var
DEMO_API_KEY = os.getenv("DEMO_API_KEY", "demo-key-free-tier")


def process_image(file_bytes: bytes) -> bytes:
    """Transform AI-generated image to make it undetectable. Returns processed JPEG bytes."""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    # Add imperceptible Gaussian noise
    img_array = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, 3, img_array.shape)
    img_array = np.clip(img_array + noise, 0, 255)
    img = Image.fromarray(img_array.astype(np.uint8))

    # Subtle contrast boost
    img = ImageEnhance.Contrast(img).enhance(1.05)

    # Slight brightness increase
    img = ImageEnhance.Brightness(img).enhance(1.02)

    # JPEG compression cycle (simulates camera capture)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=92)
    buffer.seek(0)
    img = Image.open(buffer).convert("RGB")

    # Light blur + sharpen (changes frequency spectrum)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = ImageEnhance.Sharpness(blurred).enhance(1.3)

    # Subtle saturation boost
    img = ImageEnhance.Color(img).enhance(1.08)

    # Final JPEG encoding
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=94)
    return output.getvalue()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "ai-undetectable"}


@app.post("/api/process")
async def process_image_endpoint(
    file: UploadFile = File(...),
    x_api_key: str = Header(None),
):
    """Upload and process an image to make it undetectable. Returns the processed image directly."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    # Validate file size (max 4.5MB for Vercel serverless payload limit)
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > 4.5:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Max size: 4.5MB for serverless processing",
        )

    # Validate image format
    valid_formats = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    filename = file.filename or "image.jpg"
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format. Supported: {', '.join(valid_formats)}",
        )

    try:
        processed_bytes = process_image(file_bytes)
        return Response(
            content=processed_bytes,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'attachment; filename="undetectable_{uuid.uuid4().hex[:8]}.jpg"',
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}",
        )


@app.get("/api/usage")
def get_usage(x_api_key: str = Header(None)):
    """Get usage stats (placeholder for serverless deployment)."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    return {
        "tier": "free",
        "monthly_usage": 0,
        "monthly_limit": 10,
        "remaining_quota": 10,
    }
