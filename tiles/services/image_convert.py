"""
Image format conversion service.

Converts PNG/JPEG (and other flattened raster) images into TIFF, BMP, PSD or
PDF, optionally with "extracted layers": the source image's color channels
are emitted as separate layers (PSD) or pages (TIFF/PDF).

Pure functions — no Django request/response handling here (that lives in the
views) — so everything is directly unit-testable.
"""

from __future__ import annotations

from io import BytesIO

from PIL import Image
from PIL import ImageSequence

# ─────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────

#: Target formats offered by the converter.
FORMAT_CHOICES = ("tiff", "bmp", "psd", "pdf")

#: Canonical HTTP content types + file extensions per target format.
FORMAT_META = {
    "tiff": {"content_type": "image/tiff", "extension": "tiff"},
    "bmp": {"content_type": "image/bmp", "extension": "bmp"},
    "psd": {"content_type": "image/vnd.adobe.photoshop", "extension": "psd"},
    "pdf": {"content_type": "application/pdf", "extension": "pdf"},
}

#: Source formats we accept. Verified AFTER PIL opens the bytes, so we go by
#: what the file actually is, not by its extension.
ALLOWED_SOURCE_FORMATS = {"PNG", "JPEG", "JPG", "WEBP"}

#: Hard cap on uploaded source bytes (10 MB).
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

#: Default output resolution when none supplied.
DEFAULT_DPI = 300


class ImageConversionError(ValueError):
    """User-safe conversion failure (bad input, unsupported type, size cap)."""


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────


def _coerce_dpi(dpi) -> tuple[int, int]:
    """Normalize a dpi value (int, str, or (x, y) tuple) into a positive
    (dpi, dpi) tuple."""
    if isinstance(dpi, (tuple, list)) and len(dpi) >= 1:
        dpi = dpi[0]
    try:
        dpi_int = int(float(dpi))
    except (TypeError, ValueError):
        dpi_int = DEFAULT_DPI
    if dpi_int <= 0:
        dpi_int = DEFAULT_DPI
    return (dpi_int, dpi_int)


def open_source_image(source) -> Image.Image:
    """
    Open raw source bytes and validate the format.

    Returns a PIL image in a mode suitable for channel extraction
    (RGB, or RGBA when the source has transparency).  Raises
    ImageConversionError with a user-safe message otherwise.
    """
    try:
        img = Image.open(source)
        img.load()
    except Exception:
        raise ImageConversionError(
            "That file doesn't look like a valid image. "
            "Please upload a PNG, JPEG or WebP image."
        )

    fmt = (img.format or "").upper()
    if fmt not in ALLOWED_SOURCE_FORMATS:
        raise ImageConversionError(
            f"Unsupported source format \"{fmt or 'unknown'}\". "
            "Supported source formats: PNG, JPEG and WebP."
        )

    # Promote exotic modes to something with well-defined R/G/B channels.
    if img.mode == "P":
        img = img.convert("RGBA") if "transparency" in img.info else img.convert("RGB")
    elif img.mode not in ("RGB", "RGBA"):
        # L, LA, CMYK, I;16, … → RGB(A)
        if "A" in img.getbands():
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

    return img


def extract_channel_layers(img: Image.Image) -> list[tuple[str, Image.Image]]:
    """
    Split a PIL image into per-channel layers.

    Returns a list of ``(name, image)`` tuples, one per channel: the Red,
    Green and Blue channels as full-color RGB images carrying only that
    channel's data, plus Alpha when the source has a transparency band.

    RGB (8, 60, 200) →
        Red   layer (8, 0, 0)
        Green layer (0, 60, 0)
        Blue  layer (0, 0, 200)
    """
    img = img.convert("RGBA") if "A" in img.getbands() else img.convert("RGB")
    bands = img.split()  # (R, G, B) or (R, G, B, A)

    names = ["Red", "Green", "Blue"][: len(bands)] + (
        ["Alpha"] if len(bands) > 3 else []
    )

    layers: list[tuple[str, Image.Image]] = []
    for idx, (name, band) in enumerate(zip(names, bands)):
        if name == "Alpha":
            # Show the alpha band as a grayscale image (that's how Photoshop
            # renders a mask/alpha channel).
            layers.append((name, band.convert("RGB")))
        else:
            empty = Image.new("L", img.size, 0)
            chans = [empty, empty, empty]
            chans[idx] = band
            layers.append((name, Image.merge("RGB", chans)))
    return layers


