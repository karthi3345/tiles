from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tiles.models import (
    Country, State, City, Village,
    TileCategory, TileEffect, TileFinish, TileSize, TileProduct, MarketInsight
)


class Command(BaseCommand):
    help = 'Seed Studio Mathri with 10 countries, all states/cities/villages, and complete tile catalog'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Studio Mathri database...\n')

        self._seed_tile_meta()
        self._seed_tiles()
        self._seed_locations()
        self._link_tiles_to_countries()

        self.stdout.write(self.style.SUCCESS('\n✅ Studio Mathri seeding complete!'))

    # ─────────── TILE METADATA ───────────

    def _seed_tile_meta(self):
        self.stdout.write('  Seeding tile categories, effects, finishes, sizes...')

        categories = [
            ('Porcelain Floor Tiles', 'floor', 'lucide:square', 1),
            ('Ceramic Floor Tiles', 'floor', 'lucide:grid-3x3', 2),
            ('Vitrified Floor Tiles', 'floor', 'lucide:diamond', 3),
            ('Porcelain Wall Tiles', 'wall', 'lucide:rectangle-vertical', 4),
            ('Ceramic Wall Tiles', 'wall', 'lucide:columns-3', 5),
            ('Mosaic Tiles', 'both', 'lucide:layout-grid', 6),
            ('Subway Tiles', 'wall', 'lucide:train-front', 7),
            ('Natural Stone Tiles', 'both', 'lucide:mountain', 8),
            ('Large Format Slabs', 'both', 'lucide:rectangle-horizontal', 9),
            ('Wood Look Tiles', 'floor', 'lucide:trees', 10),
            ('Marble Effect Tiles', 'both', 'lucide:gem', 11),
            ('Outdoor / Exterior Tiles', 'special', 'lucide:sun', 12),
            ('Swimming Pool Tiles', 'special', 'lucide:waves', 13),
            ('Parking / Heavy Duty Tiles', 'special', 'lucide:car', 14),
            ('Anti-Slip Tiles', 'special', 'lucide:shield-check', 15),
            ('Kitchen Backsplash Tiles', 'wall', 'lucide:chef-hat', 16),
            ('Bathroom Tiles', 'both', 'lucide:bath', 17),
            ('Commercial Tiles', 'floor', 'lucide:building-2', 18),
            ('Terracotta / Rustic Tiles', 'both', 'lucide:flame', 19),
            ('3D / Textured Wall Tiles', 'wall', 'lucide:box', 20),
            ('Metallic Effect Tiles', 'both', 'lucide:sparkles', 21),
            ('Geometric Pattern Tiles', 'both', 'lucide:hexagon', 22),
            ('Concrete Effect Tiles', 'both', 'lucide:construction', 23),
            ('Glass Tiles', 'wall', 'lucide:glass-water', 24),
        ]

        for name, ttype, icon, order in categories:
            TileCategory.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'icon': icon,
                    'tile_type': ttype,
                    'sort_order': order,
                }
            )

        effects = [
            'Marble Effect', 'Wood Effect', 'Stone Effect', 'Concrete Effect',
            'Solid Color', 'Geometric Pattern', 'Floral Pattern', 'Textured',
            'Metallic Effect', 'Terracotta Effect', 'Subway Brick', 'Chevron',
            'Herringbone', 'Penny Round', 'Arabesque', 'Fish Scale',
            'Hexagonal', 'Diamond Pattern', 'Striped', 'Gradient',
            'Mirror Effect', 'Fabric Effect', 'Sand Effect', 'Rustic',
        ]
        for e in effects:
            TileEffect.objects.get_or_create(name=e, defaults={'slug': slugify(e)})

        finishes = [
            'Glossy', 'Polished', 'Matte', 'Satin', 'Textured', 'Rustic',
            'Anti-Slip R9', 'Anti-Slip R10', 'Anti-Slip R11', 'Anti-Slip R12',
            'Anti-Slip R13', 'Carved 3D', 'Lappato (Semi-Polished)', 'Natural',
            'Glazed', 'Unglazed', 'Salt Glaze', 'Crackle Glaze', 'Reactive Glaze',
        ]
        for f in finishes:
            TileFinish.objects.get_or_create(name=f, defaults={'slug': slugify(f)})

        sizes = [
            ('2"x2" (50x50mm)', 50, 50, 6),
            ('4"x4" (100x100mm)', 100, 100, 7),
            ('6"x6" (150x150mm)', 150, 150, 7),
            ('8"x8" (200x200mm)', 200, 200, 8),
            ('12"x12" (300x300mm)', 300, 300, 8),
            ('12"x24" (300x600mm)', 300, 600, 8),
            ('16"x16" (400x400mm)', 400, 400, 8),
            ('18"x18" (450x450mm)', 450, 450, 9),
            ('20"x20" (500x500mm)', 500, 500, 9),
            ('24"x24" (600x600mm)', 600, 600, 9),
            ('24"x48" (600x1200mm)', 600, 1200, 9),
            ('32"x32" (800x800mm)', 800, 800, 10),
            ('36"x36" (900x900mm)', 900, 900, 10),
            ('40"x40" (1000x1000mm)', 1000, 1000, 11),
            ('24"x48" Plank (600x1200mm)', 600, 1200, 9),
            ('32"x64" Plank (800x1600mm)', 800, 1600, 10),
            ('48"x48" (1200x1200mm)', 1200, 1200, 12),
            ('48"x96" Slab (1200x2400mm)', 1200, 2400, 12),
            ('63"x126" Slab (1600x3200mm)', 1600, 3200, 12),
            ('Mosaic Sheet (300x300mm)', 300, 300, 6),
            ('Subway 3"x6" (75x150mm)', 75, 150, 7),
            ('Subway 4"x8" (100x200mm)', 100, 200, 7),
            ('Subway 3"x12" (75x300mm)', 75, 300, 7),
        ]
        for label, w, h, t in sizes:
            TileSize.objects.get_or_create(
                size_label=label,
                defaults={'width_mm': w, 'height_mm': h, 'thickness_mm': t}
            )

    # ─────────── TILE PRODUCTS ───────────

    def _seed_tiles(self):
        self.stdout.write('  Seeding tile products...')

        tiles_data = [
            {'name': 'White Carrara Marble Effect Porcelain Floor Tile', 'cat': 'Porcelain Floor Tiles', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Matte'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 8, 'price_max': 35, 'features': ['High durability', 'Low water absorption', 'Scratch resistant', 'Stain resistant', 'Rectified edges'], 'apps': ['Living room', 'Bedroom', 'Kitchen', 'Commercial lobby']},
            {'name': 'Calacatta Gold Marble Porcelain Tile', 'cat': 'Marble Effect Tiles', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Glossy'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)', '48"x48" (1200x1200mm)', '48"x96" Slab (1200x2400mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 15, 'price_max': 65, 'features': ['Premium marble look', 'Gold veining', 'Large format available', 'Book-match capable'], 'apps': ['Luxury residential', 'Hotel lobby', 'High-end commercial']},
            {'name': 'Dark Emperador Marble Effect Porcelain', 'cat': 'Porcelain Floor Tiles', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Matte'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 10, 'price_max': 40, 'features': ['Deep brown tones', 'White veining', 'Elegant appearance', 'High traffic rated'], 'apps': ['Living room', 'Office', 'Restaurant']},
            {'name': 'Grey Statuario Marble Porcelain Tile', 'cat': 'Porcelain Floor Tiles', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Lappato (Semi-Polished)'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 9, 'price_max': 38, 'features': ['Grey base with white veins', 'Modern look', 'Easy maintenance'], 'apps': ['Modern living', 'Bathroom floor', 'Kitchen']},
            {'name': 'Italian Crema Marfil Porcelain', 'cat': 'Porcelain Floor Tiles', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Matte'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 8, 'price_max': 32, 'features': ['Warm cream tones', 'Subtle veining', 'Versatile design'], 'apps': ['Living room', 'Hallway', 'Commercial']},
            {'name': 'Natural Oak Wood Look Porcelain Plank', 'cat': 'Wood Look Tiles', 'effects': ['Wood Effect'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x48" (600x1200mm)', '32"x64" Plank (800x1600mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 7, 'price_max': 28, 'features': ['Realistic wood grain', 'Textured surface', 'Waterproof', 'No warping'], 'apps': ['Living room', 'Bedroom', 'Kitchen', 'Bathroom']},
            {'name': 'Dark Walnut Wood Effect Porcelain', 'cat': 'Wood Look Tiles', 'effects': ['Wood Effect'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x48" (600x1200mm)', '24"x48" Plank (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 8, 'price_max': 30, 'features': ['Rich dark brown', 'Deep grain detail', 'High durability'], 'apps': ['Bedroom', 'Study', 'Restaurant', 'Bar']},
            {'name': 'Grey Washed Wood Porcelain Plank', 'cat': 'Wood Look Tiles', 'effects': ['Wood Effect'], 'finishes': ['Matte'], 'sizes': ['24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 6, 'price_max': 22, 'features': ['Scandinavian style', 'Light grey tones', 'Modern aesthetic'], 'apps': ['Modern apartment', 'Retail store', 'Office']},
            {'name': 'Antique Teak Wood Look Tile', 'cat': 'Wood Look Tiles', 'effects': ['Wood Effect', 'Rustic Effect'], 'finishes': ['Textured', 'Rustic'], 'sizes': ['24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 7, 'price_max': 25, 'features': ['Weathered look', 'Warm brown tones', 'Rustic charm'], 'apps': ['Cafe', 'Resort', 'Rustic interior']},
            {'name': 'Herringbone Wood Look Porcelain', 'cat': 'Wood Look Tiles', 'effects': ['Wood Effect', 'Herringbone'], 'finishes': ['Matte', 'Textured'], 'sizes': ['Subway 3"x12" (75x300mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 10, 'price_max': 35, 'features': ['Pre-cut herringbone pattern', 'Easy installation', 'Premium look'], 'apps': ['Feature floor', 'Kitchen', 'Hallway']},
            {'name': 'Plain White Ceramic Floor Tile', 'cat': 'Ceramic Floor Tiles', 'effects': ['Solid Color'], 'finishes': ['Glossy', 'Matte'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)', '24"x24" (600x600mm)'], 'material': 'Ceramic', 'water': '<3%', 'price_min': 2, 'price_max': 8, 'features': ['Budget friendly', 'Easy to clean', 'Multiple sizes', 'Wide availability'], 'apps': ['Bathroom', 'Kitchen', 'Utility room']},
            {'name': 'Grey Ceramic Floor Tile', 'cat': 'Ceramic Floor Tiles', 'effects': ['Solid Color'], 'finishes': ['Matte', 'Glossy'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)', '24"x24" (600x600mm)'], 'material': 'Ceramic', 'water': '<3%', 'price_min': 2, 'price_max': 9, 'features': ['Modern grey tones', 'Affordable', 'Low maintenance'], 'apps': ['Bathroom', 'Kitchen', 'Balcony']},
            {'name': 'Beige Ceramic Floor Tile', 'cat': 'Ceramic Floor Tiles', 'effects': ['Solid Color'], 'finishes': ['Matte', 'Glossy'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Ceramic', 'water': '<3%', 'price_min': 1.5, 'price_max': 7, 'features': ['Warm neutral tone', 'Economical', 'Easy installation'], 'apps': ['Budget bathroom', 'Kitchen', 'Laundry']},
            {'name': 'Double Charged Vitrified Tile - Ivory', 'cat': 'Vitrified Floor Tiles', 'effects': ['Solid Color', 'Marble Effect'], 'finishes': ['Polished', 'Glossy'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 4, 'price_max': 18, 'features': ['Double-layer pressing', 'Extreme hardness', 'Scratch proof', 'Stain proof', 'Ideal for commercial'], 'apps': ['Shopping mall', 'Office', 'Airport', 'Hospital']},
            {'name': 'Double Charged Vitrified Tile - Grey', 'cat': 'Vitrified Floor Tiles', 'effects': ['Solid Color', 'Marble Effect'], 'finishes': ['Polished', 'Matte'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 4, 'price_max': 18, 'features': ['Modern grey', 'Heavy duty', 'Polished finish', 'Commercial grade'], 'apps': ['Corporate office', 'Showroom', 'Retail']},
            {'name': 'Full Body Vitrified Tile - Terra', 'cat': 'Vitrified Floor Tiles', 'effects': ['Solid Color', 'Terracotta Effect'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x24" (600x600mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 5, 'price_max': 20, 'features': ['Color through body', 'No chipping visibility', 'Heavy traffic', 'Industrial grade'], 'apps': ['Factory', 'Warehouse', 'Parking', 'Outdoor']},
            {'name': 'Soluble Salt Vitrified Tile', 'cat': 'Vitrified Floor Tiles', 'effects': ['Solid Color'], 'finishes': ['Matte'], 'sizes': ['24"x24" (600x600mm)'], 'material': 'Vitrified', 'water': '<0.1%', 'price_min': 3, 'price_max': 12, 'features': ['Economical vitrified', 'Basic colors', 'Good for budget projects'], 'apps': ['Budget residential', 'Utility areas']},
            {'name': 'Glazed Vitrified Tile - Nano Polish', 'cat': 'Vitrified Floor Tiles', 'effects': ['Marble Effect', 'Solid Color'], 'finishes': ['Polished', 'Glossy'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 5, 'price_max': 22, 'features': ['Nano coating', 'Stain resistance', 'High gloss', 'Digital print layer'], 'apps': ['Luxury home', 'Hotel', 'Showroom']},
            {'name': 'White Glossy Ceramic Wall Tile', 'cat': 'Ceramic Wall Tiles', 'effects': ['Solid Color'], 'finishes': ['Glossy'], 'sizes': ['8"x8" (200x200mm)', '8"x12" (200x300mm)', '10"x16" (250x400mm)', '12"x24" (300x600mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 1, 'price_max': 5, 'features': ['Classic white', 'Easy clean', 'Reflective', 'Budget friendly'], 'apps': ['Bathroom wall', 'Kitchen backsplash', 'Laundry']},
            {'name': 'Grey Matte Ceramic Wall Tile', 'cat': 'Ceramic Wall Tiles', 'effects': ['Solid Color'], 'finishes': ['Matte'], 'sizes': ['10"x16" (250x400mm)', '12"x24" (300x600mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 1.5, 'price_max': 6, 'features': ['Modern grey', 'Anti-glare', 'Contemporary look'], 'apps': ['Bathroom', 'Kitchen', 'Feature wall']},
            {'name': 'Beige Textured Wall Tile', 'cat': 'Ceramic Wall Tiles', 'effects': ['Textured', 'Solid Color'], 'finishes': ['Textured'], 'sizes': ['12"x24" (300x600mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 2, 'price_max': 8, 'features': ['3D texture', 'Warm neutral', 'Depth and dimension'], 'apps': ['Feature wall', 'Bathroom', 'Living room accent']},
            {'name': 'Blue Patterned Ceramic Wall Tile', 'cat': 'Ceramic Wall Tiles', 'effects': ['Geometric Pattern', 'Floral Pattern'], 'finishes': ['Glossy'], 'sizes': ['8"x8" (200x200mm)', '6"x6" (150x150mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 3, 'price_max': 12, 'features': ['Decorative pattern', 'Mediterranean style', 'Hand-painted look'], 'apps': ['Kitchen backsplash', 'Bathroom accent', 'Shower niche']},
            {'name': 'Large Format Porcelain Wall Slab', 'cat': 'Porcelain Wall Tiles', 'effects': ['Marble Effect', 'Solid Color'], 'finishes': ['Polished', 'Matte', 'Textured'], 'sizes': ['48"x96" Slab (1200x2400mm)', '48"x48" (1200x1200mm)', '63"x126" Slab (1600x3200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 40, 'price_max': 120, 'features': ['Minimal grout lines', 'Seamless look', 'Book-match patterns', 'Ventilated facade capable'], 'apps': ['Luxury bathroom', 'Living room wall', 'Hotel lobby', 'Exterior cladding']},
            {'name': 'Wood Look Porcelain Wall Tile', 'cat': 'Porcelain Wall Tiles', 'effects': ['Wood Effect'], 'finishes': ['Matte', 'Textured'], 'sizes': ['8"x48" (200x1200mm)', '12"x48" (300x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 8, 'price_max': 25, 'features': ['Warm wood aesthetic', 'Waterproof', 'Easy maintenance'], 'apps': ['Bathroom wall', 'Bedroom accent', 'Kitchen wall']},
            {'name': 'Classic White Subway Tile', 'cat': 'Subway Tiles', 'effects': ['Subway Brick'], 'finishes': ['Glossy'], 'sizes': ['Subway 3"x6" (75x150mm)', 'Subway 4"x8" (100x200mm)', 'Subway 3"x12" (75x300mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 1.5, 'price_max': 8, 'features': ['Timeless design', 'Brick bond pattern', 'Easy to install', 'Classic metro look'], 'apps': ['Kitchen backsplash', 'Bathroom wall', 'Commercial kitchen']},
            {'name': 'Black Subway Tile', 'cat': 'Subway Tiles', 'effects': ['Subway Brick'], 'finishes': ['Glossy', 'Matte'], 'sizes': ['Subway 3"x6" (75x150mm)', 'Subway 4"x8" (100x200mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 2, 'price_max': 10, 'features': ['Bold contrast', 'Modern drama', 'Industrial chic'], 'apps': ['Kitchen backsplash', 'Feature wall', 'Bar area']},
            {'name': 'Colored Subway Tile - Sage Green', 'cat': 'Subway Tiles', 'effects': ['Subway Brick'], 'finishes': ['Glossy', 'Matte'], 'sizes': ['Subway 3"x6" (75x150mm)', 'Subway 4"x8" (100x200mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 2, 'price_max': 9, 'features': ['Trendy color', 'Soft green tone', 'Versatile pattern'], 'apps': ['Kitchen backsplash', 'Bathroom', 'Laundry room']},
            {'name': 'Beveled Subway Tile - White', 'cat': 'Subway Tiles', 'effects': ['Subway Brick'], 'finishes': ['Glossy'], 'sizes': ['Subway 3"x6" (75x150mm)', 'Subway 4"x8" (100x200mm)'], 'material': 'Ceramic', 'water': '<10%', 'price_min': 3, 'price_max': 12, 'features': ['Beveled edge detail', 'Light reflection', 'Classic elegance'], 'apps': ['Bathroom', 'Kitchen', 'Restaurant wall']},
            {'name': 'Glass Mosaic Sheet - Mixed Colors', 'cat': 'Mosaic Tiles', 'effects': ['Geometric Pattern', 'Gradient'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Glass', 'water': '<0.5%', 'price_min': 5, 'price_max': 25, 'features': ['Vibrant colors', 'Mesh-mounted', 'Easy to cut', 'Waterproof'], 'apps': ['Swimming pool', 'Shower floor', 'Kitchen backsplash', 'Feature strip']},
            {'name': 'Marble Mosaic Sheet - Carrara', 'cat': 'Mosaic Tiles', 'effects': ['Marble Effect', 'Geometric Pattern'], 'finishes': ['Polished', 'Matte'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Natural Marble', 'water': '<0.5%', 'price_min': 10, 'price_max': 45, 'features': ['Real marble chips', 'Luxury look', 'Mesh-backed', 'Classic pattern'], 'apps': ['Luxury bathroom', 'Kitchen backsplash', 'Shower niche']},
            {'name': 'Penny Round Mosaic - White', 'cat': 'Mosaic Tiles', 'effects': ['Penny Round'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Ceramic', 'water': '<5%', 'price_min': 4, 'price_max': 18, 'features': ['Retro circular design', 'Playful pattern', 'Easy installation'], 'apps': ['Bathroom floor', 'Shower floor', 'Backsplash accent']},
            {'name': 'Hexagonal Mosaic - Black & White', 'cat': 'Mosaic Tiles', 'effects': ['Hexagonal', 'Geometric Pattern'], 'finishes': ['Matte', 'Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Ceramic', 'water': '<5%', 'price_min': 5, 'price_max': 22, 'features': ['Geometric hex pattern', 'Bold contrast', 'Victorian style'], 'apps': ['Bathroom floor', 'Kitchen floor', 'Entryway']},
            {'name': 'Metallic Mosaic Sheet - Gold & Silver', 'cat': 'Mosaic Tiles', 'effects': ['Metallic Effect', 'Geometric Pattern'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Glass/Metal', 'water': '<0.5%', 'price_min': 8, 'price_max': 35, 'features': ['Luxury metallic finish', 'Reflective surfaces', 'Premium accent'], 'apps': ['Feature wall', 'Kitchen backsplash', 'Bar area', 'Spa']},
            {'name': 'Italian Carrara Marble Tile', 'cat': 'Natural Stone Tiles', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Natural'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)', '24"x24" (600x600mm)', '24"x48" (600x1200mm)'], 'material': 'Natural Marble', 'water': '<0.5%', 'price_min': 30, 'price_max': 120, 'features': ['Genuine marble', 'Unique veining', 'Luxury material', 'Requires sealing'], 'apps': ['Luxury bathroom', 'Living room', 'Countertop', 'Feature wall']},
            {'name': 'Indian Granite Floor Tile - Black Galaxy', 'cat': 'Natural Stone Tiles', 'effects': ['Solid Color'], 'finishes': ['Polished'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)', '24"x24" (600x600mm)'], 'material': 'Natural Granite', 'water': '<0.2%', 'price_min': 15, 'price_max': 55, 'features': ['Extremely hard', 'Gold speckles', 'Polished or flamed', 'Very durable'], 'apps': ['Commercial floor', 'Kitchen floor', 'Outdoor', 'Staircase']},
            {'name': 'Travertine Tile - Ivory', 'cat': 'Natural Stone Tiles', 'effects': ['Stone Effect', 'Textured'], 'finishes': ['Matte'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)', '24"x24" (600x600mm)'], 'material': 'Natural Travertine', 'water': '<1%', 'price_min': 20, 'price_max': 70, 'features': ['Natural pits and holes', 'Warm earth tones', 'Classic Roman look', 'Requires sealing'], 'apps': ['Patio', 'Pool surround', 'Bathroom', 'Living room']},
            {'name': 'Slate Tile - Multi Color', 'cat': 'Natural Stone Tiles', 'effects': ['Stone Effect', 'Textured'], 'finishes': ['Natural'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Natural Slate', 'water': '<0.5%', 'price_min': 12, 'price_max': 45, 'features': ['Layered natural look', 'Cleft surface', 'Earthy tones', 'Slip resistant'], 'apps': ['Outdoor patio', 'Entryway', 'Bathroom', 'Kitchen floor']},
            {'name': 'Sandstone Tile - Raj Green', 'cat': 'Natural Stone Tiles', 'effects': ['Stone Effect', 'Textured'], 'finishes': ['Natural'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Natural Sandstone', 'water': '<2%', 'price_min': 8, 'price_max': 35, 'features': ['Warm green-grey tones', 'Natural riven surface', 'Affordable stone', 'Good outdoor performance'], 'apps': ['Garden path', 'Patio', 'Wall cladding', 'Landscaping']},
            {'name': 'Super White Marble Look Porcelain Slab', 'cat': 'Large Format Slabs', 'effects': ['Marble Effect'], 'finishes': ['Polished', 'Matte'], 'sizes': ['48"x96" Slab (1200x2400mm)', '48"x48" (1200x1200mm)', '63"x126" Slab (1600x3200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 45, 'price_max': 150, 'features': ['Dramatic grey veining on white', 'Book-match capable', '6mm or 12mm thickness', 'Countertop capable'], 'apps': ['Kitchen countertop', 'Island', 'Shower wall', 'Feature wall']},
            {'name': 'Dark Concrete Look Porcelain Slab', 'cat': 'Large Format Slabs', 'effects': ['Concrete Effect'], 'finishes': ['Matte', 'Textured'], 'sizes': ['48"x96" Slab (1200x2400mm)', '63"x126" Slab (1600x3200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 35, 'price_max': 100, 'features': ['Industrial concrete aesthetic', 'Minimal joints', 'Furniture compatible', 'Interior & exterior'], 'apps': ['Kitchen countertop', 'Living room wall', 'Furniture', 'Exterior cladding']},
            {'name': 'Noir Black Porcelain Slab', 'cat': 'Large Format Slabs', 'effects': ['Solid Color'], 'finishes': ['Polished', 'Matte'], 'sizes': ['48"x96" Slab (1200x2400mm)', '63"x126" Slab (1600x3200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 40, 'price_max': 110, 'features': ['Deep solid black', 'Sophisticated look', 'Easy maintenance', 'Premium feel'], 'apps': ['Luxury kitchen', 'Bathroom wall', 'Fireplace surround', 'Bar top']},
            {'name': 'Anti-Slip Exterior Porcelain Tile - Stone Grey', 'cat': 'Outdoor / Exterior Tiles', 'effects': ['Stone Effect'], 'finishes': ['Anti-Slip R11', 'Textured'], 'sizes': ['24"x24" (600x600mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 8, 'price_max': 30, 'features': ['Frost resistant', 'R11 anti-slip', 'UV stable', '20mm thickness option'], 'apps': ['Garden patio', 'Balcony', 'Terrace', 'Pool deck']},
            {'name': 'Wood Look Outdoor Porcelain Plank', 'cat': 'Outdoor / Exterior Tiles', 'effects': ['Wood Effect'], 'finishes': ['Anti-Slip R11', 'Textured'], 'sizes': ['24"x48" Plank (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 10, 'price_max': 35, 'features': ['Wood look for outdoors', 'No rotting', 'Frost proof', 'Raised pedestal install'], 'apps': ['Deck', 'Balcony', 'Garden path', 'Rooftop terrace']},
            {'name': 'Cotto Look Exterior Tile', 'cat': 'Outdoor / Exterior Tiles', 'effects': ['Terracotta Effect', 'Rustic Effect'], 'finishes': ['Anti-Slip R12', 'Textured', 'Rustic'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 6, 'price_max': 22, 'features': ['Mediterranean warmth', 'Slip resistant', 'Frost proof', 'Colorfast'], 'apps': ['Courtyard', 'Garden', 'Pathway', 'Terrace']},
            {'name': 'Pool Mosaic Tile - Ocean Blue', 'cat': 'Swimming Pool Tiles', 'effects': ['Solid Color', 'Geometric Pattern'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Glass', 'water': '<0.1%', 'price_min': 6, 'price_max': 28, 'features': ['Chemical resistant', 'UV stable', 'Zero water absorption', 'Easy to clean', 'Smooth surface'], 'apps': ['Swimming pool interior', 'Pool waterline', 'Spa', 'Jacuzzi']},
            {'name': 'Pool Tile - Crystalline White', 'cat': 'Swimming Pool Tiles', 'effects': ['Solid Color'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Glass', 'water': '<0.1%', 'price_min': 5, 'price_max': 22, 'features': ['Pure white crystal look', 'Reflective', 'Pool grade adhesive required', 'Chemical resistant'], 'apps': ['Pool interior', 'Waterline', 'Fountain']},
            {'name': 'Anti-Slip Pool Deck Tile - Sand', 'cat': 'Swimming Pool Tiles', 'effects': ['Solid Color', 'Stone Effect'], 'finishes': ['Anti-Slip R12', 'Textured'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 7, 'price_max': 25, 'features': ['Barefoot friendly', 'Heat resistant', 'Slip resistant', 'Pool chemicals resistant'], 'apps': ['Pool surround', 'Wet deck', 'Shower area']},
            {'name': 'Heavy Duty Parking Tile - Dark Grey', 'cat': 'Parking / Heavy Duty Tiles', 'effects': ['Solid Color'], 'finishes': ['Matte', 'Textured'], 'sizes': ['16"x16" (400x400mm)', '24"x24" (600x600mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 3, 'price_max': 12, 'features': ['40+ ton load bearing', 'Abrasion resistant', 'Oil & chemical resistant', 'Low maintenance', 'Cost effective'], 'apps': ['Parking garage', 'Driveway', 'Warehouse', 'Industrial floor', 'Loading dock']},
            {'name': 'Industrial Floor Tile - Red', 'cat': 'Parking / Heavy Duty Tiles', 'effects': ['Solid Color'], 'finishes': ['Matte', 'Anti-Slip R10'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Vitrified', 'water': '<0.1%', 'price_min': 2.5, 'price_max': 10, 'features': ['High compressive strength', 'Chemical resistant', 'Anti-slip', 'Easy replacement'], 'apps': ['Factory floor', 'Workshop', 'Garage', 'Loading area']},
            {'name': 'Chevron Pattern Parking Tile', 'cat': 'Parking / Heavy Duty Tiles', 'effects': ['Chevron', 'Geometric Pattern'], 'finishes': ['Matte', 'Textured'], 'sizes': ['16"x16" (400x400mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 4, 'price_max': 14, 'features': ['Directional chevron pattern', 'Traffic flow guidance', 'Heavy duty', 'Visual interest'], 'apps': ['Parking lot', 'Ramp', 'Driveway']},
            {'name': 'Anti-Slip Bathroom Floor Tile - White', 'cat': 'Anti-Slip Tiles', 'effects': ['Solid Color'], 'finishes': ['Anti-Slip R10', 'Textured'], 'sizes': ['12"x12" (300x300mm)', '16"x16" (400x400mm)'], 'material': 'Porcelain', 'water': '<0.1%', 'price_min': 4, 'price_max': 15, 'features': ['Wet area safe', 'R10 slip rating', 'Easy clean textured surface', 'Hygienic'], 'apps': ['Bathroom floor', 'Shower floor', 'Wet room', 'Sauna']},
            {'name': 'Anti-Slip Commercial Floor Tile - Charcoal', 'cat': 'Anti-Slip Tiles', 'effects': ['Solid Color', 'Carved 3D'], 'finishes': ['Anti-Slip R12', 'Textured'], 'sizes': ['16"x16" (400x400mm)', '24"x24" (600x600mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 6, 'price_max': 22, 'features': ['Maximum slip resistance', 'Commercial grade', 'Heavy traffic', 'ADA compliant'], 'apps': ['Commercial kitchen', 'Hospital corridor', 'Public restroom', 'Ramp']},
            {'name': 'Arabesque Kitchen Backsplash Tile - White', 'cat': 'Kitchen Backsplash Tiles', 'effects': ['Arabesque', 'Geometric Pattern'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Ceramic', 'water': '<8%', 'price_min': 4, 'price_max': 18, 'features': ['Elegant curved shape', 'Instant style upgrade', 'Mesh-mounted', 'Grout lines create pattern'], 'apps': ['Kitchen backsplash', 'Bathroom accent', 'Range hood wall']},
            {'name': 'Fish Scale Tile - Teal', 'cat': 'Kitchen Backsplash Tiles', 'effects': ['Fish Scale', 'Geometric Pattern'], 'finishes': ['Glossy', 'Matte'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Ceramic', 'water': '<8%', 'price_min': 5, 'price_max': 20, 'features': ['Trendy scallop shape', 'Rich teal color', 'Instagram-worthy', 'Easy installation'], 'apps': ['Kitchen backsplash', 'Bathroom wall', 'Bar area']},
            {'name': 'Brick Joint Subway Backsplash - Cream', 'cat': 'Kitchen Backsplash Tiles', 'effects': ['Subway Brick'], 'finishes': ['Matte', 'Textured'], 'sizes': ['Subway 3"x12" (75x300mm)'], 'material': 'Ceramic', 'water': '<8%', 'price_min': 2, 'price_max': 10, 'features': ['Elongated subway format', 'Modern brick look', 'Warm cream color', 'Grout joint emphasis'], 'apps': ['Kitchen backsplash', 'Bathroom', 'Feature wall']},
            {'name': 'Bathroom Wall & Floor Set - Italian Grey', 'cat': 'Bathroom Tiles', 'effects': ['Marble Effect', 'Solid Color'], 'finishes': ['Polished', 'Matte', 'Anti-Slip R10'], 'sizes': ['12"x24" (300x600mm)', '24"x24" (600x600mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 8, 'price_max': 30, 'features': ['Coordinated wall & floor', 'Marble effect wall', 'Anti-slip floor option', 'Complete bathroom solution'], 'apps': ['Master bathroom', 'Guest bathroom', 'En-suite']},
            {'name': 'Small Format Bathroom Tile Set - Navy', 'cat': 'Bathroom Tiles', 'effects': ['Solid Color', 'Geometric Pattern'], 'finishes': ['Glossy', 'Matte'], 'sizes': ['4"x4" (100x100mm)', '8"x8" (200x200mm)', 'Subway 3"x12" (75x300mm)'], 'material': 'Ceramic', 'water': '<5%', 'price_min': 3, 'price_max': 15, 'features': ['Multiple sizes to mix', 'Navy blue palette', 'Pattern mixing friendly', 'Classic bathroom feel'], 'apps': ['Bathroom wall', 'Bathroom floor', 'Shower enclosure']},
            {'name': 'Commercial Porcelain Tile - Light Grey', 'cat': 'Commercial Tiles', 'effects': ['Solid Color', 'Concrete Effect'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 5, 'price_max': 20, 'features': ['High PEI rating', 'Heavy traffic', 'Low maintenance', 'Large format reduces grout', 'Cost effective'], 'apps': ['Office floor', 'Retail store', 'Hospital', 'School', 'Airport']},
            {'name': 'Polished Commercial Tile - White', 'cat': 'Commercial Tiles', 'effects': ['Solid Color'], 'finishes': ['Polished'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)'], 'material': 'Vitrified', 'water': '<0.05%', 'price_min': 5, 'price_max': 18, 'features': ['High reflectivity', 'Clean bright look', 'Stain resistant', 'Easy maintenance', 'Professional appearance'], 'apps': ['Corporate lobby', 'Showroom', 'Hotel', 'Mall']},
            {'name': 'Handmade Terracotta Floor Tile', 'cat': 'Terracotta / Rustic Tiles', 'effects': ['Terracotta Effect', 'Rustic Effect'], 'finishes': ['Rustic', 'Matte', 'Textured'], 'sizes': ['8"x8" (200x200mm)', '12"x12" (300x300mm)'], 'material': 'Natural Clay', 'water': '<8%', 'price_min': 5, 'price_max': 25, 'features': ['Handmade charm', 'Warm red-brown tones', 'Natural variation', 'Requires sealing', 'Authentic rustic look'], 'apps': ['Rustic kitchen', 'Mediterranean home', 'Patio', 'Conservatory']},
            {'name': 'Mexican Saltillo Tile', 'cat': 'Terracotta / Rustic Tiles', 'effects': ['Terracotta Effect', 'Rustic Effect'], 'finishes': ['Rustic', 'Matte'], 'sizes': ['12"x12" (300x300mm)'], 'material': 'Natural Clay', 'water': '<10%', 'price_min': 6, 'price_max': 28, 'features': ['Traditional Mexican style', 'Rust/amber/red colors', 'Hand-pressed', 'Sealed finish available', 'Southwestern aesthetic'], 'apps': ['Kitchen', 'Hallway', 'Patio', 'Southwestern interior']},
            {'name': '3D Wave Textured Wall Tile - White', 'cat': '3D / Textured Wall Tiles', 'effects': ['Textured', 'Carved 3D'], 'finishes': ['Matte'], 'sizes': ['12"x24" (300x600mm)'], 'material': 'Ceramic', 'water': '<5%', 'price_min': 6, 'price_max': 25, 'features': ['Sculptural wave pattern', 'Light & shadow play', 'Modern focal point', 'Easy to clean'], 'apps': ['Feature wall', 'Bathroom accent', 'Living room', 'Headboard wall']},
            {'name': '3D Brick Texture Wall Tile - Grey', 'cat': '3D / Textured Wall Tiles', 'effects': ['Textured', 'Carved 3D', 'Subway Brick'], 'finishes': ['Matte'], 'sizes': ['12"x24" (300x600mm)'], 'material': 'Ceramic', 'water': '<5%', 'price_min': 5, 'price_max': 22, 'features': ['Realistic brick texture', 'Industrial loft feel', 'No mortar needed', 'Lightweight'], 'apps': ['Accent wall', 'Kitchen backsplash', 'Bar wall', 'Loft interior']},
            {'name': 'Metallic Silver Porcelain Tile', 'cat': 'Metallic Effect Tiles', 'effects': ['Metallic Effect', 'Solid Color'], 'finishes': ['Polished', 'Matte'], 'sizes': ['24"x24" (600x600mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 12, 'price_max': 40, 'features': ['Brushed metal look', 'Reflective surface', 'Industrial luxury', 'Scratch resistant'], 'apps': ['Feature wall', 'Kitchen backsplash', 'Bar area', 'Commercial accent']},
            {'name': 'Copper Effect Porcelain Tile', 'cat': 'Metallic Effect Tiles', 'effects': ['Metallic Effect', 'Solid Color'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x24" (600x600mm)', '12"x24" (300x600mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 12, 'price_max': 38, 'features': ['Warm copper tones', 'No oxidation', 'Easy maintenance', 'Unique accent'], 'apps': ['Kitchen backsplash', 'Feature wall', 'Bathroom accent', 'Restaurant interior']},
            {'name': 'Geometric Encaustic Look Tile - Blue & White', 'cat': 'Geometric Pattern Tiles', 'effects': ['Geometric Pattern'], 'finishes': ['Matte'], 'sizes': ['8"x8" (200x200mm)', '10"x10" (250x250mm)'], 'material': 'Porcelain', 'water': '<0.5%', 'price_min': 5, 'price_max': 22, 'features': ['Encaustic pattern', 'Victorian inspired', 'No fading', 'Durable porcelain body'], 'apps': ['Kitchen floor', 'Bathroom floor', 'Hallway', 'Porch']},
            {'name': 'Moroccan Star Pattern Tile', 'cat': 'Geometric Pattern Tiles', 'effects': ['Geometric Pattern', 'Floral Pattern'], 'finishes': ['Matte', 'Glossy'], 'sizes': ['8"x8" (200x200mm)', '6"x6" (150x150mm)'], 'material': 'Ceramic', 'water': '<5%', 'price_min': 4, 'price_max': 18, 'features': ['Exotic Moroccan design', 'Bold geometric star', 'Colorful options', 'Cultural charm'], 'apps': ['Backsplash', 'Bathroom floor', 'Feature area', 'Riad style']},
            {'name': 'Light Grey Concrete Effect Porcelain', 'cat': 'Concrete Effect Tiles', 'effects': ['Concrete Effect', 'Solid Color'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x24" (600x600mm)', '32"x32" (800x800mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 6, 'price_max': 25, 'features': ['Industrial concrete look', 'No sealing needed', 'Consistent color', 'Warm grey tones'], 'apps': ['Industrial loft', 'Modern living', 'Retail floor', 'Office']},
            {'name': 'Dark Concrete Effect Porcelain', 'cat': 'Concrete Effect Tiles', 'effects': ['Concrete Effect', 'Solid Color'], 'finishes': ['Matte', 'Textured'], 'sizes': ['24"x24" (600x600mm)', '24"x48" (600x1200mm)'], 'material': 'Porcelain', 'water': '<0.05%', 'price_min': 7, 'price_max': 28, 'features': ['Dark industrial aesthetic', 'Urban feel', 'Low maintenance', 'Modern minimalist'], 'apps': ['Modern kitchen', 'Living room', 'Commercial space', 'Bar']},
            {'name': 'Clear Glass Brick Tile', 'cat': 'Glass Tiles', 'effects': ['Solid Color'], 'finishes': ['Glossy'], 'sizes': ['8"x8" (200x200mm)', '12"x12" (300x300mm)'], 'material': 'Glass', 'water': '0%', 'price_min': 5, 'price_max': 20, 'features': ['Transparent/translucent', 'Light transmitting', 'Easy to clean', 'Modern look'], 'apps': ['Shower wall', 'Partition', 'Backsplash', 'Feature wall']},
            {'name': 'Iridescent Glass Tile Sheet', 'cat': 'Glass Tiles', 'effects': ['Metallic Effect', 'Gradient'], 'finishes': ['Glossy'], 'sizes': ['Mosaic Sheet (300x300mm)'], 'material': 'Glass', 'water': '0%', 'price_min': 8, 'price_max': 30, 'features': ['Color-shifting iridescence', 'Rainbow reflections', 'Luxury accent', 'Mesh-mounted'], 'apps': ['Spa wall', 'Feature strip', 'Kitchen backsplash', 'Bathroom accent']},
        ]

        cat_map = {c.name: c for c in TileCategory.objects.all()}
        eff_map = {e.name: e for e in TileEffect.objects.all()}
        fin_map = {f.name: f for f in TileFinish.objects.all()}
        size_map = {s.size_label: s for s in TileSize.objects.all()}

        for td in tiles_data:
            cat = cat_map.get(td['cat'])
            if not cat:
                continue
            product, created = TileProduct.objects.update_or_create(
                name=td['name'],
                defaults={
                    'slug': slugify(td['name']),
                    'category': cat,
                    'description': f"{td['material']} {td['cat'].lower()} with {', '.join(td['effects'][:2])} design.",
                    'material': td['material'],
                    'water_absorption': td.get('water', ''),
                    'price_range_min': td['price_min'],
                    'price_range_max': td['price_max'],
                    'features': td['features'],
                    'applications': td['apps'],
                    'is_featured': td['price_max'] > 50,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'    Created: {td["name"][:60]}'))
            for ename in td.get('effects', []):
                e = eff_map.get(ename)
                if e:
                    product.effects.add(e)
            for fname in td.get('finishes', []):
                f = fin_map.get(fname)
                if f:
                    product.finishes.add(f)
            for slabel in td.get('sizes', []):
                s = size_map.get(slabel)
                if s:
                    product.sizes.add(s)

    # ─────────── LOCATIONS ───────────

    def _seed_locations(self):
        self.stdout.write('  Seeding locations for 10 countries...')

        LOCATIONS = {
            'China': {
                'flag_emoji': '🇨🇳', 'continent': 'Asia', 'ranking': 1,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': "The world's largest producer and consumer of ceramic tiles, with over 3,000 manufacturers.",
                'market_overview': 'China dominates global tile production with 8.5 billion sqm annually. Major clusters in Foshan, Jinjiang, Zibo, and Jingdezhen.',
                'key_stats': {'production_billion_sqm': 8.5, 'consumption_billion_sqm': 7.2, 'export_share': '12%', 'market_growth': '3.5%', 'manufacturers': '3000+', 'export_value': '$6.8B'},
                'insights': [{'title': 'Foshan: Global Tile Capital', 'content': 'Foshan houses 500+ large manufacturers and hosts Ceramics China exhibition.', 'year': 2024}],
                'states': [
                    {'name': 'Guangdong', 'type': 'Province', 'hub': True, 'desc': "China's largest tile-producing province",
                     'cities': [
                         {'name': 'Foshan', 'type': 'City', 'hub': True, 'villages': ['Nanhai District', 'Shunde District', 'Chancheng District', 'Sanshui District', 'Gaoming District', 'Shiwan Town', 'Nanzhuang Town', 'Xiqiao Town', 'Leping Town', 'Dali Town']},
                         {'name': 'Guangzhou', 'type': 'City', 'hub': False, 'villages': ['Tianhe District', 'Yuexiu District', 'Haizhu District', 'Panyu District', 'Baiyun District', 'Foshan-border area']},
                         {'name': 'Shenzhen', 'type': 'City', 'hub': False, 'villages': ['Nanshan District', 'Futian District', 'Luohu District', 'Baoan District', 'Longgang District', 'Longhua District']},
                         {'name': 'Dongguan', 'type': 'City', 'hub': False, 'villages': ['Humen Town', 'Changan Town', 'Dalingshan Town', 'Chashan Town']},
                         {'name': 'Zhaoqing', 'type': 'City', 'hub': False, 'villages': ['Duanzhou District', 'Gaoyao District', 'Sihui City', 'Deqing County']},
                     ]},
                    {'name': 'Fujian', 'type': 'Province', 'hub': True, 'desc': 'Second major tile province, Jinjiang is a key center',
                     'cities': [
                         {'name': 'Jinjiang', 'type': 'City', 'hub': True, 'villages': ['Cizao Town', 'Yinglin Town', 'Anhai Town', 'Longhu Town', 'Shenhu Town', 'Neikeng Town']},
                         {'name': 'Quanzhou', 'type': 'City', 'hub': False, 'villages': ['Fengze District', 'Licheng District', 'Jinjiang-suburb', 'Nanan City', 'Hui\'an County']},
                         {'name': 'Xiamen', 'type': 'City', 'hub': False, 'villages': ['Siming District', 'Huli District', 'Haicang District', 'Jimei District', 'Tongan District', 'Xiang\'an District']},
                     ]},
                    {'name': 'Shandong', 'type': 'Province', 'hub': True, 'desc': 'Major northern tile production base',
                     'cities': [
                         {'name': 'Zibo', 'type': 'City', 'hub': True, 'villages': ['Zichuan District', 'Zhoucun District', 'Boshan District', 'Linzi District', 'Zhangdian District', 'Huantai County']},
                         {'name': 'Qingdao', 'type': 'City', 'hub': False, 'villages': ['Shinan District', 'Shibei District', 'Chengyang District', 'Huangdao District', 'Jimo District', 'Jiaozhou City']},
                         {'name': 'Jinan', 'type': 'City', 'hub': False, 'villages': ['Lixia District', 'Shizhong District', 'Huaiyin District', 'Tianqiao District', 'Licheng District', 'Changqing District']},
                     ]},
                    {'name': 'Jiangxi', 'type': 'Province', 'hub': True, 'desc': 'Historic ceramic center, Jingdezhen is the Porcelain Capital',
                     'cities': [
                         {'name': 'Jingdezhen', 'type': 'City', 'hub': True, 'villages': ['Zhushan District', 'Changjiang District', 'Fuliang County', 'Leping City', 'Ceramic Industrial Park', 'Kaiping Village', 'Sanbao Village']},
                         {'name': 'Nanchang', 'type': 'City', 'hub': False, 'villages': ['Donghu District', 'Xihu District', 'Qingyunpu District', 'Qingshanhu District', 'Xinjian District']},
                     ]},
                    {'name': 'Sichuan', 'type': 'Province', 'hub': False, 'desc': 'Growing western tile production hub',
                     'cities': [
                         {'name': 'Chengdu', 'type': 'City', 'hub': False, 'villages': ['Jinjiang District', 'Qingyang District', 'Jinniu District', 'Wuhou District', 'Chenghua District', 'Pidu District', 'Xindu District', 'Wenjiang District', 'Shuangliu District']},
                         {'name': 'Deyang', 'type': 'City', 'hub': False, 'villages': ['Jingyang District', 'Guanghan City', 'Shifang City', 'Mianzhu City', 'Luojiang District']},
                     ]},
                    {'name': 'Zhejiang', 'type': 'Province', 'hub': False, 'desc': 'Eastern province with growing tile output',
                     'cities': [
                         {'name': 'Hangzhou', 'type': 'City', 'hub': False, 'villages': ['Shangcheng District', 'Xiacheng District', 'Gongshu District', 'Jianggan District', 'Binjiang District', 'Yuhang District', 'Xiaoshan District', 'Fuyang District']},
                         {'name': 'Wenzhou', 'type': 'City', 'hub': False, 'villages': ['Lucheng District', 'Longwan District', 'Ouhai District', 'Ruian City', 'Yueqing City']},
                     ]},
                ],
            },
            'India': {
                'flag_emoji': '🇮🇳', 'continent': 'Asia', 'ranking': 2,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': 'Second-largest tile producer globally and one of the fastest-growing markets.',
                'market_overview': 'India produces 3.4 billion sqm annually. Morbi (Gujarat) produces 70%+ of tiles with 600+ units. Kishangarh (Rajasthan) is the marble/tile hub of North India.',
                'key_stats': {'production_billion_sqm': 3.4, 'consumption_billion_sqm': 2.8, 'export_share': '15%', 'market_growth': '8.2%', 'manufacturers': '900+', 'export_value': '$3.2B'},
                'insights': [{'title': 'Morbi: The Ceramic City', 'content': 'Morbi produces 70%+ of India\'s tiles with 600+ manufacturing units.', 'year': 2024}],
                'states': [
                    {'name': 'Gujarat', 'type': 'State', 'hub': True, 'desc': "India's largest tile-producing state",
                     'cities': [
                         {'name': 'Morbi', 'type': 'City', 'hub': True, 'villages': ['Ceramic Industrial Estate', 'Wankaner Road Area', 'Tankara Road', 'Maliya Miyana Road', 'NH-8A Industrial Area', 'Vavdi Industrial Area', 'Navagam', 'Gondal Road Area', 'Limbdi Road', 'Halvad Road', 'Dhariwad Village', 'Kharaghoda Village', 'Miyana Village', 'Bhalgamda Village', 'Khanpur Village']},
                         {'name': 'Rajkot', 'type': 'City', 'hub': False, 'villages': ['Rajkot City Area', 'Jamnagar Road', 'Bhavnagar Road', 'Morbi Highway Area', 'Kalawad Road', 'Gondal Road', 'Wankaner Road']},
                         {'name': 'Ahmedabad', 'type': 'City', 'hub': False, 'villages': ['SG Highway Area', 'Naroda Industrial Area', 'Odhav Industrial Estate', 'Vatva GIDC', 'Chandkheda', 'Bopal', 'Thaltej', 'Prahlad Nagar', 'Mansi Crossroad', 'Drive-in Road', 'Satellite', 'Vastrapur', 'Navrangpura', 'Relief Road Tiles Market']},
                         {'name': 'Surat', 'type': 'City', 'hub': False, 'villages': ['Ring Road Tiles Market', 'Dumas Road', 'Katra Road', 'Rander Road', 'Sachin GIDC', 'Kapodra Patiya', 'Pandesara Industrial Area', 'Udhna', 'Ved Road', 'Adajan']},
                         {'name': 'Vadodara', 'type': 'City', 'hub': False, 'villages': ['Sayajigunj Tiles Market', 'Alkapuri', 'Gotri Road', 'Tandalja Industrial Area', 'Makarpura GIDC', 'Chhani Road', 'Vasna-Bhayli Road', 'Manjalpur', 'Karelibaug', 'Fatehgunj']},
                     ]},
                    {'name': 'Rajasthan', 'type': 'State', 'hub': True, 'desc': 'Kishangarh is the marble and tile processing hub',
                     'cities': [
                         {'name': 'Kishangarh', 'type': 'City', 'hub': True, 'villages': ['Marble Industrial Area', 'NH-8 Tile Market', 'Madanganj Area', 'Roopangarh Road', 'Ghati Village', 'Tilonia Village', 'Ajkhera Village', 'Rupnagar Village', 'Khari Khera', 'Mundiyar Village', 'Gogelav Village', 'Makrana Road Area']},
                         {'name': 'Jaipur', 'type': 'City', 'hub': False, 'villages': ['Sanganer Tiles Market', 'MI Road', 'Tonk Road Tiles Market', 'Ajmer Road Industrial Area', 'Sitapura Industrial Area', 'Jhotwara', 'Mansarovar', 'Malviya Nagar', 'Vidhyadhar Nagar', 'Jagatpura', 'Pratap Nagar', 'C-Scheme']},
                         {'name': 'Jodhpur', 'type': 'City', 'hub': False, 'villages': ['Paota Tiles Market', 'Sojati Gate Area', 'Mandore Road', 'Pali Road Industrial Area', 'Basni Industrial Area', 'Shastri Nagar', 'Ratanada', 'Sardarpura']},
                         {'name': 'Udaipur', 'type': 'City', 'hub': False, 'villages': ['Sukhadia Circle Tiles Area', 'Fateh Sagar Road', 'Hiran Magri', 'Sector 11-14', 'Bhopalpura', 'Chetak Circle', 'Rampura Circle']},
                     ]},
                    {'name': 'Tamil Nadu', 'type': 'State', 'hub': False, 'desc': 'Major southern market',
                     'cities': [
                         {'name': 'Chennai', 'type': 'City', 'hub': False, 'villages': ['Anna Nagar Tiles Market', 'Velachery', 'OMR Road', 'Porur', 'Ambattur Industrial Estate', 'Thiruvottiyur', 'Padi', 'Mogappair', 'Kodambakkam', 'T Nagar Tiles Market', 'Chromepet', 'Tambaram', 'Pallikaranai', 'Sholinganallur']},
                         {'name': 'Coimbatore', 'type': 'City', 'hub': False, 'villages': ['RS Puram Tiles Market', 'Avinashi Road', 'Peelamedu', 'Sundarapuram', 'Ukkadam', 'Gandhipuram', 'Saibaba Colony', 'Singanallur', 'Hopes College', 'Ramanathapuram']},
                         {'name': 'Salem', 'type': 'City', 'hub': False, 'villages': ['Five Roads Tiles Market', 'Omalur Road', 'Suramangalam', 'Kondalampatti', 'Fairlands', 'Meyyanur', 'Ammapet', 'Sevvapet']},
                         {'name': 'Madurai', 'type': 'City', 'hub': False, 'villages': ['North Masi Street Tiles Market', 'Vadipatti Road', 'Bypass Road', 'K. Pudur', 'Anna Nagar', 'KK Nagar', 'Tallakulam', 'Goripalayam']},
                     ]},
                    {'name': 'Karnataka', 'type': 'State', 'hub': False, 'desc': 'Growing market with Bangalore as major center',
                     'cities': [
                         {'name': 'Bangalore', 'type': 'City', 'hub': False, 'villages': ['JP Nagar Tiles Market', 'Bannerghatta Road', 'Whitefield', 'Electronic City', 'Yelahanka', 'Hennur Road', 'Tumkur Road Tiles Market', 'Mysore Road Industrial Area', 'Peenya Industrial Area', 'Rajajinagar', 'Basaveshwara Nagar', 'Marathahalli', 'HSR Layout', 'Koramangala', 'Bellandur', 'Sarjapur Road']},
                         {'name': 'Mysore', 'type': 'City', 'hub': False, 'villages': ['Saraswathipuram Tiles Market', 'Vijayanagar', 'Gokulam', 'Hunsur Road', 'Bannimantap', 'Kuvempu Nagar', 'Nazarbad', 'Lashkar Mohalla']},
                         {'name': 'Hubli', 'type': 'City', 'hub': False, 'villages': ['Old Hubli Tiles Market', 'Dharwad Road', 'Gokul Road', 'Vidyanagar', 'Industrial Area Hubli', 'Kumarpadam', 'Akshay Colony']},
                     ]},
                    {'name': 'Maharashtra', 'type': 'State', 'hub': False, 'desc': 'Largest state economy, Mumbai is massive market',
                     'cities': [
                         {'name': 'Mumbai', 'type': 'City', 'hub': False, 'villages': ['Andheri Tiles Market', 'Borivali', 'Malad', 'Kandivali', 'Goregaon', 'Juhu', 'Bandra', 'Dadar Tiles Market', 'Lower Parel', 'Powai', 'Thane', 'Navi Mumbai', 'Vashi', 'Kalyan', 'Dombivli', 'Palghar', 'Virar']},
                         {'name': 'Pune', 'type': 'City', 'hub': False, 'villages': ['SB Road Tiles Market', 'FC Road Area', 'Hadapsar', 'Hinjewadi', 'Wakad', 'Baner', 'Pimpri-Chinchwad', 'Chinchwad', 'Bhosari', 'Talegaon', 'Lonavala Road', 'Sinhagad Road', 'Kothrud', 'Warje', 'Katraj', 'Hadapsar MIDC', 'Chakan Industrial Area']},
                         {'name': 'Nashik', 'type': 'City', 'hub': False, 'villages': ['College Road Tiles Market', 'Indira Nagar', 'Satpur Industrial Area', 'Ambad MIDC', 'Gangapur Road', 'Panchavati', 'Nashik Road', 'Deolali', 'Igatpuri Road']},
                         {'name': 'Nagpur', 'type': 'City', 'hub': False, 'villages': ['Dharampeth Tiles Market', 'Sitabuldi', 'Wardha Road', 'Amravati Road', 'Hingna Road', 'MIHAN Area', 'Kamptee Road', 'Sadar']},
                     ]},
                    {'name': 'Uttar Pradesh', 'type': 'State', 'hub': False, 'desc': 'Huge market driven by NCR region',
                     'cities': [
                         {'name': 'Noida', 'type': 'City', 'hub': False, 'villages': ['Sector 18 Tiles Market', 'Sector 62', 'Sector 63', 'Sector 65', 'Sector 135', 'Greater Noida', 'Yamuna Expressway', 'Surajpur Industrial Area', 'Sector 12-22', 'Atta Market Area']},
                         {'name': 'Agra', 'type': 'City', 'hub': False, 'villages': ['Sadar Bazaar Tiles Market', 'M.G. Road', 'Fatehabad Road', 'Balkeshwar Road', 'Loha Mandi', 'Sanjay Place', 'Kamla Nagar', 'Shahganj']},
                         {'name': 'Varanasi', 'type': 'City', 'hub': False, 'villages': ['Godaulia Tiles Market', 'Sigra', 'Bhelupur', 'Lahurabir', 'Cantt Area', 'Maldahiya', 'Pandey Haveli', 'Assi Ghat Area']},
                         {'name': 'Lucknow', 'type': 'City', 'hub': False, 'villages': ['Aminabad Tiles Market', 'Hazratganj', 'Gomti Nagar', 'Kanpur Road', 'Sitapur Road Industrial Area', 'Amausi', 'Aliganj', 'Indira Nagar', 'Chinhat Industrial Area']},
                     ]},
                    {'name': 'Telangana', 'type': 'State', 'hub': False, 'desc': 'Hyderabad is a major tile consumption center',
                     'cities': [
                         {'name': 'Hyderabad', 'type': 'City', 'hub': False, 'villages': ['Abids Tiles Market', 'Begumpet', 'Madhapur', 'Kukatpally', 'Miyapur', 'Gachibowli', 'Hitech City', 'Attapur', 'LB Nagar', 'Dilsukhnagar', 'Tolichowki', 'Charminar Area', 'Mehdipatnam', 'Kukatpally Housing Board', 'Balapur', 'Shamshabad']},
                         {'name': 'Warangal', 'type': 'City', 'hub': False, 'villages': ['Kazipet Tiles Market', 'Hanamkonda', 'Warangal City', 'Narsampet Road', 'Parkal', 'Jangaon']},
                     ]},
                    {'name': 'Kerala', 'type': 'State', 'hub': False, 'desc': 'High per-capita tile consumption',
                     'cities': [
                         {'name': 'Kochi', 'type': 'City', 'hub': False, 'villages': ['Broadway Tiles Market', 'Edappally', 'Kalamassery', 'Aluva', 'Kakkanad', 'Vytilla', 'Palarivattom', 'Marad', 'Kaloor', 'MG Road']},
                         {'name': 'Thiruvananthapuram', 'type': 'City', 'hub': False, 'villages': ['Palayam Tiles Market', 'Kesavadasapuram', 'Sasthamangalam', 'Vellayambalam', 'Kowdiar', 'Pattom', 'Kazhakkoottam', 'Attingal', 'Neyyattinkara']},
                         {'name': 'Kozhikode', 'type': 'City', 'hub': False, 'villages': ['Mavoor Road Tiles Market', 'Sweet Meat Street', 'Palayam', 'Kuttichira', 'West Hill', 'Kannur Road', 'Feroke', 'Ramanattukara']},
                     ]},
                ],
            },
            'Brazil': {
                'flag_emoji': '🇧🇷', 'continent': 'South America', 'ranking': 3,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': 'Largest tile market in the Americas.',
                'market_overview': 'Brazil produces 1.1 billion sqm annually. Santa Catarina state (Criciúma) produces 60%+ of national output.',
                'key_stats': {'production_billion_sqm': 1.1, 'consumption_billion_sqm': 0.95, 'export_share': '18%', 'market_growth': '4.1%', 'manufacturers': '200+', 'export_value': '$450M'},
                'insights': [{'title': 'Santa Catarina Hub', 'content': 'Santa Catarina concentrates 60%+ of Brazilian tile production.', 'year': 2024}],
                'states': [
                    {'name': 'Santa Catarina', 'type': 'State', 'hub': True, 'desc': "Brazil's ceramic heartland",
                     'cities': [
                         {'name': 'Criciuma', 'type': 'City', 'hub': True, 'villages': ['Centro', 'Jardim Athena', 'Sao Jose', 'Pinheirinho', 'Covoqueira', 'Santa Barbara', 'Industrial District', 'Ipiranga', 'Quarta Linha', 'Linha Santa Terezinha', 'Sangao Village', 'Forquilhinha']},
                         {'name': 'Orleans', 'type': 'City', 'hub': True, 'villages': ['Centro', 'Barra do Rio Marombas', 'Sao Pedro', 'Braco do Norte Road', 'Industrial Zone', 'Sao Luiz', 'Sao Joao']},
                         {'name': 'Tubarao', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Distrito Industrial', 'Sao Joao', 'Passo de Torres', 'Pedras Grandes Area', 'Capivari de Baixo']},
                         {'name': 'Joinville', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Bucarein', 'Avenida Beira Rio', 'Distrito Industrial Norte', 'Saguaçu', 'Itaum', 'Pirabeiraba', 'Sao Francisco do Sul Road']},
                     ]},
                    {'name': 'Sao Paulo', 'type': 'State', 'hub': False, 'desc': 'Largest consumption market',
                     'cities': [
                         {'name': 'Sao Paulo', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Vila Mariana', 'Pinheiros', 'Moema', 'Itaim Bibi', 'Faria Lima', 'Lapa', 'Barra Funda', 'Tatuape', 'Santana', 'Zona Sul Tiles District', 'Consolação', 'Bela Vista', 'Liberdade', 'Bras Tiles Wholesale']},
                         {'name': 'Campinas', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Sao Jose', 'Barao Geraldo', 'Cambui', 'Swiss Park', 'Distrito Industrial', 'Jardim Campineiro', 'Sousas', 'Joaquim Egídio']},
                         {'name': 'Sorocaba', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Avenida Sao Carlos', 'Distrito Industrial', 'Eden', 'Jardim Paulista', 'Wanel Ville', 'Alto da Boa Vista']},
                     ]},
                    {'name': 'Rio de Janeiro', 'type': 'State', 'hub': False, 'desc': 'Major coastal market',
                     'cities': [
                         {'name': 'Rio de Janeiro', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Copacabana', 'Ipanema', 'Barra da Tijuca', 'Leblon', 'Tijuca', 'Niterói Connection', 'Recreio', 'Botafogo', 'Flamengo', 'Laranjeiras', 'Saara Tiles District']},
                         {'name': 'Petropolis', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Itaipava', 'Alto da Serra', 'Mosela', 'Valparaiso', 'Quitandinha']},
                     ]},
                    {'name': 'Minas Gerais', 'type': 'State', 'hub': False, 'desc': 'Large interior market',
                     'cities': [
                         {'name': 'Belo Horizonte', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Savassi', 'Lourdes', 'Funcionários', 'Contagem Industrial', 'Betim', 'Pampulha', 'Barreiro']},
                         {'name': 'Uberlandia', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Segredo', 'Tubalina', 'Santa Monica', 'Luizote de Freitas', 'Distrito Industrial']},
                     ]},
                ],
            },
            'Spain': {
                'flag_emoji': '🇪🇸', 'continent': 'Europe', 'ranking': 4,
                'is_top_producer': True, 'is_top_consumer': False,
                'description': "Global leader in high-quality tile manufacturing and world's second-largest exporter.",
                'market_overview': 'Spain produces 0.55 billion sqm, exports 80%. Castellón province is the ceramic engine of Europe.',
                'key_stats': {'production_billion_sqm': 0.55, 'consumption_billion_sqm': 0.12, 'export_share': '80%', 'market_growth': '2.8%', 'manufacturers': '150+', 'export_value': '$4.1B'},
                'insights': [{'title': 'Castellón: Ceramic Engine', 'content': 'Castellón hosts 90%+ of Spanish tile production.', 'year': 2024}],
                'states': [
                    {'name': 'Valencia', 'type': 'Autonomous Community', 'hub': True, 'desc': "Spain's ceramic heartland",
                     'cities': [
                         {'name': 'Castellon de la Plana', 'type': 'City', 'hub': True, 'villages': ['Centro', 'Zona Ceramica', 'Villarreal Area', 'Nules', 'Onda', 'Alcora', 'La Plana Industrial', 'Benicassim Road', 'Ribesalbes', 'Fanzara', 'Soneja', 'Artana', 'LAlcora Industrial', 'Vila-real Ceramics Zone', 'Saler Industrial']},
                         {'name': 'Valencia', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Ruzafa', 'Eixample', 'Cabanyal', 'Benimaclet', 'Paterna Industrial', 'Manises', 'Quart de Poblet', 'Sedavi', 'Alboraya']},
                         {'name': 'Alicante', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Playa de San Juan', 'Villajoyosa Area', 'Elche Industrial', 'Elda', 'Petrer', 'Novelda']},
                     ]},
                    {'name': 'Catalonia', 'type': 'Autonomous Community', 'hub': False, 'desc': 'Major consumption market',
                     'cities': [
                         {'name': 'Barcelona', 'type': 'City', 'hub': False, 'villages': ['Eixample', 'Gracia', 'Sants', 'Poblenou', 'Zona Franca', 'Diagonal Mar', 'Les Corts', 'Sarria', 'Sant Marti', 'El Raval']},
                         {'name': 'Tarragona', 'type': 'City', 'hub': False, 'villages': ['Centro', 'El Serrallo', 'Reus Area', 'Valls', 'Salou', 'Cambrils', 'Constanti Industrial']},
                     ]},
                    {'name': 'Andalusia', 'type': 'Autonomous Community', 'hub': False, 'desc': 'Large southern market',
                     'cities': [
                         {'name': 'Seville', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Triana', 'Nervion', 'Los Remedios', 'Sevilla Este', 'Alcalá de Guadaíra', 'Dos Hermanas', 'Mairena del Alcor']},
                         {'name': 'Malaga', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Marbella', 'Fuengirola', 'Benalmádena', 'Mijas', 'Torremolinos', 'Antequera', 'Rincón de la Victoria']},
                     ]},
                ],
            },
            'Italy': {
                'flag_emoji': '🇮🇹', 'continent': 'Europe', 'ranking': 5,
                'is_top_producer': True, 'is_top_consumer': False,
                'description': 'Birthplace of premium tile manufacturing.',
                'market_overview': 'Italy produces 0.45 billion sqm, exports 82%. Sassuolo (Modena) is the most advanced ceramic district worldwide.',
                'key_stats': {'production_billion_sqm': 0.45, 'consumption_billion_sqm': 0.08, 'export_share': '82%', 'market_growth': '1.9%', 'manufacturers': '130+', 'export_value': '$5.8B'},
                'insights': [{'title': 'Sassuolo Innovation Hub', 'content': 'Sassuolo district leads global tile technology.', 'year': 2024}],
                'states': [
                    {'name': 'Emilia-Romagna', 'type': 'Region', 'hub': True, 'desc': "World's most advanced ceramic district",
                     'cities': [
                         {'name': 'Sassuolo', 'type': 'City', 'hub': True, 'villages': ['Centro Ceramico', 'Fiorano Modenese', 'Scandiano', 'Formigine', 'Maranello', 'Casalgrande', 'Castelnuovo Rangone', 'Rubiera', 'Baggiovara', 'Montegibbio', 'San Michele dei Mucchietti', 'Pavullo nel Frignano Area', 'Polinario']},
                         {'name': 'Bologna', 'type': 'City', 'hub': False, 'villages': ['Centro Storico', 'Santo Stefano', 'Via dellIndipendenza', 'Fiera District', 'Casteldebole', 'Borgo Panigale', 'Zola Predosa', 'Casalecchio di Reno']},
                         {'name': 'Reggio Emilia', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Via Emilia', 'Santa Croce', 'Boretto', 'Guastalla', 'Correggio', 'Scandiano Area']},
                     ]},
                    {'name': 'Lombardy', 'type': 'Region', 'hub': False, 'desc': 'Major consumption market',
                     'cities': [
                         {'name': 'Milan', 'type': 'City', 'hub': False, 'villages': ['Centro Storico', 'Brera Design District', 'Porta Nuova', 'Tortona Design District', 'Rho Fiera', 'Sesto San Giovanni', 'Cinisello Balsamo', 'Monza']},
                         {'name': 'Bergamo', 'type': 'City', 'hub': False, 'villages': ['Città Alta', 'Città Bassa', 'Albino', 'Treviglio', 'Romano di Lombardia', 'Dalmine']},
                     ]},
                    {'name': 'Veneto', 'type': 'Region', 'hub': False, 'desc': 'Strong tile market',
                     'cities': [
                         {'name': 'Verona', 'type': 'City', 'hub': False, 'villages': ['Centro Storico', 'Borgo Trento', 'San Giovanni Lupatoto', 'Villafranca di Verona', 'Legnago', 'Cerea']},
                         {'name': 'Treviso', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Conegliano', 'Montebelluna', 'Castelfranco Veneto', 'Valdobbiadene']},
                     ]},
                    {'name': 'Tuscany', 'type': 'Region', 'hub': False, 'desc': 'Historic ceramic region',
                     'cities': [
                         {'name': 'Florence', 'type': 'City', 'hub': False, 'villages': ['Centro Storico', 'Oltrarno', 'Campo di Marte', 'Novoli', 'Scandicci', 'Prato', 'Empoli', 'Pontedera']},
                         {'name': 'Prato', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Macrolotto', 'Iolo', 'Carmignano', 'Vernio', 'Vaiano']},
                     ]},
                ],
            },
            'Turkey': {
                'flag_emoji': '🇹🇷', 'continent': 'Europe/Middle East', 'ranking': 6,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': 'Strategic tile producer bridging Europe, Middle East, and Africa.',
                'market_overview': 'Turkey produces 0.42 billion sqm, exports 55%. Bilecik and Kütahya are the main production centers.',
                'key_stats': {'production_billion_sqm': 0.42, 'consumption_billion_sqm': 0.25, 'export_share': '55%', 'market_growth': '5.3%', 'manufacturers': '80+', 'export_value': '$1.8B'},
                'insights': [{'title': 'Strategic Location', 'content': 'Turkey bridges Europe and Asia for tile exports.', 'year': 2024}],
                'states': [
                    {'name': 'Bilecik', 'type': 'Province', 'hub': True, 'desc': "Turkey's primary tile production center",
                     'cities': [
                         {'name': 'Bilecik Merkez', 'type': 'City', 'hub': True, 'villages': ['Centrum', 'Organized Industrial Zone', 'Inonu', 'Bozuyuk Road', 'Osmaneli', 'Pazaryeri', 'Golpazari', 'Sogut Road', 'Yenipazar', 'Bayirkoy']},
                         {'name': 'Bozuyuk', 'type': 'City', 'hub': True, 'villages': ['Centrum', 'Organize Sanayi Bolgesi', 'Karaagac', 'Akcaalan', 'Duzcami', 'Komurcuadem', 'Saricalar', 'Yenikoy', 'Buyukdere']},
                         {'name': 'Sogut', 'type': 'Town', 'hub': False, 'villages': ['Centrum', 'Kirka', 'Calti', 'Haybardi', 'Kure']},
                     ]},
                    {'name': 'Kutahya', 'type': 'Province', 'hub': True, 'desc': 'Historic ceramic city, major production',
                     'cities': [
                         {'name': 'Kutahya Merkez', 'type': 'City', 'hub': True, 'villages': ['Centrum', 'Organized Industrial Zone', 'Domanic Road', 'Tavsanli Road', 'Simav Road', 'Gediz', 'Emet', 'Hisarcik', 'Pazarlar']},
                         {'name': 'Tavsanli', 'type': 'City', 'hub': False, 'villages': ['Centrum', 'OSB Area', 'Balikesir Road', 'Kutahya Road', 'Gonen Road', 'Kizilcaoren']},
                     ]},
                    {'name': 'Istanbul', 'type': 'Province', 'hub': False, 'desc': 'Largest consumption market',
                     'cities': [
                         {'name': 'Istanbul European Side', 'type': 'District', 'hub': False, 'villages': ['Kadikoy', 'Bakirkoy', 'Sisli', 'Besiktas', 'Fatih', 'Beyoglu', 'Esenler Tiles Market', 'Bagcilar', 'Basaksehir', 'Buyukcekmece', 'Avcilar', 'Beylikduzu', 'Silivri', 'Gungoren', 'Zeytinburnu', 'Kucukcekmece']},
                         {'name': 'Istanbul Asian Side', 'type': 'District', 'hub': False, 'villages': ['Uskudar', 'Umraniye', 'Atasehir', 'Kartal', 'Pendik', 'Tuzla', 'Maltepe', 'Sultanbeyli', 'Sancaktepe', 'Cekmekoy', 'Sile']},
                     ]},
                    {'name': 'Izmir', 'type': 'Province', 'hub': False, 'desc': 'Aegean coast market',
                     'cities': [
                         {'name': 'Izmir Merkez', 'type': 'City', 'hub': False, 'villages': ['Konak', 'Bornova', 'Karsiyaka', 'Buca', 'Cigli', 'Bayrakli', 'Gaziemir', 'Karabaglar', 'Alsancak', 'Kemeralti Tiles Market', 'Menemen', 'Torbalı', 'Kemalpasa']},
                     ]},
                ],
            },
            'Vietnam': {
                'flag_emoji': '🇻🇳', 'continent': 'Asia', 'ranking': 7,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': 'Rapidly growing tile manufacturing hub in Southeast Asia.',
                'market_overview': 'Vietnam produces 0.65 billion sqm. Binh Duong is the main production hub.',
                'key_stats': {'production_billion_sqm': 0.65, 'consumption_billion_sqm': 0.55, 'export_share': '12%', 'market_growth': '7.5%', 'manufacturers': '150+', 'export_value': '$280M'},
                'insights': [{'title': 'ASEAN Export Growth', 'content': 'Vietnamese tile exports to ASEAN grew 25%.', 'year': 2024}],
                'states': [
                    {'name': 'Binh Duong', 'type': 'Province', 'hub': True, 'desc': "Vietnam's ceramic capital",
                     'cities': [
                         {'name': 'Thu Dau Mot', 'type': 'City', 'hub': True, 'villages': ['Chon Lon', 'Phu My', 'Di An Connection', 'Tan Uyen Road', 'Ben Cat', 'My Phuoc', 'Thoi Hoa', 'Tuong Binh Hiep', 'Hoa Phu', 'Vinh Tan']},
                         {'name': 'Di An', 'type': 'City', 'hub': False, 'villages': ['Di An Town Center', 'Binh Thang', 'Tan Binh', 'Dong Hoa', 'Linh Xuan', 'An Binh', 'Binh An', 'Tam Binh']},
                         {'name': 'Tan Uyen', 'type': 'Town', 'hub': False, 'villages': ['Tan Uyen Center', 'Uyen Hung', 'Bac Tan Uyen', 'Thanh Phu', 'Hoi Nghia', 'Vinh Hoa', 'Khanh Binh']},
                     ]},
                    {'name': 'Dong Nai', 'type': 'Province', 'hub': False, 'desc': 'Southern production zone',
                     'cities': [
                         {'name': 'Bien Hoa', 'type': 'City', 'hub': False, 'villages': ['Quang Vinh', 'Tam Hiep', 'Trang Dai', 'Long Binh', 'Tan Hiep', 'Ho Nai', 'Buu Hoa', 'Tam Phuoc']},
                         {'name': 'Long Khanh', 'type': 'City', 'hub': False, 'villages': ['Long Khanh Center', 'Bao Vinh', 'Xuan Loc', 'Dinh Quan', 'Cam My']},
                     ]},
                    {'name': 'Ho Chi Minh City', 'type': 'Municipality', 'hub': False, 'desc': 'Largest consumption market',
                     'cities': [
                         {'name': 'District 1', 'type': 'District', 'hub': False, 'villages': ['Ben Nghe', 'Ben Thanh', 'Cau Kho', 'Cau Ong Lanh', 'Nguyen Cu Trinh', 'Pham Ngu Lao', 'Tan Dinh']},
                         {'name': 'District 7', 'type': 'District', 'hub': False, 'villages': ['Phu My Hung', 'Tan Thuan Dong', 'Tan Thuan Tay', 'Binh Thuan', 'Phu Thuan', 'Tan Phong', 'Tan Quy']},
                         {'name': 'Binh Thanh', 'type': 'District', 'hub': False, 'villages': ['Binh Thanh Center', 'Phu Nhuan Connection', 'Van Thanh', 'Nguyen Hue', '26 Ly Thuong Kiet Area', 'Phu Dinh']},
                     ]},
                    {'name': 'Hanoi', 'type': 'Municipality', 'hub': False, 'desc': 'Northern capital market',
                     'cities': [
                         {'name': 'Hoan Kiem', 'type': 'District', 'hub': False, 'villages': ['Old Quarter', 'Hang Bac', 'Hang Dao', 'Hang Ma', 'Trang Tien', 'Ly Thai To']},
                         {'name': 'Cau Giay', 'type': 'District', 'hub': False, 'villages': ['Cau Giay Center', 'Nghia Do', 'Dich Vong', 'Mai Dich', 'Yen Hoa', 'Quan Hoa', 'Trung Hoa']},
                         {'name': 'Ha Dong', 'type': 'District', 'hub': False, 'villages': ['Ha Dong Center', 'Yen Nghia', 'Mo Lao', 'Van Quan', 'Phu Lam', 'Kien Hung', 'Dong Mai']},
                     ]},
                ],
            },
            'United States': {
                'flag_emoji': '🇺🇸', 'continent': 'North America', 'ranking': 8,
                'is_top_producer': False, 'is_top_consumer': True,
                'description': "World's largest tile import market.",
                'market_overview': 'US consumes 0.95 billion sqm, imports 70-75%. Strong preference for large format and wood-look tiles.',
                'key_stats': {'production_billion_sqm': 0.08, 'consumption_billion_sqm': 0.95, 'export_share': '5%', 'import_value': '$3.8B'},
                'insights': [{'title': 'Anti-Dumping Impact', 'content': 'US duties shifted imports from China to Spain, India, Turkey, Mexico.', 'year': 2024}],
                'states': [
                    {'name': 'California', 'type': 'State', 'hub': False, 'desc': 'Largest US tile market',
                     'cities': [
                         {'name': 'Los Angeles', 'type': 'City', 'hub': False, 'villages': ['Downtown LA', 'Santa Monica', 'Beverly Hills', 'Hollywood', 'Culver City', 'Pasadena', 'Glendale', 'Burbank', 'Torrance', 'Long Beach', 'Anaheim', 'Irvine', 'Huntington Beach', 'Santa Ana', 'Costa Mesa']},
                         {'name': 'San Francisco', 'type': 'City', 'hub': False, 'villages': ['SoMa', 'Mission District', 'Marina', 'Pacific Heights', 'Hayes Valley', 'Oakland', 'Berkeley', 'San Jose', 'Palo Alto', 'Mountain View', 'Sunnyvale', 'Fremont']},
                         {'name': 'San Diego', 'type': 'City', 'hub': False, 'villages': ['Gaslamp Quarter', 'La Jolla', 'Del Mar', 'Carlsbad', 'Encinitas', 'Coronado', 'Mission Valley', 'Point Loma', 'Pacific Beach']},
                     ]},
                    {'name': 'Texas', 'type': 'State', 'hub': False, 'desc': 'Second largest market',
                     'cities': [
                         {'name': 'Houston', 'type': 'City', 'hub': False, 'villages': ['Downtown Houston', 'The Heights', 'Montrose', 'Galleria Area', 'Katy', 'Sugar Land', 'The Woodlands', 'Pearland', 'Clear Lake', 'Memorial', 'River Oaks', 'Midtown']},
                         {'name': 'Dallas', 'type': 'City', 'hub': False, 'villages': ['Downtown Dallas', 'Uptown', 'Deep Ellum', 'Design District', 'Plano', 'Frisco', 'McKinney', 'Richardson', 'Irving', 'Garland', 'Arlington', 'Fort Worth']},
                         {'name': 'Austin', 'type': 'City', 'hub': False, 'villages': ['Downtown Austin', 'South Congress', 'East Austin', 'Zilker', 'Barton Creek', 'Round Rock', 'Cedar Park', 'Westlake', 'Tarrytown']},
                     ]},
                    {'name': 'Florida', 'type': 'State', 'hub': False, 'desc': 'Major coastal market',
                     'cities': [
                         {'name': 'Miami', 'type': 'City', 'hub': False, 'villages': ['Downtown Miami', 'Miami Beach', 'Brickell', 'Wynwood', 'Coconut Grove', 'Coral Gables', 'Doral', 'Aventura', 'Key Biscayne', 'South Beach', 'Design District']},
                         {'name': 'Orlando', 'type': 'City', 'hub': False, 'villages': ['Downtown Orlando', 'Winter Park', 'Baldwin Park', 'Lake Nona', 'Dr. Phillips', 'Celebration', 'Kissimmee']},
                     ]},
                    {'name': 'New York', 'type': 'State', 'hub': False, 'desc': 'Northeast market',
                     'cities': [
                         {'name': 'New York City', 'type': 'City', 'hub': False, 'villages': ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island', 'Harlem', 'Upper East Side', 'Upper West Side', 'Midtown', 'SoHo', 'Tribeca', 'Chelsea', 'Williamsburg', 'DUMBO', 'Astoria', 'Long Island City']},
                     ]},
                    {'name': 'New Jersey', 'type': 'State', 'hub': False, 'desc': 'Dense suburban tile market',
                     'cities': [
                         {'name': 'Newark', 'type': 'City', 'hub': False, 'villages': ['Downtown Newark', 'Ironbound', 'Forest Hill', 'University Heights', 'North Ward', 'East Ward']},
                         {'name': 'Jersey City', 'type': 'City', 'hub': False, 'villages': ['Downtown Jersey City', 'Newport', 'Paulus Hook', 'Journal Square', 'Heights', 'Greenville', 'West Side']},
                     ]},
                    {'name': 'Illinois', 'type': 'State', 'hub': False, 'desc': 'Midwest market',
                     'cities': [
                         {'name': 'Chicago', 'type': 'City', 'hub': False, 'villages': ['Loop', 'River North', 'Lincoln Park', 'Wicker Park', 'Bucktown', 'West Loop', 'Gold Coast', 'Lakeview', 'Logan Square', 'Hyde Park', 'South Loop', 'Magnificent Mile', 'Streeterville', 'Old Town']},
                     ]},
                ],
            },
            'Mexico': {
                'flag_emoji': '🇲🇽', 'continent': 'North America', 'ranking': 9,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': 'Major North American producer with duty-free US access under USMCA.',
                'market_overview': 'Mexico produces 0.38 billion sqm, exports 30%. Jalisco (Guadalajara) produces 70% of national output.',
                'key_stats': {'production_billion_sqm': 0.38, 'consumption_billion_sqm': 0.28, 'export_share': '30%', 'market_growth': '3.8%', 'manufacturers': '120+', 'export_value': '$520M'},
                'insights': [{'title': 'USMCA Advantage', 'content': 'Duty-free access to US gives Mexico competitive edge.', 'year': 2024}],
                'states': [
                    {'name': 'Jalisco', 'type': 'State', 'hub': True, 'desc': "Mexico's ceramic heartland",
                     'cities': [
                         {'name': 'Guadalajara', 'type': 'City', 'hub': True, 'villages': ['Centro Historico', 'Minerva', 'Puerta de Hierro', 'Zapopan', 'Tlaquepaque', 'Tonala', 'Tlajomulco de Zuniga', 'El Salto', 'San Pedro Tlaquepaque Centro', 'Santa Anita', 'Nextipac', 'San Juan de Dios', 'Lazaro Cardenas']},
                         {'name': 'Zapopan', 'type': 'City', 'hub': False, 'villages': ['Centro Zapopan', 'Andares', 'Arcos Vallarta', 'Tesistan', 'San Esteban', 'Santa Cruz del Valle', 'Cruz de la Laguna']},
                         {'name': 'Tlaquepaque', 'type': 'City', 'hub': True, 'villages': ['Centro Tlaquepaque', 'Zona Ceramica', 'Santa Anita', 'El Refugio', 'San Pedro Tlaquepaque', 'Tonala Border', 'El Rosario', 'La Sauceda']},
                     ]},
                    {'name': 'Nuevo Leon', 'type': 'State', 'hub': False, 'desc': 'Northern industrial market',
                     'cities': [
                         {'name': 'Monterrey', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Cumbres', 'Garza Garcia', 'San Pedro Garza Garcia', 'Apodaca', 'Escobedo', 'Guadalupe', 'Juarez', 'Anahuac', 'Valle Oriente']},
                         {'name': 'San Nicolas de los Garza', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Zona Industrial', 'Anahuac Area', 'Unidad Modelo', 'Ninos Heroes']},
                     ]},
                    {'name': 'Puebla', 'type': 'State', 'hub': False, 'desc': 'Central Mexican market',
                     'cities': [
                         {'name': 'Puebla', 'type': 'City', 'hub': False, 'villages': ['Centro Historico', 'Angelopolis', 'Jardines de San Manuel', 'La Paz', 'San Baltazar Campeche', 'Cholula', 'Amozoc', 'Huejotzingo']},
                     ]},
                    {'name': 'Veracruz', 'type': 'State', 'hub': False, 'desc': 'Gulf coast market',
                     'cities': [
                         {'name': 'Veracruz', 'type': 'City', 'hub': False, 'villages': ['Centro', 'Boca del Rio', 'Mandinga', 'Costa de Oro', 'Zona Industrial', 'Medellin de Bravo']},
                         {'name': 'Xalapa', 'type': 'City', 'hub': False, 'villages': ['Centro Xalapa', 'Las Animas', 'Coatepec', 'Banderilla', 'Tlapacoyan', 'Xico']},
                     ]},
                ],
            },
            'Indonesia': {
                'flag_emoji': '🇮🇩', 'continent': 'Asia', 'ranking': 10,
                'is_top_producer': True, 'is_top_consumer': True,
                'description': 'Strong domestic market of 270+ million people.',
                'market_overview': 'Indonesia produces 0.48 billion sqm. Java island hosts most production. Local brands dominate 60%+ market.',
                'key_stats': {'production_billion_sqm': 0.48, 'consumption_billion_sqm': 0.42, 'export_share': '10%', 'market_growth': '5.8%', 'manufacturers': '100+', 'export_value': '$180M'},
                'insights': [{'title': 'New Capital Nusantara', 'content': 'New capital city will create significant tile demand.', 'year': 2024}],
                'states': [
                    {'name': 'West Java', 'type': 'Province', 'hub': False, 'desc': 'Largest tile market',
                     'cities': [
                         {'name': 'Bandung', 'type': 'City', 'hub': False, 'villages': ['Coblong', 'Sukajadi', 'Cicendo', 'Sumur Bandung', 'Bandung Wetan', 'Buah Batu', 'Antapani', 'Arcamanik', 'Kiaracondong', 'Babakan Ciamis', 'Cimahi', 'Lembang', 'Dago', 'Pasteur']},
                         {'name': 'Bekasi', 'type': 'City', 'hub': False, 'villages': ['Bekasi Timur', 'Bekasi Barat', 'Bekasi Selatan', 'Bekasi Utara', 'Pondok Gede', 'Cikarang', 'Jababeka Industrial', 'MM2100 Industrial', 'Delta Mas', 'Lippo Cikarang']},
                         {'name': 'Bogor', 'type': 'City', 'hub': False, 'villages': ['Bogor Tengah', 'Bogor Utara', 'Bogor Selatan', 'Bogor Barat', 'Bogor Timur', 'Tanah Barat', 'Cibinong', 'Sentul', 'Dramaga']},
                         {'name': 'Depok', 'type': 'City', 'hub': False, 'villages': ['Beji', 'Cimanggis', 'Limo', 'Pancoran Mas', 'Sawangan', 'Bojongsari', 'Margonda', 'Depok Jaya', 'Tapos']},
                     ]},
                    {'name': 'East Java', 'type': 'Province', 'hub': True, 'desc': 'Major production center',
                     'cities': [
                         {'name': 'Surabaya', 'type': 'City', 'hub': False, 'villages': ['Gubeng', 'Genteng', 'Tegalsari', 'Wonokromo', 'Rungkut', 'Mulyorejo', 'Sukolilo', 'Kenjeran', 'Tambaksari', 'Benowo', 'Asemrowo', 'Bubutan']},
                         {'name': 'Malang', 'type': 'City', 'hub': False, 'villages': ['Klojen', 'Blimbing', 'Kedungkandang', 'Lowokwaru', 'Batu', 'Lawang', 'Singosari', 'Dampit']},
                         {'name': 'Gresik', 'type': 'City', 'hub': True, 'villages': ['Gresik Center', 'Ceramic Industrial Zone', 'Kebomas', 'Manyar', 'Menganti', 'Driyorejo', 'Bungah', 'Sidakarya']},
                     ]},
                    {'name': 'Central Java', 'type': 'Province', 'hub': False, 'desc': 'Central Java market',
                     'cities': [
                         {'name': 'Semarang', 'type': 'City', 'hub': False, 'villages': ['Semarang Tengah', 'Semarang Utara', 'Semarang Selatan', 'Semarang Barat', 'Semarang Timur', 'Banyumanik', 'Candisari', 'Gajah Mungkur', 'Tembalang', 'Ungaran', 'Kendal']},
                         {'name': 'Solo (Surakarta)', 'type': 'City', 'hub': False, 'villages': ['Laweyan', 'Serengan', 'Pasar Kliwon', 'Jebres', 'Banjarsari', 'Kartasura', 'Boyolali', 'Sukoharjo']},
                     ]},
                    {'name': 'DKI Jakarta', 'type': 'Special Capital Region', 'hub': False, 'desc': 'Capital and largest market',
                     'cities': [
                         {'name': 'Jakarta Pusat', 'type': 'District', 'hub': False, 'villages': ['Menteng', 'Tanah Abang', 'Gambir', 'Senen', 'Kemayoran', 'Cempaka Putih', 'Johar Baru']},
                         {'name': 'Jakarta Selatan', 'type': 'District', 'hub': False, 'villages': ['Kebayoran Baru', 'Kebayoran Lama', 'Cipete', 'Kemang', 'Pondok Indah', 'Mangga Dua Selatan', 'Tebet', 'Pancoran', 'Kalibata', 'Pesanggrahan', 'Cilandak', 'Lebak Bulus']},
                         {'name': 'Jakarta Barat', 'type': 'District', 'hub': False, 'villages': ['Grogol', 'Palmerah', 'Slipi', 'Kebon Jeruk', 'Cengkareng', 'Kalideres', 'Taman Sari', 'Tambora']},
                     ]},
                    {'name': 'Banten', 'type': 'Province', 'hub': False, 'desc': 'Greater Jakarta industrial zone',
                     'cities': [
                         {'name': 'Tangerang', 'type': 'City', 'hub': False, 'villages': ['Tangerang Center', 'Cipondoh', 'Karawaci', 'Serpong', 'BSD City', 'Gading Serpong', 'Alam Sutera', 'Bintaro', 'Cikokol', 'Pinang', 'Karang Tengah']},
                         {'name': 'Serang', 'type': 'City', 'hub': False, 'villages': ['Serang Center', 'Cipocok Jaya', 'Walantaka', 'Kasemen', 'Taktakan', 'Curug']},
                     ]},
                ],
            },
        }

        for country_name, cdata in LOCATIONS.items():
            country, created = Country.objects.update_or_create(
                name=country_name,
                defaults={
                    'slug': slugify(country_name),
                    'flag_emoji': cdata['flag_emoji'],
                    'continent': cdata['continent'],
                    'ranking': cdata['ranking'],
                    'is_top_producer': cdata.get('is_top_producer', False),
                    'is_top_consumer': cdata.get('is_top_consumer', False),
                    'description': cdata.get('description', ''),
                    'market_overview': cdata.get('market_overview', ''),
                    'key_stats': cdata.get('key_stats', {}),
                }
            )
            status = self.style.SUCCESS('CREATED') if created else self.style.WARNING('UPDATED')
            self.stdout.write(f'    {status} {country_name}')

            for ins in cdata.get('insights', []):
                MarketInsight.objects.update_or_create(
                    country=country, title=ins['title'],
                    defaults={'content': ins['content'], 'year': ins['year']}
                )

            for sdata in cdata.get('states', []):
                state, _ = State.objects.update_or_create(
                    country=country, name=sdata['name'],
                    defaults={'slug': slugify(sdata['name']), 'state_type': sdata['type'], 'description': sdata.get('desc', ''), 'is_tile_hub': sdata.get('hub', False)}
                )
                for cdata2 in sdata.get('cities', []):
                    city, _ = City.objects.update_or_create(
                        state=state, name=cdata2['name'],
                        defaults={'slug': slugify(cdata2['name']), 'city_type': cdata2['type'], 'is_tile_hub': cdata2.get('hub', False)}
                    )
                    village_list = cdata2.get('villages', [])
                    if isinstance(village_list, str):
                        village_list = [v.strip() for v in village_list.split(',')]
                    for vname in village_list:
                        Village.objects.get_or_create(
                            city=city, name=vname,
                            defaults={'slug': slugify(vname), 'area_type': 'Area'}
                        )

        self.stdout.write(f'\n  Location Stats:')
        self.stdout.write(f'     Countries: {Country.objects.count()}')
        self.stdout.write(f'     States/Provinces: {State.objects.count()}')
        self.stdout.write(f'     Cities: {City.objects.count()}')
        self.stdout.write(f'     Villages/Areas: {Village.objects.count()}')

    def _link_tiles_to_countries(self):

         india = Country.objects.get(name="India")
         italy = Country.objects.get(name="Italy")
         china = Country.objects.get(name="China")
         spain = Country.objects.get(name="Spain")

         TileProduct.objects.filter(
        name__icontains="Indian"
    ).update()

         for tile in TileProduct.objects.filter(name__icontains="Indian"):
           tile.countries.set([india])

         for tile in TileProduct.objects.filter(name__icontains="Italian"):
            tile.countries.set([italy])

         for tile in TileProduct.objects.filter(
        material__icontains="Porcelain"
    ):
          tile.countries.add(china)

         for tile in TileProduct.objects.filter(
        effects__name__icontains="Concrete"
    ).distinct():
          tile.countries.add(spain)