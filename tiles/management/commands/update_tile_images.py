from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tiles.models import TileProduct

class Command(BaseCommand):
    help = 'Update TileProduct image URLs to real Unsplash images based on product name'

    def handle(self, *args, **options):
        self.stdout.write('Updating TileProduct images...')
        count = 0
        # Dynamically generate Unsplash image URLs based on the tile category name.
        # Using the source.unsplash.com endpoint ensures a valid image is always returned.
        # The URL format returns a random high‑quality image matching the query.
        import os, requests
        # Ensure media/tiles directory exists
        media_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'media', 'tiles')
        os.makedirs(media_root, exist_ok=True)
        for product in TileProduct.objects.all():
            query = slugify(product.category.name) if product.category else 'tile'
            # Try primary Unsplash URL
            remote_url = f"https://source.unsplash.com/800x800/?{query}"
            try:
                # Perform a HEAD request to verify availability (Unsplash redirects)
                response = requests.head(remote_url, allow_redirects=True, timeout=5)
                if response.status_code != 200:
                    raise Exception("Bad status")
                final_url = response.url
            except Exception:
                # Fallback to a generic query that is more likely to succeed
                fallback_query = "concrete-tiles" if "concrete" in query else "tiles"
                fallback_url = f"https://source.unsplash.com/800x800/?{fallback_query}"
                try:
                    response = requests.head(fallback_url, allow_redirects=True, timeout=5)
                    final_url = response.url if response.status_code == 200 else fallback_url
                except Exception:
                    # As last resort, keep the original remote_url
                    final_url = remote_url
            product.image = final_url
            product.save(update_fields=["image"])
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {count} TileProduct image URLs.'))