def get_image_metadata(source) -> dict:
    """Best-effort metadata peek for the upload-preview UI."""
    img = open_source_image(source)
    return {
        "format": (img.format or "").upper(),
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "has_alpha": "A" in img.getbands(),
    }


def _normalize_geometry(
    img: Image.Image, width=None, height=None
) -> Image.Image:
    """Optionally resize before conversion. Missing width/height keep aspect."""
    try:
        w = int(width) if width else None
        h = int(height) if height else None
    except (TypeError, ValueError):
        w = h = None
    if w and h and (w, h) != img.size:
        return img.resize((w, h), Image.LANCZOS)
    return img


# ─────────────────────────────────────────────────────────────────────────
# Encoders
# ─────────────────────────────────────────────────────────────────────────


def save_bmp(img: Image.Image, dpi=None) -> BytesIO:
    """BMP is a single-layer format: emit the flattened image."""
    output = BytesIO()
    img.convert("RGB").save(output, format="BMP", dpi=_coerce_dpi(dpi))
    return output


def save_multipage_tiff(img: Image.Image, layers=None, dpi=None) -> BytesIO:
    """
    Multi-page TIFF. Page 1 is the original (flattened) image; one page per
    extracted channel layer follows when ``layers`` is provided.
    """
    pages = [img.convert("RGB")]
    if layers:
        pages.extend(layer.convert("RGB") for _, layer in layers)
    output = BytesIO()
    dpi_t = _coerce_dpi(dpi)
    pages[0].save(
        output,
        format="TIFF",
        save_all=True,
        append_images=pages[1:],
        dpi=dpi_t,
        compression="tiff_deflate",
    )
    return output


def save_multipage_pdf(img: Image.Image, layers=None, dpi=None) -> BytesIO:
    """
    Multi-page PDF. Page 1 is the original (flattened) image; one page per
    extracted channel layer follows when ``layers`` is provided.
    """
    pages = [img.convert("RGB")]
    if layers:
        pages.extend(layer.convert("RGB") for _, layer in layers)
    output = BytesIO()
    dpi_t = _coerce_dpi(dpi)
    pages[0].save(
        output,
        format="PDF",
        save_all=True,
        append_images=pages[1:],
        resolution=dpi_t[0],
    )
    return output


