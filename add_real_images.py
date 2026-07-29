import os
import requests
import django
import cloudinary.uploader
from dotenv import load_dotenv

# Django Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studiomathri.settings")
django.setup()
load_dotenv()

from tiles.models import TileProduct
from django.db.models import Q

# Cloudflare Settings
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_IMAGE_MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"
CF_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run"

def generate_and_upload():
    # Broken links மற்றும் Empty images-ஐ தேடுகிறது
    tiles_to_fix = TileProduct.objects.filter(
        Q(image__isnull=True) | 
        Q(image='') | 
        Q(image__icontains='unsplash') |
        Q(image__icontains='source.')
    )

    total = tiles_to_fix.count()
    if total == 0:
        print("✅ All tiles already have real images!")
        return

    print(f"🚀 Found {total} tiles. Generating via Cloudflare AI...\n")

    for index, tile in enumerate(tiles_to_fix, 1):
        prompt = f"Photorealistic high quality texture of {tile.name}, seamless tile pattern, studio lighting, 8k resolution, architectural photography"
        print(f"[{index}/{total}] Generating: {tile.name}...")

        try:
            # 1. Cloudflare AI-க்கு Request அனுப்புகிறது
            response = requests.post(
                f"{CF_BASE_URL}/{CF_IMAGE_MODEL}",
                headers={
                    "Authorization": f"Bearer {CF_API_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024,
                    "steps": 20,
                    "seed": index * 1000
                }
            )

            if response.status_code != 200:
                print(f"   ⚠️ Cloudflare Error: {response.status_code}")
                continue

            # 2. Response Type-ஐ பார்க்கிறது (Raw PNG அல்லது JSON Base64)
            content_type = response.headers.get('Content-Type', '')
            
            if 'image/' in content_type:
                # Cloudflare நேரடியாக Raw Image கொடுத்துச்சு
                img_data = response.content
                print("   ↳ Received Raw PNG from Cloudflare")
            else:
                # Cloudflare JSON-ல Base64 கொடுத்துச்சு
                result = response.json()
                image_b64 = result.get('result', {}).get('image', '')
                if not image_b64:
                    print(f"   ⚠️ No image in response")
                    continue
                import base64
                img_data = base64.b64decode(image_b64)
                print("   ↳ Decoded Base64 Image")

            # 3. Cloudinary-க்கு Upload செய்கிறது
            upload_result = cloudinary.uploader.upload(
                img_data,
                folder="tiles_catalog",
                public_id=tile.slug,
                overwrite=True
            )

            # 4. Database-ல Cloudinary URL-ஐ Save செய்கிறது
            tile.image = upload_result['secure_url']
            tile.save(update_fields=['image'])
            
            print(f"   ✅ Saved: {tile.name}")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    print("\n🎉 Done! Check your catalog page.")

if __name__ == "__main__":
    generate_and_upload()