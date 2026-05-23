"""Generate randomized, internally-consistent EXIF metadata."""

import io
import math
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

import piexif
from PIL import Image

from exif_profiles import (
    CAMERA_PROFILES,
    GPS_CITY_POLYGONS,
    SCENE_TYPES,
    _lens_serial,
)

SCENE_EXPOSURE = {
    "outdoor_daylight": {
        "ilc": {"iso": (100, 400), "shutter": (1 / 2000, 1 / 125), "ev_bias": 0},
        "phone": {"iso": (50, 200), "shutter": (1 / 4000, 1 / 500), "ev_bias": 0},
        "hour_range": (8, 17),
    },
    "outdoor_golden": {
        "ilc": {"iso": (200, 800), "shutter": (1 / 500, 1 / 60), "ev_bias": 0},
        "phone": {"iso": (100, 400), "shutter": (1 / 1000, 1 / 125), "ev_bias": 0},
        "hour_range": (5, 8),
    },
    "indoor_natural": {
        "ilc": {"iso": (400, 1600), "shutter": (1 / 250, 1 / 30), "ev_bias": 0},
        "phone": {"iso": (200, 800), "shutter": (1 / 250, 1 / 60), "ev_bias": 0},
        "hour_range": (9, 16),
    },
    "indoor_artificial": {
        "ilc": {"iso": (800, 3200), "shutter": (1 / 125, 1 / 15), "ev_bias": 0},
        "phone": {"iso": (400, 1600), "shutter": (1 / 125, 1 / 30), "ev_bias": 0},
        "hour_range": (18, 23),
    },
    "lowlight": {
        "ilc": {"iso": (1600, 12800), "shutter": (1 / 60, 1 / 4), "ev_bias": 0},
        "phone": {"iso": (800, 3200), "shutter": (1 / 30, 1 / 4), "ev_bias": 0},
        "hour_range": (21, 3),
    },
}

METERING_MODES = [1, 2, 3, 5]
SCENE_CAPTURE_TYPES = [0, 1, 2, 3]


def _float_to_rational(value: float) -> tuple:
    if value == 0:
        return (0, 1)
    denom = 1000000
    num = int(round(value * denom))
    return (num, denom)


def _float_to_srational(value: float) -> tuple:
    denom = 1000000
    num = int(round(value * denom))
    return (num, denom)


def _shutter_to_rational(shutter_speed: float) -> tuple:
    if shutter_speed >= 1:
        return (int(round(shutter_speed)), 1)
    denom = int(round(1.0 / shutter_speed))
    return (1, denom)


