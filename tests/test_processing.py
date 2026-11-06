"""Unit tests for the real image pipeline."""
from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from src.photo_editor import EditSettings, apply_edits, encode_image, load_image


@pytest.fixture
def image():
    return Image.fromarray(np.array([[[200, 20, 10], [10, 100, 240]]], dtype=np.uint8))


def test_load_png_and_jpeg(image):
    for fmt in ("PNG", "JPEG"):
        data = encode_image(image, fmt)
        loaded = load_image(data)
        assert loaded.mode == "RGB"
        assert loaded.size == image.size


def test_invalid_input():
    with pytest.raises(ValueError, match="valid"):
        load_image(b"not an image")


def test_unsupported_format(image):
    buffer = BytesIO()
    image.save(buffer, "BMP")
    with pytest.raises(ValueError, match="Only JPEG"):
        load_image(buffer.getvalue())


def test_brightness_and_clipping(image):
    result, _ = apply_edits(image, EditSettings(brightness=100))
    assert np.asarray(result).tolist() == [[[255, 120, 110], [110, 200, 255]]]


def test_grayscale(image):
    result, _ = apply_edits(image, EditSettings(grayscale=True))
    pixels = np.asarray(result)
    assert np.all(pixels[:, :, 0] == pixels[:, :, 1])
    assert pixels[0, 0, 0] == 76


def test_negative(image):
    result, _ = apply_edits(image, EditSettings(negative=True))
    assert np.asarray(result)[0, 0].tolist() == [55, 235, 245]


def test_selective_color(image):
    result, percent = apply_edits(image, EditSettings(selective_color=True, color="red"))
    assert percent == 50.0
    assert np.asarray(result)[0, 0].tolist() == [200, 20, 10]
    assert len(set(np.asarray(result)[0, 1].tolist())) == 1


def test_combined_order(image):
    result, _ = apply_edits(image, EditSettings(brightness=10, grayscale=True, negative=True))
    assert np.asarray(result)[0, 0].tolist() == [168, 168, 168]


def test_no_mutation(image):
    original = np.asarray(image).copy()
    apply_edits(image, EditSettings(brightness=80, negative=True))
    assert np.array_equal(np.asarray(image), original)


def test_export_roundtrip(image):
    for fmt in ("PNG", "JPEG"):
        output = encode_image(image, fmt)
        assert load_image(output).size == image.size


def test_invalid_settings_and_export(image):
    with pytest.raises(ValueError):
        EditSettings(brightness=101)
    with pytest.raises(ValueError):
        EditSettings(threshold=-1)
    with pytest.raises(ValueError):
        EditSettings(color="yellow")
    with pytest.raises(ValueError):
        encode_image(image, "GIF")


def test_one_pixel_image():
    single = Image.new("RGB", (1, 1), (0, 0, 0))
    edited, percent = apply_edits(single, EditSettings(selective_color=True))
    assert edited.size == (1, 1)
    assert percent == 0.0


def test_exif_orientation():
    image = Image.new("RGB", (2, 3), "red")
    exif = Image.Exif()
    exif[274] = 6
    buffer = BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    assert load_image(buffer.getvalue()).size == (3, 2)
