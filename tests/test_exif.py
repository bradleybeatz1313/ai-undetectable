"""Tests for realistic EXIF metadata generation."""

import io
import math
import os
import sys

import piexif
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from exif_generator import add_realistic_exif
from exif_profiles import CAMERA_PROFILES


@pytest.fixture
def sample_image(tmp_path):
    """Create a minimal test JPEG."""
    img = Image.new("RGB", (640, 480), color=(128, 100, 80))
    path = str(tmp_path / "test.jpg")
    img.save(path, format="JPEG", quality=95)
    return path


def _generate_for_profile(profile, tmp_path, count=5):
    results = []
    for i in range(count):
        path = str(tmp_path / f"test_{profile['model']}_{i}.jpg")
        img = Image.new("RGB", (640, 480), color=(128, 100, 80))
        img.save(path, format="JPEG", quality=95)
        info = add_realistic_exif(path, profile=profile)
        exif_data = piexif.load(path)
        results.append((info, exif_data, path))
    return results


class TestLensCoherence:
    def test_lens_from_profile_pool(self, tmp_path):
        for profile in CAMERA_PROFILES:
            results = _generate_for_profile(profile, tmp_path, count=5)
            pool_names = {l[0] for l in profile["lens_pool"]}
            for info, _, _ in results:
                assert info["lens_model"] in pool_names, (
                    f"{profile['model']}: lens '{info['lens_model']}' not in pool"
                )


class TestExposureConsistency:
    def test_aperture_value_matches_fnumber(self, tmp_path):
        for profile in CAMERA_PROFILES:
            results = _generate_for_profile(profile, tmp_path, count=5)
            for info, exif_data, _ in results:
                fnumber = info["fnumber"]
                expected_av = 2 * math.log2(fnumber)

                av_rational = exif_data["Exif"][piexif.ExifIFD.ApertureValue]
                actual_av = av_rational[0] / av_rational[1]
                assert abs(actual_av - expected_av) < 0.01, (
                    f"{profile['model']}: ApertureValue {actual_av} != expected {expected_av}"
                )

    def test_shutter_speed_value_matches_exposure(self, tmp_path):
        for profile in CAMERA_PROFILES:
            results = _generate_for_profile(profile, tmp_path, count=5)
            for info, exif_data, _ in results:
                shutter = info["shutter_speed"]
                expected_sv = -math.log2(shutter)

                sv_rational = exif_data["Exif"][piexif.ExifIFD.ShutterSpeedValue]
                actual_sv = sv_rational[0] / sv_rational[1]
                assert abs(actual_sv - expected_sv) < 0.01, (
                    f"{profile['model']}: ShutterSpeedValue {actual_sv} != expected {expected_sv}"
                )


class TestTimestamps:
    def test_original_before_modified(self, tmp_path):
        for profile in CAMERA_PROFILES:
            results = _generate_for_profile(profile, tmp_path, count=5)
            for _, exif_data, _ in results:
                dt_orig = exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
                dt_mod = exif_data["0th"][piexif.ImageIFD.DateTime].decode()
                assert dt_orig <= dt_mod, (
                    f"{profile['model']}: DateTimeOriginal ({dt_orig}) > DateTime ({dt_mod})"
                )


class TestGPS:
    def test_gps_only_on_phones(self, tmp_path):
        for profile in CAMERA_PROFILES:
            results = _generate_for_profile(profile, tmp_path, count=30)
            gps_count = sum(1 for info, _, _ in results if info["has_gps"])

            if not profile["is_phone"]:
                assert gps_count == 0, (
                    f"{profile['model']}: ILC should have no GPS, got {gps_count}/30"
                )
            else:
                assert gps_count > 0, (
                    f"{profile['model']}: phone should have some GPS, got 0/30"
                )


class TestThumbnail:
    def test_thumbnail_present_and_valid(self, tmp_path):
        for profile in CAMERA_PROFILES:
            results = _generate_for_profile(profile, tmp_path, count=2)
            for _, exif_data, _ in results:
                thumb = exif_data.get("thumbnail")
                assert thumb is not None and len(thumb) > 0, (
                    f"{profile['model']}: missing thumbnail"
                )
                img = Image.open(io.BytesIO(thumb))
                assert img.format == "JPEG"
                assert img.size[0] == 160


class TestFieldCoverage:
    def test_required_exif_fields(self, sample_image):
        add_realistic_exif(sample_image)
        exif_data = piexif.load(sample_image)

        required_0th = [
            piexif.ImageIFD.Make,
            piexif.ImageIFD.Model,
            piexif.ImageIFD.Software,
            piexif.ImageIFD.DateTime,
            piexif.ImageIFD.Orientation,
        ]
        for tag in required_0th:
            assert tag in exif_data["0th"], f"Missing 0th IFD tag {tag}"

        required_exif = [
            piexif.ExifIFD.ExifVersion,
            piexif.ExifIFD.FlashpixVersion,
            piexif.ExifIFD.ComponentsConfiguration,
            piexif.ExifIFD.ColorSpace,
            piexif.ExifIFD.ExposureTime,
            piexif.ExifIFD.FNumber,
            piexif.ExifIFD.ISOSpeedRatings,
            piexif.ExifIFD.FocalLength,
            piexif.ExifIFD.FocalLengthIn35mmFilm,
            piexif.ExifIFD.LensModel,
            piexif.ExifIFD.BodySerialNumber,
            piexif.ExifIFD.PixelXDimension,
            piexif.ExifIFD.PixelYDimension,
        ]
        for tag in required_exif:
            assert tag in exif_data["Exif"], f"Missing Exif IFD tag {tag}"


class TestVariation:
    def test_batch_differs(self, tmp_path):
        cameras = set()
        isos = set()
        for i in range(5):
            path = str(tmp_path / f"vary_{i}.jpg")
            img = Image.new("RGB", (640, 480), color=(128, 100, 80))
            img.save(path, format="JPEG", quality=95)
            info = add_realistic_exif(path)
            cameras.add(info["profile_name"])
            isos.add(info["iso"])
        assert len(cameras) > 1, "5 random runs should pick more than 1 camera"
        assert len(isos) > 1, "5 random runs should produce more than 1 ISO"


if __name__ == "__main__":
    import textwrap

    print("\n" + "=" * 70)
    print("EXIF Generation Summary")
    print("=" * 70)

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        for profile in CAMERA_PROFILES:
            print(f"\n--- {profile['model']} ---")
            for i in range(3):
                path = os.path.join(td, f"{profile['model']}_{i}.jpg")
                img = Image.new("RGB", (640, 480), color=(128, 100, 80))
                img.save(path, format="JPEG", quality=95)
                info = add_realistic_exif(path, profile=profile)
                gps_str = "GPS" if info["has_gps"] else "no GPS"
                print(
                    f"  [{i+1}] {info['lens_model']:<40} "
                    f"ISO {info['iso']:>5}  f/{info['fnumber']:<5.1f}  "
                    f"1/{int(round(1/info['shutter_speed'])):>4}s  "
                    f"{info['focal_length']:>5.1f}mm  {gps_str}"
                )

    print("\n" + "=" * 70)
    print("Run `pytest tests/test_exif.py -v` for full validation.")
    print("=" * 70)