def _deg_to_dms_rational(deg: float) -> tuple:
    d = int(abs(deg))
    m_float = (abs(deg) - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return ((d, 1), (m, 1), (int(round(s * 100)), 100))


def _make_thumbnail(img: Image.Image) -> bytes:
    thumb = img.copy()
    w, h = thumb.size
    new_w = 160
    new_h = int(h * (new_w / w))
    thumb = thumb.resize((new_w, new_h), Image.LANCZOS)
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def _pick_software(profile: dict, rng: random.Random) -> str:
    if profile["is_phone"]:
        return rng.choice(profile["software_pool"])

    if rng.random() < 0.3:
        editors = [
            "Adobe Photoshop Lightroom Classic 13.2",
            "Adobe Photoshop Lightroom Classic 13.4 (Windows)",
            "Adobe Photoshop 25.5",
            "Capture One 23",
            "Darktable 4.6.0",
            "Darktable 4.8.0",
        ]
        return rng.choice(editors)
    return rng.choice(profile["software_pool"])


def _random_hour_for_scene(scene_type: str, rng: random.Random) -> int:
    lo, hi = SCENE_EXPOSURE[scene_type]["hour_range"]
    if lo <= hi:
        return rng.randint(lo, hi)
    if rng.random() < 0.5:
        return rng.randint(lo, 23)
    return rng.randint(0, hi)


def add_realistic_exif(
    image_path: str,
    profile: Optional[dict] = None,
    scene_type: Optional[str] = None,
    gps: Optional[bool] = None,
) -> dict:
    rng = random.Random()

    if profile is None:
        profile = rng.choice(CAMERA_PROFILES)
    if scene_type is None:
        scene_type = rng.choice(SCENE_TYPES)

    img = Image.open(image_path)
    width, height = img.size

    lens_entry = rng.choice(profile["lens_pool"])
    lens_model, focal_min, focal_max, f_min, f_max = lens_entry

    if focal_min == focal_max:
        focal_length = float(focal_min)
    else:
        focal_length = float(rng.randint(int(focal_min), int(focal_max)))

    if profile["is_phone"]:
        fnumber = f_min
    else:
        f_stops = []
        f = f_min
        while f <= f_max + 0.01:
            f_stops.append(round(f, 1))
            f *= 1.4142
        fnumber = rng.choice(f_stops) if f_stops else f_min

    body_class = "phone" if profile["is_phone"] else "ilc"
    exp_cfg = SCENE_EXPOSURE[scene_type][body_class]

    iso = rng.randint(exp_cfg["iso"][0], exp_cfg["iso"][1])
    iso = max(50, (iso // 50) * 50)

    shutter_lo, shutter_hi = exp_cfg["shutter"]
    shutter_speed = math.exp(rng.uniform(math.log(shutter_lo), math.log(shutter_hi)))

    aperture_value = 2 * math.log2(fnumber)
    shutter_speed_value = -math.log2(shutter_speed)

    focal_length_35mm = int(round(focal_length * profile["sensor_crop_factor"]))

    now = datetime.now(timezone.utc)
    hour = _random_hour_for_scene(scene_type, rng)
    days_ago = rng.randint(0, 13)
    dt_original = now - timedelta(days=days_ago)
    dt_original = dt_original.replace(
        hour=hour,
        minute=rng.randint(0, 59),
        second=rng.randint(0, 59),
        microsecond=0,
    )
    dt_digitized = dt_original
    post_offset = timedelta(seconds=rng.randint(0, 6 * 3600))
    dt_modified = dt_original + post_offset

    dt_fmt = "%Y:%m:%d %H:%M:%S"
    dt_original_str = dt_original.strftime(dt_fmt)
    dt_digitized_str = dt_digitized.strftime(dt_fmt)
    dt_modified_str = dt_modified.strftime(dt_fmt)

    subsec = str(rng.randint(100, 999))

    body_serial = profile["body_serial_generator"](rng)
    lens_serial_num = _lens_serial(rng)

    software = _pick_software(profile, rng)

    lens_spec = (
        _float_to_rational(float(focal_min)),
        _float_to_rational(float(focal_max)),
        _float_to_rational(f_min),
        _float_to_rational(f_max),
    )

    zeroth_ifd = {
        piexif.ImageIFD.Make: profile["make"].encode(),
        piexif.ImageIFD.Model: profile["model"].encode(),
        piexif.ImageIFD.Software: software.encode(),
        piexif.ImageIFD.DateTime: dt_modified_str.encode(),
        piexif.ImageIFD.Orientation: 1,
        piexif.ImageIFD.YCbCrPositioning: 1,
        piexif.ImageIFD.XResolution: (72, 1),
        piexif.ImageIFD.YResolution: (72, 1),
        piexif.ImageIFD.ResolutionUnit: 2,
    }

    exif_ifd = {
        piexif.ExifIFD.ExifVersion: b"0220",
        piexif.ExifIFD.FlashpixVersion: b"0100",
        piexif.ExifIFD.ComponentsConfiguration: b"\x01\x02\x03\x00",
        piexif.ExifIFD.ColorSpace: 1,
        piexif.ExifIFD.DateTimeOriginal: dt_original_str.encode(),
        piexif.ExifIFD.DateTimeDigitized: dt_digitized_str.encode(),
        piexif.ExifIFD.SubSecTime: subsec.encode(),
        piexif.ExifIFD.SubSecTimeOriginal: subsec.encode(),
        piexif.ExifIFD.SubSecTimeDigitized: subsec.encode(),
        piexif.ExifIFD.ExposureTime: _shutter_to_rational(shutter_speed),
        piexif.ExifIFD.FNumber: _float_to_rational(fnumber),
        piexif.ExifIFD.ISOSpeedRatings: iso,
        piexif.ExifIFD.ApertureValue: _float_to_srational(aperture_value),
        piexif.ExifIFD.ShutterSpeedValue: _float_to_srational(shutter_speed_value),
        piexif.ExifIFD.FocalLength: _float_to_rational(focal_length),
        piexif.ExifIFD.FocalLengthIn35mmFilm: focal_length_35mm,
        piexif.ExifIFD.MeteringMode: rng.choice(METERING_MODES),
        piexif.ExifIFD.ExposureProgram: rng.choice([2, 3]),
        piexif.ExifIFD.ExposureMode: 0,
        piexif.ExifIFD.SceneCaptureType: rng.choice(SCENE_CAPTURE_TYPES),
        piexif.ExifIFD.CustomRendered: 0,
        piexif.ExifIFD.DigitalZoomRatio: (1, 1),
        piexif.ExifIFD.LensSpecification: lens_spec,
        piexif.ExifIFD.LensMake: profile["make"].encode(),
        piexif.ExifIFD.LensModel: lens_model.encode(),
        piexif.ExifIFD.LensSerialNumber: lens_serial_num.encode(),
        piexif.ExifIFD.BodySerialNumber: body_serial.encode(),
        piexif.ExifIFD.PixelXDimension: width,
        piexif.ExifIFD.PixelYDimension: height,
    }

    has_gps = False
    gps_ifd = {}

    if profile["is_phone"]:
        add_gps = gps if gps is not None else (rng.random() < 0.7)
        if add_gps:
            has_gps = True
            city = rng.choice(GPS_CITY_POLYGONS)
            lat = rng.uniform(city["lat_min"], city["lat_max"])
            lon = rng.uniform(city["lon_min"], city["lon_max"])

            gps_ifd = {
                piexif.GPSIFD.GPSVersionID: (2, 3, 0, 0),
                piexif.GPSIFD.GPSLatitudeRef: b"N" if lat >= 0 else b"S",
                piexif.GPSIFD.GPSLatitude: _deg_to_dms_rational(lat),
                piexif.GPSIFD.GPSLongitudeRef: b"E" if lon >= 0 else b"W",
                piexif.GPSIFD.GPSLongitude: _deg_to_dms_rational(lon),
                piexif.GPSIFD.GPSAltitudeRef: 0,
                piexif.GPSIFD.GPSAltitude: (rng.randint(0, 500), 1),
                piexif.GPSIFD.GPSTimeStamp: (
                    (dt_original.hour, 1),
                    (dt_original.minute, 1),
                    (dt_original.second, 1),
                ),
                piexif.GPSIFD.GPSDateStamp: dt_original.strftime("%Y:%m:%d").encode(),
                piexif.GPSIFD.GPSMapDatum: b"WGS-84",
            }

    thumbnail_bytes = _make_thumbnail(img)

    first_ifd = {
        piexif.ImageIFD.Orientation: 1,
        piexif.ImageIFD.XResolution: (72, 1),
        piexif.ImageIFD.YResolution: (72, 1),
        piexif.ImageIFD.ResolutionUnit: 2,
    }

    exif_dict = {
        "0th": zeroth_ifd,
        "Exif": exif_ifd,
        "GPS": gps_ifd,
        "1st": first_ifd,
        "thumbnail": thumbnail_bytes,
    }

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)

    img.close()

    return {
        "profile_name": profile["model"],
        "scene_type": scene_type,
        "iso": iso,
        "shutter_speed": shutter_speed,
        "fnumber": fnumber,
        "focal_length": focal_length,
        "has_gps": has_gps,
        "lens_model": lens_model,
        "body_serial": body_serial,
    }


def add_fake_exif(image_path: str) -> dict:
    return add_realistic_exif(image_path)
