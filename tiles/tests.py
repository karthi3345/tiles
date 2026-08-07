import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from tiles.models import City, Country, State, TileCategory, TileProduct, Order, OrderItem, Payment
from tiles.views import _haversine_distance
from tiles.cart import Cart


class HaversineDistanceTest(TestCase):
    """Unit tests for the Haversine distance calculation."""

    def test_known_distance_london_to_paris(self):
        # London → Paris ≈ 343 km
        dist = _haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertAlmostEqual(dist, 343, delta=5)

    def test_zero_distance_same_point(self):
        dist = _haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
        self.assertAlmostEqual(dist, 0.0, places=3)

    def test_antipode_distance(self):
        # Distance from a point to its antipode should be ~half Earth circumference
        lat, lng = 10.0, 20.0
        dist = _haversine_distance(lat, lng, -lat, lng + 180)
        self.assertAlmostEqual(dist, 20015, delta=100)

    def test_short_distance(self):
        # Two points ~1 km apart
        dist = _haversine_distance(12.9716, 77.5946, 12.9750, 77.6050)
        self.assertLess(dist, 2.0)
        self.assertGreater(dist, 0.5)


class FindNearestLocationAPITest(TestCase):
    """Integration tests for the /api/find-nearest/ endpoint."""

    def setUp(self):
        self.client = Client()
        # Create minimal location hierarchy
        self.country = Country.objects.create(
            name='TestCountry', slug='test-country',
            flag_emoji='🏳', continent='TestLand',
        )
        self.state = State.objects.create(
            country=self.country, name='TestState', slug='test-state',
        )
        self.city_a = City.objects.create(
            state=self.state, name='CityA', slug='city-a',
            latitude=10.0, longitude=10.0,
        )
        self.city_b = City.objects.create(
            state=self.state, name='CityB', slug='city-b',
            latitude=20.0, longitude=20.0,
        )
        self.city_c = City.objects.create(
            state=self.state, name='CityC', slug='city-c',
            latitude=30.0, longitude=30.0,
        )

    def test_finds_nearest_city(self):
        """Coords near CityA should return CityA."""
        resp = self.client.get('/api/find-nearest/?lat=10.5&lng=10.5')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['found'])
        self.assertEqual(data['city'], 'CityA')
        self.assertEqual(data['redirect_url'], '/locations/test-country/test-state/city-a/')

    def test_finds_correct_nearest_for_different_coords(self):
        """Coords near CityC should return CityC."""
        resp = self.client.get('/api/find-nearest/?lat=29.5&lng=29.8')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['found'])
        self.assertEqual(data['city'], 'CityC')

    def test_missing_params_returns_400(self):
        """Missing lat/lng should return 400 with found=false."""
        resp = self.client.get('/api/find-nearest/?lat=&lng=')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data['found'])
        self.assertIn('required', data['error'].lower())

    def test_invalid_params_returns_400(self):
        """Non-numeric lat/lng should return 400."""
        resp = self.client.get('/api/find-nearest/?lat=abc&lng=xyz')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data['found'])

    def test_out_of_range_coords_returns_400(self):
        """Latitude > 90 should return 400."""
        resp = self.client.get('/api/find-nearest/?lat=91&lng=0')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data['found'])

    def test_no_params_returns_400(self):
        """No query params at all should return 400."""
        resp = self.client.get('/api/find-nearest/')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data['found'])

    def test_response_includes_distance(self):
        """Response should include a distance_km field."""
        resp = self.client.get('/api/find-nearest/?lat=10.0&lng=10.0')
        data = resp.json()
        self.assertIn('distance_km', data)
        self.assertEqual(data['distance_km'], 0.0)

    def test_response_includes_location_hierarchy(self):
        """Response should include city, state, country names and slugs."""
        resp = self.client.get('/api/find-nearest/?lat=10.0&lng=10.0')
        data = resp.json()
        self.assertEqual(data['city'], 'CityA')
        self.assertEqual(data['state'], 'TestState')
        self.assertEqual(data['country'], 'TestCountry')
        self.assertEqual(data['country_slug'], 'test-country')
        self.assertEqual(data['state_slug'], 'test-state')
        self.assertEqual(data['city_slug'], 'city-a')


# ─────────── CART UNIT TESTS ───────────


