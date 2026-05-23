"""Camera/phone EXIF profiles for realistic metadata generation."""

import random
import string


def _canon_serial(rng: random.Random) -> str:
    return "".join(rng.choices(string.digits, k=12))


def _sony_serial(rng: random.Random) -> str:
    return "".join(rng.choices(string.digits, k=7))


def _nikon_serial(rng: random.Random) -> str:
    return "".join(rng.choices(string.digits, k=7))


def _fuji_serial(rng: random.Random) -> str:
    return rng.choice(["1DA", "2CA", "3BA"]) + "".join(rng.choices(string.digits, k=5))


def _phone_serial(rng: random.Random) -> str:
    return "".join(rng.choices(string.ascii_uppercase + string.digits, k=12))


def _lens_serial(rng: random.Random) -> str:
    return "".join(rng.choices(string.digits, k=10))


CAMERA_PROFILES = [
    {
        "make": "Canon",
        "model": "Canon EOS 5D Mark IV",
        "sensor_crop_factor": 1.0,
        "lens_pool": [
            ("EF24-70mm f/2.8L II USM", 24, 70, 2.8, 22.0),
            ("EF70-200mm f/2.8L IS III USM", 70, 200, 2.8, 32.0),
            ("EF50mm f/1.4 USM", 50, 50, 1.4, 22.0),
            ("EF85mm f/1.2L II USM", 85, 85, 1.2, 16.0),
            ("EF16-35mm f/2.8L III USM", 16, 35, 2.8, 22.0),
        ],
        "software_pool": [
            "Canon EOS 5D Mark IV Firmware Version 1.3.3",
            "Canon EOS 5D Mark IV Firmware Version 1.2.1",
            "Adobe Photoshop Lightroom Classic 13.2 (Windows)",
            "Adobe Photoshop 25.5",
        ],
        "is_phone": False,
        "body_serial_generator": _canon_serial,
    },
    {
        "make": "Canon",
        "model": "Canon EOS R5",
        "sensor_crop_factor": 1.0,
        "lens_pool": [
            ("RF24-70mm F2.8 L IS USM", 24, 70, 2.8, 22.0),
            ("RF70-200mm F2.8 L IS USM", 70, 200, 2.8, 32.0),
            ("RF50mm F1.2 L USM", 50, 50, 1.2, 16.0),
            ("RF85mm F1.2 L USM", 85, 85, 1.2, 16.0),
            ("RF15-35mm F2.8 L IS USM", 15, 35, 2.8, 22.0),
        ],
        "software_pool": [
            "Canon EOS R5 Firmware Version 1.8.1",
            "Canon EOS R5 Firmware Version 1.9.0",
            "Adobe Photoshop Lightroom Classic 13.4 (Windows)",
            "Capture One 23",
        ],
        "is_phone": False,
        "body_serial_generator": _canon_serial,
    },
    {
        "make": "SONY",
        "model": "ILCE-7M4",
        "sensor_crop_factor": 1.0,
        "lens_pool": [
            ("FE 24-70mm F2.8 GM II", 24, 70, 2.8, 22.0),
            ("FE 70-200mm F2.8 GM OSS II", 70, 200, 2.8, 22.0),
            ("FE 50mm F1.2 GM", 50, 50, 1.2, 16.0),
            ("FE 35mm F1.4 GM", 35, 35, 1.4, 16.0),
            ("FE 85mm F1.4 GM", 85, 85, 1.4, 16.0),
        ],
        "software_pool": [
            "ILCE-7M4 v2.01",
            "ILCE-7M4 v3.00",
            "Adobe Photoshop Lightroom Classic 13.2",
            "Capture One 23",
        ],
        "is_phone": False,
        "body_serial_generator": _sony_serial,
    },
    {
        "make": "SONY",
        "model": "ILCE-7RM5",
        "sensor_crop_factor": 1.0,
        "lens_pool": [
            ("FE 24-70mm F2.8 GM II", 24, 70, 2.8, 22.0),
            ("FE 70-200mm F2.8 GM OSS II", 70, 200, 2.8, 22.0),
            ("FE 50mm F1.2 GM", 50, 50, 1.2, 16.0),
            ("FE 14mm F1.8 GM", 14, 14, 1.8, 16.0),
            ("FE 135mm F1.8 GM", 135, 135, 1.8, 22.0),
        ],
        "software_pool": [
            "ILCE-7RM5 v2.00",
            "ILCE-7RM5 v2.01",
            "Adobe Photoshop Lightroom Classic 13.4",
            "Darktable 4.6.0",
        ],
        "is_phone": False,
        "body_serial_generator": _sony_serial,
    },
    {
        "make": "NIKON CORPORATION",
        "model": "NIKON Z 6II",
        "sensor_crop_factor": 1.0,
        "lens_pool": [
            ("NIKKOR Z 24-70mm f/2.8 S", 24, 70, 2.8, 22.0),
            ("NIKKOR Z 70-200mm f/2.8 VR S", 70, 200, 2.8, 22.0),
            ("NIKKOR Z 50mm f/1.2 S", 50, 50, 1.2, 16.0),
            ("NIKKOR Z 85mm f/1.2 S", 85, 85, 1.2, 16.0),
            ("NIKKOR Z 14-24mm f/2.8 S", 14, 24, 2.8, 22.0),
        ],
        "software_pool": [
            "NIKON Z 6II Ver.1.60",
            "NIKON Z 6II Ver.1.50",
            "Adobe Photoshop Lightroom Classic 13.2",
            "Capture One 23",
        ],
        "is_phone": False,
        "body_serial_generator": _nikon_serial,
    },
    {
        "make": "FUJIFILM",
        "model": "X-T5",
        "sensor_crop_factor": 1.5,
        "lens_pool": [
            ("XF23mmF1.4 R LM WR", 23, 23, 1.4, 16.0),
            ("XF56mmF1.2 R WR", 56, 56, 1.2, 16.0),
            ("XF16-55mmF2.8 R LM WR", 16, 55, 2.8, 22.0),
            ("XF50-140mmF2.8 R LM OIS WR", 50, 140, 2.8, 22.0),
            ("XF35mmF1.4 R", 35, 35, 1.4, 16.0),
        ],
        "software_pool": [
            "Digital Camera X-T5 Ver3.01",
            "Digital Camera X-T5 Ver2.20",
            "Adobe Photoshop Lightroom Classic 13.2",
            "Capture One 23 for Fujifilm",
        ],
        "is_phone": False,
        "body_serial_generator": _fuji_serial,
    },
    {
        "make": "Apple",
        "model": "iPhone 15 Pro",
        "sensor_crop_factor": 7.0,
        "lens_pool": [
            ("iPhone 15 Pro back triple camera 6.765mm f/1.78", 6.765, 6.765, 1.78, 1.78),
            ("iPhone 15 Pro back triple camera 2.22mm f/2.2", 2.22, 2.22, 2.2, 2.2),
            ("iPhone 15 Pro back triple camera 9mm f/2.8", 9.0, 9.0, 2.8, 2.8),
        ],
        "software_pool": [
            "17.4.1",
            "17.5",
            "17.5.1",
            "18.0",
            "18.1",
        ],
        "is_phone": True,
        "body_serial_generator": _phone_serial,
    },
    {
        "make": "Google",
        "model": "Pixel 8 Pro",
        "sensor_crop_factor": 6.0,
        "lens_pool": [
            ("Pixel 8 Pro back camera 6.9mm f/1.68", 6.9, 6.9, 1.68, 1.68),
            ("Pixel 8 Pro back camera 2.35mm f/2.2", 2.35, 2.35, 2.2, 2.2),
            ("Pixel 8 Pro back camera 18.0mm f/2.8", 18.0, 18.0, 2.8, 2.8),
        ],
        "software_pool": [
            "Android 14",
            "Android 14 HDR+ 9.4.108",
            "Android 15",
            "Android 15 HDR+ 9.6.042",
        ],
        "is_phone": True,
        "body_serial_generator": _phone_serial,
    },
]

