from django.core.management.base import BaseCommand
from tiles.models import TileProduct
from tiles.services.image_gen import image_gen_service


class Command(BaseCommand):
    help = 'Generate AI tile design images for all products using Cloudflare SDXL'

    def add_arguments(self, parser):
        parser.add_argument('--product', type=str, help='Generate for specific product name (partial match)')
        parser.add_argument('--category', type=str, help='Generate for specific category slug')
        parser.add_argument('--limit', type=int, default=0, help='Max number of products to process (0=all)')
        parser.add_argument('--force', action='store_true', help='Re-generate even if image exists')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without generating')

    def handle(self, *args, **options):
        products = TileProduct.objects.filter(is_active=True)

        if options['product']:
            products = products.filter(name__icontains=options['product'])
        if options['category']:
            products = products.filter(category__slug=options['category'])
        if options['limit'] > 0:
            products = products[:options['limit']]

        total = products.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No products found matching criteria.'))
            return

        self.stdout.write(f'🎨 Will generate tile designs for {total} products')
        if options['dry_run']:
            for p in products:
                self.stdout.write(f'   📋 {p.name}')
                self.stdout.write(f'      Prompt: {self._build_prompt(p)[:120]}...')
            return

        if not image_gen_service.is_configured():
            self.stdout.write(self.style.ERROR('❌ Cloudflare AI not configured. Set CF_ACCOUNT_ID and CF_API_TOKEN in .env'))
            return

        success = 0
        failed = 0
        skipped = 0

        for i, product in enumerate(products, 1):
            if product.image and not options['force']:
                self.stdout.write(f'   ⏭️  [{i}/{total}] {product.name[:50]} — already has image (use --force)')
                skipped += 1
                continue

            prompt = self._build_prompt(product)
            self.stdout.write(f'   🔄 [{i}/{total}] {product.name[:50]}...')

            result = image_gen_service.generate(prompt)

            if result['success'] and result['image_file']:
                # Delete old image if exists
                if product.image:
                    product.image.delete(save=False)
                product.image = result['image_file']
                product.save(update_fields=['image'])
                success += 1
                self.stdout.write(self.style.SUCCESS(f'      ✅ Generated!'))
            else:
                failed += 1
                error = result.get('error', 'Unknown error')
                self.stdout.write(self.style.ERROR(f'      ❌ Failed: {error[:80]}'))

            # Small delay to avoid rate limiting
            import time
            time.sleep(1)

        self.stdout.write(f'\n📊 Results: {success} generated, {failed} failed, {skipped} skipped (of {total} total)')

    def _build_prompt(self, product):
        """Build an optimized prompt for tile design generation based on product attributes."""
        parts = []

        # Category-based base
        cat_name = product.category.name.lower() if product.category else ''

        # Effects
        effects = [e.name.lower() for e in product.effects.all()[:3]]
        if effects:
            parts.append(', '.join(effects))

        # Material
        if product.material:
            parts.append(product.material.lower())

        # Finishes
        finishes = [f.name.lower() for f in product.finishes.all()[:2]]
        if finishes:
            parts.append(', '.join(finishes))

        # Sizes for context
        sizes = list(product.sizes.all()[:2])
        if sizes:
            s = sizes[0]
            parts.append(f'{s.width_mm}x{s.height_mm}mm')

        # Build full prompt
        base = ' '.join(parts)

        # Ensure we have enough detail
        if len(base) < 30:
            base += f', {cat_name}'

        return base