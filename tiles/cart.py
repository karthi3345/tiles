"""
Session-based shopping cart helper.

Stores cart items in Django's session as a list of dicts:
    [{"tile_id": int, "quantity": int, "size_label": str}, ...]

No DB writes for the cart itself — only on order placement.
"""
from decimal import Decimal
from django.conf import settings
from .models import TileProduct, TileSize


CART_SESSION_KEY = 'cart'


class Cart:
    """Lightweight session-backed cart."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = []
        self.cart = cart

    # ── iteration ──────────────────────────────────────────────

    def __iter__(self):
        """
        Yield enriched dicts with live tile data.
        Each item gets: tile_id, quantity, size_label, tile (obj),
        price, total.

        IMPORTANT: yields a COPY so the original session-stored cart
        stays JSON-serializable (no model objects leak into the session).
        """
        tile_ids = [item['tile_id'] for item in self.cart]
        tiles = TileProduct.objects.in_bulk(tile_ids)

        for item in self.cart:
            tile = tiles.get(item['tile_id'])
            if tile is None:
                continue
            price = tile.price_range_min if tile.price_range_min else Decimal('0')
            enriched = dict(item)
            enriched['tile'] = tile
            enriched['price'] = price
            enriched['total'] = price * item['quantity']
            yield enriched

    def __len__(self):
        """Total number of individual units (not distinct products)."""
        return sum(item['quantity'] for item in self.cart)

    # ── mutations ──────────────────────────────────────────────

    def add(self, tile_id, quantity=1, size_label='', override_quantity=False):
        """Add a tile to the cart or increase its quantity."""
        tile_id = int(tile_id)
        for item in self.cart:
            if item['tile_id'] == tile_id and item.get('size_label', '') == size_label:
                if override_quantity:
                    item['quantity'] = quantity
                else:
                    item['quantity'] += quantity
                self._save()
                return
        self.cart.append({
            'tile_id': tile_id,
            'quantity': quantity,
            'size_label': size_label,
        })
        self._save()

    def remove(self, tile_id, size_label=''):
        """Remove a tile from the cart."""
        tile_id = int(tile_id)
        self.cart = [
            item for item in self.cart
            if not (item['tile_id'] == tile_id and item.get('size_label', '') == size_label)
        ]
        self._save()

    def update_quantity(self, tile_id, quantity, size_label=''):
        """Set the exact quantity for a cart item. Removes if quantity <= 0."""
        tile_id = int(tile_id)
        if quantity <= 0:
            self.remove(tile_id, size_label)
            return
        for item in self.cart:
            if item['tile_id'] == tile_id and item.get('size_label', '') == size_label:
                item['quantity'] = quantity
                self._save()
                return

    def clear(self):
        """Empty the cart."""
        self.session[CART_SESSION_KEY] = []
        self.cart = []
        self._save()

    # ── totals ─────────────────────────────────────────────────

    def get_total_price(self):
        """Return Decimal sum of all line totals."""
        total = Decimal('0')
        tile_ids = [item['tile_id'] for item in self.cart]
        tiles = TileProduct.objects.in_bulk(tile_ids)
        for item in self.cart:
            tile = tiles.get(item['tile_id'])
            if tile:
                price = tile.price_range_min if tile.price_range_min else Decimal('0')
                total += price * item['quantity']
        return total

    def get_distinct_count(self):
        """Number of distinct tile products in cart."""
        return len(self.cart)

    def _save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True
