"""Image processing pipeline to make AI-generated images undetectable."""

import io
import os
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from typing import Tuple


UPLOADS_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


def process_image(input_path: str, output_path: str) -> bool:
    """
    Transform AI-generated image to make it undetectable.

    Strategy:
    1. Load image
    2. Add imperceptible Gaussian noise (breaks detection fingerprints)
    3. Apply subtle color/contrast shifts
    4. Light JPEG compression + reloading (removes metadata, alters compression patterns)
    5. Slight blur + sharpen pass (changes frequency characteristics)
    6. Subtle saturation boost (more human-like)

    Returns: bool indicating success
    """
    try:
        # Load image
        img = Image.open(input_path).convert("RGB")

        # Step 1: Add imperceptible Gaussian noise (σ ~ 2-5 for imperceptible noise)
        img_array = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, 3, img_array.shape)  # σ=3
        img_array = np.clip(img_array + noise, 0, 255)
        img = Image.fromarray(img_array.astype(np.uint8))

        # Step 2: Subtle color/contrast adjustments
        # Increase contrast slightly (AI images often have flatter contrast)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)  # +5% contrast

        # Increase brightness very slightly
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.02)  # +2% brightness

        # Step 3: JPEG compression cycle (simulates camera capture)
        # Save as JPEG with quality loss, then reload
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=92)  # Lossy compression
        buffer.seek(0)
        img = Image.open(buffer)
        img = img.convert("RGB")

        # Step 4: Light blur + sharpen (changes frequency spectrum)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=0.8))
        enhancer = ImageEnhance.Sharpness(blurred)
        img = enhancer.enhance(1.3)  # +30% sharpness to compensate

        # Step 5: Subtle saturation boost (makes it look more "real")
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.08)  # +8% saturation

        # Step 6: Final JPEG encoding with slightly different quality
        img.save(output_path, format="JPEG", quality=94)

        return True

    except Exception as e:
        print(f"Error processing image: {e}")
        return False


def get_upload_path(user_id: str, filename: str) -> str:
    """Get the full path for an uploaded file."""
    user_dir = UPLOADS_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    return str(user_dir / filename)


def get_processed_path(user_id: str, filename: str) -> str:
    """Get the full path for a processed file."""
    user_dir = PROCESSED_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    # Add .processed before extension
    base, ext = os.path.splitext(filename)
    return str(user_dir / f"{base}.processed.jpg")


def save_upload(user_id: str, filename: str, file_bytes: bytes) -> str:
    """Save uploaded file to disk."""
    path = get_upload_path(user_id, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def cleanup_upload(upload_path: str):
    """Delete uploaded file after processing."""
    try:
        if os.path.exists(upload_path):
            os.remove(upload_path)
    except Exception as e:
        print(f"Error cleaning up upload: {e}")


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)