class CartTest(TestCase):
    """Unit tests for the session-based Cart helper."""

    def setUp(self):
        self.factory = RequestFactory()
        self.category = TileCategory.objects.create(name='Floor Tiles', slug='floor-tiles')
        self.tile1 = TileProduct.objects.create(
            name='Tile A', slug='tile-a',
            category=self.category, price_range_min=Decimal('100.00'),
        )
        self.tile2 = TileProduct.objects.create(
            name='Tile B', slug='tile-b',
            category=self.category, price_range_min=Decimal('250.00'),
        )

    def _get_cart(self):
        """Helper: create a fresh request + Cart."""
        request = self.factory.get('/')
        request.session = self.client.session
        return Cart(request)

    def test_add_item(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=2)
        self.assertEqual(len(cart), 2)  # 2 units
        self.assertEqual(cart.get_distinct_count(), 1)

    def test_add_same_item_increases_quantity(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=1)
        cart.add(tile_id=self.tile1.id, quantity=3)
        self.assertEqual(len(cart), 4)

    def test_add_different_items(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=2)
        cart.add(tile_id=self.tile2.id, quantity=1)
        self.assertEqual(cart.get_distinct_count(), 2)
        self.assertEqual(len(cart), 3)

    def test_remove_item(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=2)
        cart.add(tile_id=self.tile2.id, quantity=1)
        cart.remove(tile_id=self.tile1.id)
        self.assertEqual(cart.get_distinct_count(), 1)
        self.assertEqual(len(cart), 1)

    def test_update_quantity(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=2)
        cart.update_quantity(tile_id=self.tile1.id, quantity=5)
        self.assertEqual(len(cart), 5)

    def test_update_quantity_to_zero_removes_item(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=2)
        cart.update_quantity(tile_id=self.tile1.id, quantity=0)
        self.assertEqual(cart.get_distinct_count(), 0)
        self.assertEqual(len(cart), 0)

    def test_total_price(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=2)   # 2 × 100 = 200
        cart.add(tile_id=self.tile2.id, quantity=1)   # 1 × 250 = 250
        self.assertEqual(cart.get_total_price(), Decimal('450.00'))

    def test_clear_cart(self):
        cart = self._get_cart()
        cart.add(tile_id=self.tile1.id, quantity=3)
        cart.clear()
        self.assertEqual(len(cart), 0)
        self.assertEqual(cart.get_distinct_count(), 0)

    def test_empty_cart_total(self):
        cart = self._get_cart()
        self.assertEqual(cart.get_total_price(), Decimal('0'))


# ─────────── CART VIEW INTEGRATION TESTS ───────────