def save_psd(img: Image.Image, layers=None, dpi=None) -> BytesIO:
    """
    Real layered PSD. The bottom layer is the original (flattened) image;
    one layer per extracted channel follows when ``layers`` is provided.

    Uses pytoshop's nested_layers API. Notes pinned by the dependency spike:
      * channels must be uint8 numpy planes keyed by enums.ChannelId;
      * a full-opacity alpha plane must be provided (pytoshop would otherwise
        insert an internal ``image=-1`` stub that numpy>=2 refuses to cast);
      * compression must be ``raw`` (the RLE path imports a stale ``packbits``
        module that no longer exists).
    """
    import numpy as np
    from pytoshop import enums
    from pytoshop.user import nested_layers

    def to_psd_layer(image: Image.Image, name: str) -> "nested_layers.Image":
        arr = np.asarray(image.convert("RGB"), dtype=np.uint8)
        h, w = arr.shape[:2]
        channels = {
            enums.ChannelId.red: arr[:, :, 0],
            enums.ChannelId.green: arr[:, :, 1],
            enums.ChannelId.blue: arr[:, :, 2],
            enums.ChannelId.transparency: np.full((h, w), 255, dtype=np.uint8),
        }
        return nested_layers.Image(
            name=name,
            visible=True,
            opacity=255,
            channels=channels,
            top=0,
            left=0,
        )

    # PSD layer list is bottom-up: background first, channel layers above.
    nlayers = [to_psd_layer(img, "Background")]
    if layers:
        nlayers.extend(
            to_psd_layer(layer, f"{name} Layer") for name, layer in layers
        )

    # NB: despite the docstring saying (height, width), pytoshop's `size`
    # expects (width, height) — pinned by the dependency spike.
    psd = nested_layers.nested_layers_to_psd(
        nlayers,
        color_mode=enums.ColorMode.rgb,
        size=img.size,
        depth=enums.ColorDepth.depth8,
        compression=enums.Compression.raw,
    )
    # DPI metadata: pytoshop ignores its dpi arg in this code path, so we
    # patch the image resource block directly (ResPI 1005).
    from pytoshop import image_resources

    try:
        dpi_value = float(_coerce_dpi(dpi)[0])
        res1005 = image_resources.ResolutionInfo(
            h_res=dpi_value,
            h_res_unit=image_resources.ResolutionUnit.pixels_per_inch,
            width_unit=image_resources.ResUnit.inches,
            v_res=dpi_value,
            v_res_unit=image_resources.ResolutionUnit.pixels_per_inch,
            height_unit=image_resources.ResUnit.inches,
        )
        psd.image_resources.set_data(image_resources.ResourceId.resolution_info, res1005)
    except Exception:
        pass  # metadata is best-effort; pixels already written below

    output = BytesIO()
    psd.write(output)
    return output


# ─────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────


def convert_image(
    source,
    target_format: str,
    *,
    layers: bool = True,
    width=None,
    height=None,
    dpi=None,
) -> BytesIO:
    """
    Convert raw PNG/JPEG/WebP bytes to TIFF/BMP/PSD/PDF.

    ``layers=True`` extracts the color channels as separate layers (TIFF/PDF
    pages, PSD layers). BMP ignores it (single-layer format).

    Raises ImageConversionError (a ValueError) with a user-safe message on
    invalid input.
    """
    target_format = (target_format or "").strip().lower()
    if target_format not in FORMAT_CHOICES:
        raise ImageConversionError(
            "Unsupported target format. Choose one of: TIFF, BMP, PSD, PDF."
        )

    img = open_source_image(source)

    if getattr(source, "tell", None) is not None:
        try:
            size = source.seek(0, 2)  # end
            source.seek(0)
            if size > MAX_UPLOAD_BYTES:
                raise ImageConversionError(
                    "Image is too large. Maximum upload size is 10 MB."
                )
        except OSError:
            pass

    img = _normalize_geometry(img, width, height)
    channel_layers = extract_channel_layers(img) if layers else []
    dpi_t = _coerce_dpi(dpi)

    if target_format == "tiff":
        return save_multipage_tiff(img, channel_layers, dpi_t)
    if target_format == "pdf":
        return save_multipage_pdf(img, channel_layers, dpi_t)
    if target_format == "psd":
        return save_psd(img, channel_layers, dpi_t)
    return save_bmp(img, dpi_t)


def count_pages(output: BytesIO) -> int:
    """
    Count frames in a produced TIFF/PDF (test helper + debug).

    PIL reads multi-page TIFF natively but cannot re-read PDF, so for PDF we
    count the page objects in the raw stream (Pillow emits exactly one
    ``/Type /Page`` dict per page, vs ``/Pages`` for the page tree).
    """
    output.seek(0)
    data = output.read()
    if data[:5] == b"%PDF-":
        return data.count(b"/Type /Page") - data.count(b"/Type /Pages")
    img = Image.open(BytesIO(data))
    return sum(1 for _ in ImageSequence.Iterator(img))
