import base64
import io
import uuid
import math
import requests

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


# ─────────────────────────────────────────────────────────────
# Prompt engineering — force SDXL to produce real tile products
# ─────────────────────────────────────────────────────────────

STYLE_PREFIXES = {
    "realistic": (
        "professional tile product photography, photorealistic, "
        "true-to-life material colors and surface texture, "
        "macro detail of the tile face, sharp focus, 8k, "
    ),
    "artistic": (
        "decorative artisan tile design, handcrafted painterly pattern, "
        "rich saturated glaze colors, artistic surface detail, "
    ),
    "minimalist": (
        "minimalist tile design, clean simple modern pattern, "
        "matt surface, neutral tones, precise uniform edges, "
    ),
    "luxury": (
        "luxury premium tile, high-end marble and stone look, "
        "polished reflective surface, elegant veining, opulent finish, "
    ),
    "industrial": (
        "industrial tile design, raw concrete and cement texture, "
        "strong matte surface, rugged urban material feel, "
    ),
}

TILE_CTX = (
    "a single square tile fills the entire frame edge to edge, "
    "flat top-down front view, perfectly flat surface, "
    "seamless texture across the whole tile face, "
    "visible material structure of ceramic porcelain tile, "
    "sharp focus over the entire surface, factory tile catalog photo, "
    "even studio lighting, no background, no props, no room, "
    "no shadows at the edges, no border, no frame"
)


# ─────────────────────────────────────────────────────────────
# Post-processing — turn the raw SDXL output into a tile product
# ─────────────────────────────────────────────────────────────

def _draw_tile_grid(img, cells=2, line_color=(60, 60, 60, 55), line_w=2):
    """Draw subtle grout lines over the image so the surface reads as a
    tiled wall/floor rather than one abstract square."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    for i in range(1, cells):
        x = round(w * i / cells)
        y = round(h * i / cells)
        draw.line([(x, 0), (x, h)], fill=line_color, width=line_w)
        draw.line([(0, y), (w, y)], fill=line_color, width=line_w)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _studio_light(img):
    """Radial vignette + soft diagonal highlight sweep, mimicking studio
    product photography lighting."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    # Vignette: darker corners via concentric ellipses
    steps = 40
    max_dim = math.hypot(w, h) / 2
    cx, cy = w / 2, h / 2
    for i in range(steps):
        t = i / steps
        radius = max_dim * (0.55 + 0.55 * t)
        alpha = int(38 * (t ** 1.6))
        d.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=alpha, width=int(max_dim / steps) + 2,
        )
    dark = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    vignette = Image.composite(dark, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask)

    # Soft diagonal highlight sweep from top-left
    sweep = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(sweep)
    for i in range(0, int(w * 1.4), 6):
        band = int(26 * max(0.0, 1 - abs(i - w * 0.35) / (w * 0.5)))
        sd.line([(i, 0), (i - int(w * 0.4), h)], fill=band, width=7)
    sweep = sweep.filter(ImageFilter.GaussianBlur(24))
    # White highlight layer whose alpha comes from the sweep (max ~35%)
    white = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    highlight = Image.merge(
        "RGBA", (white.split()[0], white.split()[1], white.split()[2],
                 sweep.point(lambda p: int(p * 0.35)))
    )

    out = Image.alpha_composite(img.convert("RGBA"), vignette)
    out = Image.alpha_composite(out, highlight)
    return out


def _postprocess(img):
    """Apply the full 'real tile product' pipeline to a raw generated image."""
    img = img.convert("RGB")

    # Tile-relevant chromatic boost
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.06)
    img = ImageEnhance.Brightness(img).enhance(1.04)

    # Slight sharpening for surface detail
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))

    # Grout-line grid so the structure reads as tiles
    img = _draw_tile_grid(img)

    # Studio lighting: vignette + highlight sweep
    img = _studio_light(img)

    return img.convert("RGB")


class CloudflareImageGen:

    def __init__(self):
        self.account_id = settings.CF_ACCOUNT_ID
        self.api_token = settings.CF_API_TOKEN
        self.model = settings.CF_IMAGE_MODEL
        self.base_url = settings.CF_BASE_URL

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def is_configured(self):
        return bool(self.account_id and self.api_token)

    def _get_image_bytes(self, response):

        content_type = response.headers.get("Content-Type", "")

        if content_type.startswith("image/"):
            return response.content

        data = response.json()

        if not data.get("success"):
            errors = data.get("errors", [])
            msg = errors[0]["message"] if errors else "Cloudflare Error"
            raise Exception(msg)

        result = data.get("result", {})

        if "image" in result:
            return base64.b64decode(result["image"])

        return None

    def build_prompt(self, prompt, style="realistic"):
        """Compose the full SDXL prompt. Public so tests can verify it."""
        return (
            STYLE_PREFIXES.get(style, STYLE_PREFIXES["realistic"])
            + prompt
            + ", "
            + TILE_CTX
        )

    def generate(self, prompt, style="realistic"):

        if not self.is_configured():
            return {
                "success": False,
                "image_file": None,
                "error": "Cloudflare AI not configured",
            }

        full_prompt = self.build_prompt(prompt, style)

        try:

            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=self.headers,
                json={
                    "prompt": full_prompt,
                    "width": 768,
                    "height": 768,
                    "num_steps": 20,
                    "guidance": 7.5,
                },
                timeout=120,
            )

            response.raise_for_status()

            img_bytes = self._get_image_bytes(response)

            if not img_bytes:
                return {
                    "success": False,
                    "image_file": None,
                    "error": "No image returned by Cloudflare",
                }

            # Post-process into a realistic tile product photo
            image = _postprocess(Image.open(io.BytesIO(img_bytes)))

            buffer = io.BytesIO()

            image.save(buffer, format="JPEG", quality=92)

            buffer.seek(0)

            filename = f"tile_{uuid.uuid4().hex}.jpg"

            image_file = InMemoryUploadedFile(
                buffer,
                None,
                filename,
                "image/jpeg",
                buffer.getbuffer().nbytes,
                None,
            )

            return {
                "success": True,
                "image_file": image_file,
                "error": None,
            }

        except Exception as e:

            return {
                "success": False,
                "image_file": None,
                "error": str(e),
            }


image_gen_service = CloudflareImageGen()