class CartViewTest(TestCase):
    """Integration tests for cart add/update/remove views."""

    def setUp(self):
        self.client = Client()
        self.category = TileCategory.objects.create(name='Floor Tiles', slug='floor-tiles')
        self.tile = TileProduct.objects.create(
            name='Premium Tile', slug='premium-tile',
            category=self.category, price_range_min=Decimal('500.00'),
        )

    def test_cart_detail_page_loads(self):
        resp = self.client.get('/cart/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Shopping Cart')

    def test_add_to_cart_via_post(self):
        resp = self.client.post(f'/cart/add/{self.tile.id}/', {
            'quantity': 2,
        }, follow=False)
        # Should redirect (302)
        self.assertEqual(resp.status_code, 302)
        # Check cart in session
        session = self.client.session
        cart = session.get('cart', [])
        self.assertEqual(len(cart), 1)
        self.assertEqual(cart[0]['tile_id'], self.tile.id)
        self.assertEqual(cart[0]['quantity'], 2)

    def test_add_to_cart_buy_now_redirects_to_checkout(self):
        resp = self.client.post(f'/cart/add/{self.tile.id}/', {
            'quantity': 1,
            'buy_now': '1',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/checkout/', resp.url)

    def test_remove_from_cart(self):
        self.client.post(f'/cart/add/{self.tile.id}/', {'quantity': 1})
        resp = self.client.post(f'/cart/remove/{self.tile.id}/')
        self.assertEqual(resp.status_code, 302)
        session = self.client.session
        self.assertEqual(len(session.get('cart', [])), 0)

    def test_update_cart_quantity(self):
        self.client.post(f'/cart/add/{self.tile.id}/', {'quantity': 1})
        self.client.post(f'/cart/update/{self.tile.id}/', {'quantity': 5})
        session = self.client.session
        self.assertEqual(session['cart'][0]['quantity'], 5)


# ─────────── ORDER & PAYMENT MODEL TESTS ───────────


class OrderModelTest(TestCase):
    """Unit tests for Order / OrderItem / Payment models."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@test.com'
        )
        self.category = TileCategory.objects.create(name='Wall Tiles', slug='wall-tiles')
        self.tile = TileProduct.objects.create(
            name='Marble Tile', slug='marble-tile',
            category=self.category, price_range_min=Decimal('300.00'),
        )

    def test_create_order(self):
        order = Order.objects.create(
            user=self.user,
            order_id='order_test123',
            amount=Decimal('600.00'),
            status='paid',
            customer_name='Test User',
            customer_email='test@test.com',
        )
        self.assertEqual(str(order), 'Order order_test123 — paid')
        self.assertEqual(order.total_items, 0)

    def test_create_order_with_items(self):
        order = Order.objects.create(
            user=self.user,
            order_id='order_test456',
            amount=Decimal('900.00'),
            status='paid',
        )
        OrderItem.objects.create(
            order=order, tile=self.tile,
            tile_name='Marble Tile', quantity=3,
            price=Decimal('300.00'),
        )
        self.assertEqual(order.total_items, 3)
        self.assertEqual(order.items.first().total, Decimal('900.00'))

    def test_create_payment(self):
        order = Order.objects.create(
            user=self.user, order_id='order_test789',
            amount=Decimal('500.00'), status='paid',
        )
        payment = Payment.objects.create(
            order=order,
            razorpay_payment_id='pay_test123',
            razorpay_signature='sig_test123',
            amount=Decimal('500.00'),
            status='success',
        )
        self.assertEqual(str(payment), 'Payment pay_test123 — success')


# ─────────── CHECKOUT FLOW TESTS ───────────


class CheckoutFlowTest(TestCase):
    """Integration tests for the checkout → payment flow with mocked Razorpay."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer', password='testpass123',
            email='buyer@test.com'
        )
        self.category = TileCategory.objects.create(name='Ceramic', slug='ceramic')
        self.tile = TileProduct.objects.create(
            name='Ceramic White', slug='ceramic-white',
            category=self.category, price_range_min=Decimal('150.00'),
        )
        self.client.login(username='buyer', password='testpass123')

    def test_checkout_empty_cart_redirects(self):
        resp = self.client.get('/checkout/')
        self.assertEqual(resp.status_code, 302)

    def test_checkout_page_loads_with_cart(self):
        self.client.post(f'/cart/add/{self.tile.id}/', {'quantity': 2})
        resp = self.client.get('/checkout/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Checkout')

    @patch('tiles.views.create_razorpay_order')
    def test_checkout_creates_razorpay_order(self, mock_create):
        mock_create.return_value = {
            'id': 'order_mock123',
            'amount': 30000,
            'currency': 'INR',
        }
        self.client.post(f'/cart/add/{self.tile.id}/', {'quantity': 2})
        resp = self.client.post('/checkout/', {
            'customer_name': 'Buyer Name',
            'customer_email': 'buyer@test.com',
            'customer_phone': '9876543210',
            'shipping_address': '123 Main St, City, State - 560001',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'order_mock123')
        self.assertContains(resp, 'rzp-button')

    @patch('tiles.views.verify_payment_signature')
    def test_payment_verify_success(self, mock_verify):
        mock_verify.return_value = True
        # Add item to cart
        self.client.post(f'/cart/add/{self.tile.id}/', {'quantity': 2})

        # Simulate checkout to populate session
        session = self.client.session
        session['checkout'] = {
            'order_id': 'order_mock456',
            'amount': '300.00',
            'customer_name': 'Buyer',
            'customer_email': 'buyer@test.com',
            'customer_phone': '9876543210',
            'shipping_address': '123 Main St',
        }
        session.save()

        resp = self.client.post('/payment/verify/', {
            'razorpay_payment_id': 'pay_mock789',
            'razorpay_order_id': 'order_mock456',
            'razorpay_signature': 'valid_signature',
        })

        # Should redirect to success page
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/payment/success/', resp.url)

        # Verify order was created
        order = Order.objects.get(order_id='order_mock456')
        self.assertEqual(order.status, 'paid')
        self.assertEqual(order.total_items, 2)

        # Verify payment record
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.status, 'success')
        self.assertEqual(payment.razorpay_payment_id, 'pay_mock789')

    @patch('tiles.views.verify_payment_signature')
    def test_payment_verify_failure(self, mock_verify):
        mock_verify.side_effect = Exception('Signature mismatch')

        self.client.post(f'/cart/add/{self.tile.id}/', {'quantity': 1})
        session = self.client.session
        session['checkout'] = {
            'order_id': 'order_fail001',
            'amount': '150.00',
            'customer_name': 'Buyer',
            'customer_email': 'buyer@test.com',
            'customer_phone': '9876543210',
            'shipping_address': '123 Main St',
        }
        session.save()

        resp = self.client.post('/payment/verify/', {
            'razorpay_payment_id': 'pay_fail001',
            'razorpay_order_id': 'order_fail001',
            'razorpay_signature': 'bad_signature',
        })

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/payment/failed/', resp.url)

        order = Order.objects.get(order_id='order_fail001')
        self.assertEqual(order.status, 'failed')

    def test_order_history_requires_login(self):
        self.client.logout()
        resp = self.client.get('/orders/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp.url)

    def test_order_history_shows_orders(self):
        Order.objects.create(
            user=self.user, order_id='order_hist001',
            amount=Decimal('500.00'), status='paid',
        )
        resp = self.client.get('/orders/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'order_hist001')
