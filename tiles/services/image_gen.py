import base64
import io
import uuid
import requests

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


STYLE_PREFIXES = {
    "realistic": "photorealistic, ultra realistic, 8k, ",
    "artistic": "artistic, creative, ",
    "minimalist": "minimalist, clean, modern, ",
    "luxury": "luxury, premium, elegant, ",
    "industrial": "industrial, raw, urban, ",
}

TILE_CTX = (
    "ceramic tile design, porcelain tile, wall tile, floor tile, "
    "premium tile texture, product photography, studio lighting, "
    "white background, highly detailed"
)


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

        print("=" * 60)
        print("STATUS :", response.status_code)
        print("CONTENT TYPE :", content_type)
        print("=" * 60)

        if content_type.startswith("image/"):
            return response.content

        data = response.json()

        print(data)

        if not data.get("success"):
            errors = data.get("errors", [])
            msg = errors[0]["message"] if errors else "Cloudflare Error"
            raise Exception(msg)

        result = data.get("result", {})

        if "image" in result:
            return base64.b64decode(result["image"])

        return None

    def generate(self, prompt, style="realistic"):

        if not self.is_configured():
            return {
                "success": False,
                "image_file": None,
                "error": "Cloudflare AI not configured",
            }

        full_prompt = (
            STYLE_PREFIXES.get(style, "")
            + prompt
            + ", "
            + TILE_CTX
        )

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

            print("=" * 60)
            print(response.status_code)
            print(response.text[:1000])
            print("=" * 60)

            response.raise_for_status()

            img_bytes = self._get_image_bytes(response)

            if not img_bytes:
                return {
                    "success": False,
                    "image_file": None,
                    "error": "No image returned by Cloudflare",
                }

            image = Image.open(io.BytesIO(img_bytes))

            if image.mode != "RGB":
                image = image.convert("RGB")

            buffer = io.BytesIO()

            image.save(buffer, format="PNG")

            buffer.seek(0)

            filename = f"tile_{uuid.uuid4().hex}.png"

            image_file = InMemoryUploadedFile(
                buffer,
                None,
                filename,
                "image/png",
                buffer.getbuffer().nbytes,
                None,
            )

            return {
                "success": True,
                "image_file": image_file,
                "error": None,
            }

        except Exception as e:

            print("IMAGE ERROR :", str(e))

            return {
                "success": False,
                "image_file": None,
                "error": str(e),
            }


image_gen_service = CloudflareImageGen()