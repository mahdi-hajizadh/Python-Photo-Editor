"""Pure, non-destructive RGB photo transformations and image I/O."""
from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO, Literal

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

Color = Literal["red", "green", "blue"]
MAX_IMAGE_PIXELS = 40_000_000


@dataclass(frozen=True)
class EditSettings:
    """Editor settings applied in the original application's order."""

    brightness: int = 0
    grayscale: bool = False
    negative: bool = False
    selective_color: bool = False
    color: Color = "red"
    threshold: int = 25

    def __post_init__(self) -> None:
        if not -100 <= self.brightness <= 100:
            raise ValueError("Brightness must be between -100 and 100.")
        if not 0 <= self.threshold <= 100:
            raise ValueError("Threshold must be between 0 and 100.")
        if self.color not in ("red", "green", "blue"):
            raise ValueError("Color must be red, green, or blue.")


def load_image(source: bytes | BinaryIO) -> Image.Image:
    """Decode a supported photo, normalize EXIF orientation, and return RGB.

    Only JPEG and PNG input is supported. Reject corrupt or oversized files.
    """
    stream = BytesIO(source) if isinstance(source, bytes) else source
    try:
        with Image.open(stream) as original:
            if original.format not in {"JPEG", "PNG"}:
                raise ValueError("Only JPEG and PNG photos are supported.")
            if original.width * original.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image exceeds the 40-megapixel safety limit.")
            original.load()
            return ImageOps.exif_transpose(original).convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValueError("The file is not a valid JPEG or PNG image.") from exc


def apply_edits(image: Image.Image, settings: EditSettings) -> tuple[Image.Image, float | None]:
    """Return edited image and optional percent of selectively colored pixels.

    Uses the original project's arithmetic-mean grayscale and selective-color
    calculation. The input image is never modified.
    """
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    result = rgb.astype(np.float32)
    result = np.clip(result + settings.brightness, 0, 255)
    percentage = None

    if settings.selective_color:
        channel = ("red", "green", "blue").index(settings.color)
        gray = result.mean(axis=2)
        mask = result[:, :, channel] - gray > settings.threshold
        result = np.where(mask[:, :, None], result, gray[:, :, None])
        percentage = float(mask.mean() * 100)

    if settings.grayscale:
        gray = result.mean(axis=2)
        result = np.repeat(gray[:, :, None], 3, axis=2)

    if settings.negative:
        result = 255 - result

    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), "RGB"), percentage


def encode_image(image: Image.Image, file_format: Literal["PNG", "JPEG"] = "PNG", quality: int = 95) -> bytes:
    """Encode an edited image for download without writing local files."""
    if file_format not in ("PNG", "JPEG"):
        raise ValueError("Export format must be PNG or JPEG.")
    if not 1 <= quality <= 100:
        raise ValueError("JPEG quality must be between 1 and 100.")
    output = BytesIO()
    options = {"quality": quality, "subsampling": 0} if file_format == "JPEG" else {}
    image.convert("RGB").save(output, format=file_format, **options)
    return output.getvalue()