SCENE_TYPES = [
    "outdoor_daylight",
    "outdoor_golden",
    "indoor_natural",
    "indoor_artificial",
    "lowlight",
]

GPS_CITY_POLYGONS = [
    {"name": "New York", "lat_min": 40.70, "lat_max": 40.80, "lon_min": -74.02, "lon_max": -73.93},
    {"name": "Los Angeles", "lat_min": 33.95, "lat_max": 34.10, "lon_min": -118.35, "lon_max": -118.15},
    {"name": "London", "lat_min": 51.48, "lat_max": 51.55, "lon_min": -0.18, "lon_max": -0.05},
    {"name": "Tokyo", "lat_min": 35.65, "lat_max": 35.72, "lon_min": 139.68, "lon_max": 139.82},
    {"name": "Paris", "lat_min": 48.83, "lat_max": 48.88, "lon_min": 2.28, "lon_max": 2.40},
    {"name": "Berlin", "lat_min": 52.48, "lat_max": 52.54, "lon_min": 13.34, "lon_max": 13.46},
    {"name": "Sydney", "lat_min": -33.90, "lat_max": -33.83, "lon_min": 151.17, "lon_max": 151.25},
    {"name": "San Francisco", "lat_min": 37.74, "lat_max": 37.80, "lon_min": -122.48, "lon_max": -122.39},
    {"name": "Seoul", "lat_min": 37.53, "lat_max": 37.58, "lon_min": 126.95, "lon_max": 127.05},
    {"name": "Dubai", "lat_min": 25.17, "lat_max": 25.27, "lon_min": 55.25, "lon_max": 55.35},
]
