import json
import uuid
import time
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import cloudinary.uploader


from .models import (
    Country, State, City, Village,
    TileCategory, TileEffect, TileFinish, TileSize, TileProduct,
    MarketInsight, ChatSession, ChatMessage, GeneratedImage,Notification,
    Order, OrderItem, Payment,
)
from .forms import ChatForm, ImageGenerateForm, TileSearchForm
from .cart import Cart
from .payment import create_razorpay_order, verify_payment_signature, get_razorpay_client
from .services.ai_chat import chat_service
from .services.image_gen import image_gen_service


def _build_breadcrumbs(items):
    return items


def _get_tiles_for_country(country):
    qs = TileProduct.objects.filter(
        countries=country, is_active=True
    ).select_related('category').prefetch_related('effects', 'finishes', 'sizes')
    if not qs.exists():
        qs = TileProduct.objects.filter(is_active=True).select_related('category').prefetch_related('effects', 'finishes', 'sizes')
    return qs


def _build_tile_prompt(tile):
    parts = []
    effects = [e.name.lower() for e in tile.effects.all()[:3]]
    if effects:
        parts.append(', '.join(effects))
    if tile.material:
        parts.append(tile.material.lower())
    finishes = [f.name.lower() for f in tile.finishes.all()[:2]]
    if finishes:
        parts.append(', '.join(finishes))
    sizes = list(tile.sizes.all()[:1])
    if sizes:
        s = sizes[0]
        parts.append(f'{s.width_mm}x{s.height_mm}mm')
    if tile.category:
        parts.append(tile.category.name.lower())
    return ' '.join(parts)


def upload_to_cloudinary(image_file):
    print("UPLOAD FILE:", image_file)
    print("FILE NAME:", image_file.name if hasattr(image_file, 'name') else 'In-Memory File')

    result = cloudinary.uploader.upload(
        image_file,
        folder="tiles/generated",
        resource_type="image"
    )

    print("CLOUDINARY RESULT:")
    print(result)

    return result["secure_url"]


# ─────────── HOME ───────────

def home(request):
    countries = Country.objects.all()[:10]
    categories = TileCategory.objects.all()
    total_tiles = TileProduct.objects.filter(is_active=True).count()
    total_locations = Village.objects.count() + City.objects.count() + State.objects.count()
    return render(request, 'tiles/home.html', {
        'countries': countries,
        'categories': categories,
        'total_tiles': total_tiles,
        'total_locations': total_locations,
        'total_countries': countries.count(),
    })


# ─────────── LOCATION BROWSING ───────────

def countries_list(request):
    countries = Country.objects.all().annotate(state_count=Count('states'))
    breadcrumbs = _build_breadcrumbs([('All Countries', None)])
    return render(request, 'tiles/locations/countries.html', {
        'countries': countries, 'breadcrumbs': breadcrumbs,
    })


def states_list(request, country_slug):
    country = get_object_or_404(Country, slug=country_slug)
    states = country.states.all().annotate(annotated_city_count=Count('cities'))
    tiles = _get_tiles_for_country(country)[:12]
    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, None),
    ])
    return render(request, 'tiles/locations/states.html', {
        'country': country, 'states': states, 'tiles': tiles, 'breadcrumbs': breadcrumbs,
    })


def cities_list(request, country_slug, state_slug):
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    cities = state.cities.all().annotate(annotated_village_count=Count('villages'))
    tiles = _get_tiles_for_country(country)[:12]
    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, f'/locations/{country.slug}/'),
        (state.name, None),
    ])
    return render(request, 'tiles/locations/cities.html', {
        'country': country, 'state': state, 'cities': cities,
        'tiles': tiles, 'breadcrumbs': breadcrumbs,
    })


def villages_list(request, country_slug, state_slug, city_slug):
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    city = get_object_or_404(City, slug=city_slug, state=state)
    villages = city.villages.all()
    tiles = _get_tiles_for_country(country)
    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, f'/locations/{country.slug}/'),
        (state.name, f'/locations/{country.slug}/{state.slug}/'),
        (city.name, None),
    ])
    return render(request, 'tiles/locations/villages.html', {
        'country': country, 'state': state, 'city': city,
        'villages': villages, 'tiles': tiles, 'village': None,
        'showrooms': [], 'breadcrumbs': breadcrumbs,
    })


def village_tiles(request, country_slug, state_slug, city_slug, village_slug):
    country = get_object_or_404(Country, slug=country_slug)
    state = get_object_or_404(State, slug=state_slug, country=country)
    city = get_object_or_404(City, slug=city_slug, state=state)
    village = get_object_or_404(Village, slug=village_slug, city=city)

    tiles = _get_tiles_for_country(country)
    showrooms = village.showrooms.filter(is_active=True)

    breadcrumbs = _build_breadcrumbs([
        ('All Countries', '/locations/'),
        (country.name, None),
        (state.name, None),
        (city.name, None),
        (village.name, None),
    ])

    return render(
        request,
        'tiles/locations/villages.html',
        {
            'country': country,
            'state': state,
            'city': city,
            'village': village,
            'villages': [],
            'tiles': tiles,
            'showrooms': showrooms,
            'breadcrumbs': breadcrumbs,
        }
    )


# ─────────── TILE CATALOG ───────────

def tile_catalog(request):
    form = TileSearchForm(request.GET or None)

    tiles = TileProduct.objects.filter(
        is_active=True
    ).select_related(
        'category'
    ).prefetch_related(
        'effects',
        'finishes',
        'sizes',
        'countries'
    )

    query = request.GET.get('q', '').strip()
    cat_slug = request.GET.get('category', '')
    tile_type = request.GET.get('tile_type', '')
    country_slug = request.GET.get('country', '')
    usage_type = request.GET.get('usage_type', '')

    if usage_type:
        tiles = tiles.filter(category__usage_type=usage_type)

    if query:
       tiles = tiles.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(material__icontains=query) |
        Q(category__name__icontains=query) |
        Q(effects__name__icontains=query) |
        Q(finishes__name__icontains=query)
    ).distinct()
    if cat_slug:
        tiles = tiles.filter(category__slug=cat_slug)

    if tile_type:
        tiles = tiles.filter(category__tile_type=tile_type)

    if country_slug:
        tiles = tiles.filter(countries__slug=country_slug).distinct()

    breadcrumbs = _build_breadcrumbs([
        ('Tile Catalog', None)
    ])

    return render(
        request,
        'tiles/tiles/catalog.html',
        {
            'tiles': tiles,
            'form': form,
            'query': query,
            'total': tiles.count(),
            'breadcrumbs': breadcrumbs,
        }
    )
def tile_detail(request, slug):
    tile = get_object_or_404(TileProduct, slug=slug, is_active=True)
    related = TileProduct.objects.filter(
        category=tile.category, is_active=True
    ).exclude(pk=tile.pk)[:8]
    breadcrumbs = _build_breadcrumbs([
        ('Tile Catalog', '/tiles/'),
        (tile.name, None),
    ])
    return render(request, 'tiles/tiles/detail.html', {
        'tile': tile, 'related': related, 'breadcrumbs': breadcrumbs,
    })


# ─────────── TILE IMAGE GENERATION ───────────

@login_required
def generate_single_tile_image(request, slug):
    tile = get_object_or_404(TileProduct, slug=slug, is_active=True)

    if not image_gen_service.is_configured():
        messages.error(request, 'Cloudflare AI not configured. Set CF_ACCOUNT_ID and CF_API_TOKEN in .env')
        return redirect('tiles:tile_detail', slug=slug)

    prompt = _build_tile_prompt(tile)
    result = image_gen_service.generate(prompt)

    if result['success'] and result['image_file']:
        # Upload to Cloudinary and get the URL
        image_url = upload_to_cloudinary(result['image_file'])

        # Save the Cloudinary URL to the database
        tile.image = image_url
        tile.save(update_fields=['image'])

        messages.success(request, f'Design generated for {tile.name}!')
    else:
        messages.error(
            request,
            result.get('error', 'Generation failed. Check Cloudflare credentials.')
        )

    # CRITICAL: Must redirect back to the page at the end
    return redirect('tiles:tile_detail', slug=slug)


@login_required
def generate_all_tile_images(request):
    if not image_gen_service.is_configured():
        messages.error(request, 'Cloudflare AI not configured. Set CF_ACCOUNT_ID and CF_API_TOKEN in .env')
        return redirect('tiles:tile_catalog')

    if request.method == 'POST':
        products = TileProduct.objects.filter(is_active=True)

        if request.POST.get('category'):
            products = products.filter(category__slug=request.POST.get('category'))
        if request.POST.get('force') != 'on':
            products = products.filter(image__isnull=True)

        limit = int(request.POST.get('limit', 0))
        if limit > 0:
            products = products[:limit]

        total = products.count()
        if total == 0:
            messages.info(request, 'No tiles need generation.')
            return redirect('tiles:generate_all_images')

        generated = 0
        failed = 0
        for tile in products:
            prompt = _build_tile_prompt(tile)
            result = image_gen_service.generate(prompt)
            
            if result['success'] and result['image_file']:
                # Upload to Cloudinary instead of saving locally
                image_url = upload_to_cloudinary(result['image_file'])
                
                # Save the URL
                tile.image = image_url
                tile.save(update_fields=['image'])
                generated += 1
            else:
                failed += 1
            time.sleep(1)

        messages.success(request, f'Generated {generated} designs, {failed} failed (of {total} total)')
        return redirect('tiles:generate_all_images')

    categories = TileCategory.objects.all()
    missing_count = TileProduct.objects.filter(is_active=True, image__isnull=True).count()
    total = TileProduct.objects.filter(is_active=True).count()
    with_image = total - missing_count
    tiles_without_images = TileProduct.objects.filter(is_active=True, image__isnull=True)[:30]

    breadcrumbs = _build_breadcrumbs([
        ('Tile Catalog', '/tiles/'),
        ('Generate Designs', None),
    ])
    return render(request, 'tiles/tiles/generate_designs.html', {
        'categories': categories,
        'missing': missing_count,
        'total': total,
        'with_image': with_image,
        'tiles_without_images': tiles_without_images,
        'breadcrumbs': breadcrumbs,
    })


# ─────────── AI CHAT ───────────

@csrf_exempt
@login_required(login_url='accounts:login')
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
        except json.JSONDecodeError:
            data = request.POST
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(session_id=session_id, title=message[:100])
        else:
            session, _ = ChatSession.objects.get_or_create(session_id=session_id)
            if not session.title:
                session.title = message[:100]
                session.save()

        ChatMessage.objects.create(session=session, role='user', content=message)

        chat_history_qs = list(session.messages.all()[:11])
        history = [
            {"role": m.role, "content": m.content}
            for m in chat_history_qs[:-1]
        ]

        result = chat_service.chat(message, history)
        print("=" * 60)
        print("CHAT RESULT")
        print(result)
        print("=" * 60)

        if result["success"]:
            response = result.get("response")
            if not response:
                response = "Sorry, AI returned an empty response."

            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=response
            )

            return JsonResponse({
                "success": True,
                "response": response,
                "session_id": session_id
            })
        else:
            error_msg = result.get("error", "Sorry, something went wrong while generating a response.")
            return JsonResponse({
                "success": False,
                "error": error_msg,
                "session_id": session_id
            }, status=502)

    breadcrumbs = _build_breadcrumbs([('AI Chat', None)])
    return render(request, 'tiles/chat.html', {'form': ChatForm(), 'breadcrumbs': breadcrumbs})


# ─────────── IMAGE GENERATION ───────────

@login_required(login_url='accounts:login')
def generate_image_view(request):
    images = GeneratedImage.objects.filter(user=request.user)
    form = ImageGenerateForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            prompt = form.cleaned_data.get('prompt')
            style = form.cleaned_data.get('style', 'realistic')

            result = image_gen_service.generate(prompt, style)

            if result['success'] and result.get('image_file'):
                # Upload to Cloudinary
                image_url = upload_to_cloudinary(result['image_file'])

                # Save URL to database
                GeneratedImage.objects.create(
                    user=request.user,
                    prompt=f"[{style}] {prompt}",
                    image=image_url,
                    model_used=image_gen_service.model,
                )

                messages.success(request, 'Tile design generated successfully!')
                return redirect('tiles:generate_image')
            else:
                messages.error(request, result.get('error', 'Generation failed'))

    breadcrumbs = _build_breadcrumbs([('Generate Image', None)])

    return render(
        request,
        'tiles/generate_image.html',
        {
            'form': form,
            'generated_images': images,
            'breadcrumbs': breadcrumbs,
        }
    )


# ─────────── LOCATION SEARCH API ───────────

def location_search(request):
    q = request.GET.get('q', '')
    if not q or len(q) < 2:
        return JsonResponse({'results': []})
    results = []
    for v in Village.objects.filter(name__icontains=q)[:8]:
        results.append({
            'type': 'village', 'name': v.name,
            'path': f"/locations/{v.country.slug}/{v.state.slug}/{v.city.slug}/{v.slug}/",
            'parent': f"{v.city.name}, {v.state.name}, {v.country.flag_emoji} {v.country.name}"
        })
    for c in City.objects.filter(name__icontains=q)[:8]:
        results.append({
            'type': 'city', 'name': c.name,
            'path': f"/locations/{c.country.slug}/{c.state.slug}/{c.slug}/",
            'parent': f"{c.state.name}, {c.country.flag_emoji} {c.country.name}"
        })
    for s in State.objects.filter(name__icontains=q)[:5]:
        results.append({
            'type': 'state', 'name': s.name,
            'path': f"/locations/{s.country.slug}/{s.slug}/",
            'parent': f"{s.country.flag_emoji} {s.country.name}"
        })
    return JsonResponse({'results': results})


# ─────────── NEAREST LOCATION API ───────────

def _haversine_distance(lat1, lng1, lat2, lng2):
    """Return the great-circle distance between two points in km (Haversine formula)."""
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_location(request):
    """GET ?lat=X&lng=Y → nearest city with coordinates, or found=false."""
    try:
        lat = float(request.GET.get('lat', ''))
        lng = float(request.GET.get('lng', ''))
    except (ValueError, TypeError):
        return JsonResponse(
            {'found': False, 'error': 'Valid lat and lng parameters are required.'},
            status=400,
        )

    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return JsonResponse(
            {'found': False, 'error': 'Coordinates out of valid range.'},
            status=400,
        )

    cities = City.objects.select_related('state__country').exclude(
        latitude__isnull=True, longitude__isnull=True
    )

    if not cities.exists():
        return JsonResponse(
            {'found': False, 'error': 'No cities with coordinates available.'},
            status=404,
        )

    nearest = None
    nearest_dist = None
    for city in cities:
        dist = _haversine_distance(lat, lng, city.latitude, city.longitude)
        if nearest_dist is None or dist < nearest_dist:
            nearest = city
            nearest_dist = dist

    if nearest is None:
        return JsonResponse({'found': False, 'error': 'No nearby city found.'}, status=404)

    redirect_url = (
        f'/locations/{nearest.state.country.slug}/'
        f'{nearest.state.slug}/{nearest.slug}/'
    )

    return JsonResponse({
        'found': True,
        'city': nearest.name,
        'state': nearest.state.name,
        'country': nearest.state.country.name,
        'country_slug': nearest.state.country.slug,
        'state_slug': nearest.state.slug,
        'city_slug': nearest.slug,
        'redirect_url': redirect_url,
        'distance_km': round(nearest_dist, 1),
    })


#-------------Download IMages----------------

from io import BytesIO

import requests
from PIL import Image

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def download_generated_image(request, pk):
    image = get_object_or_404(
        GeneratedImage,
        id=pk,
        user=request.user
    )

    response = requests.get(image.image)

    if response.status_code != 200:
        return HttpResponse("Image not found.", status=404)

    # Settings from modal
    width = int(request.GET.get("width", 1200))
    height = int(request.GET.get("height", 1200))
    dpi = int(request.GET.get("dpi", 300))
    fmt = request.GET.get("format", "png").lower()
    quality = int(request.GET.get("quality", 100))
    filename = request.GET.get("filename", f"tile-{pk}")

    # Open image
    img = Image.open(BytesIO(response.content)).convert("RGB")

    # Resize
    img = img.resize((width, height), Image.LANCZOS)

    output = BytesIO()

    if fmt == "jpg":
        img.save(
            output,
            format="JPEG",
            quality=quality,
            dpi=(dpi, dpi),
            optimize=True,
        )
        content_type = "image/jpeg"
        extension = "jpg"

    elif fmt == "webp":
        img.save(
            output,
            format="WEBP",
            quality=quality,
            method=6,
        )
        content_type = "image/webp"
        extension = "webp"

    else:
        img.save(
            output,
            format="PNG",
            dpi=(dpi, dpi),
        )
        content_type = "image/png"
        extension = "png"

    output.seek(0)

    download = HttpResponse(output.getvalue(), content_type=content_type)
    download["Content-Disposition"] = (
        f'attachment; filename="{filename}.{extension}"'
    )

    return download

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

# ─────────── NOTIFICATIONS ───────────

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'tiles/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['unread_count'] = Notification.objects.filter(
            user=self.request.user, is_read=False
        ).count()
        return ctx


@require_POST
def mark_all_notifications_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ─────────── SHOPPING CART ───────────

def cart_detail(request):
    """View the shopping cart page."""
    cart = Cart(request)
    breadcrumbs = _build_breadcrumbs([
        ('Home', '/'),
        ('Cart', None),
    ])
    return render(request, 'tiles/cart/cart.html', {
        'cart': cart,
        'breadcrumbs': breadcrumbs,
    })


@require_POST
def cart_add(request, tile_id):
    """Add a tile to the cart. Accepts quantity and optional size_label."""
    tile = get_object_or_404(TileProduct, id=tile_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    size_label = request.POST.get('size_label', '')

    cart = Cart(request)
    cart.add(tile_id=tile.id, quantity=quantity, size_label=size_label)

    messages.success(request, f'Added "{tile.name}" to cart.')

    # If 'buy_now' is set, redirect to checkout
    if request.POST.get('buy_now'):
        return redirect('tiles:checkout')

    return redirect(request.META.get('HTTP_REFERER', 'tiles:cart_detail'))


@require_POST
def cart_update(request, tile_id):
    """Update quantity of a cart item."""
    quantity = int(request.POST.get('quantity', 1))
    size_label = request.POST.get('size_label', '')
    cart = Cart(request)
    cart.update_quantity(tile_id=tile_id, quantity=quantity, size_label=size_label)
    messages.success(request, 'Cart updated.')
    return redirect('tiles:cart_detail')


@require_POST
def cart_remove(request, tile_id):
    """Remove a tile from the cart."""
    size_label = request.POST.get('size_label', '')
    cart = Cart(request)
    cart.remove(tile_id=tile_id, size_label=size_label)
    messages.success(request, 'Item removed from cart.')
    return redirect('tiles:cart_detail')


# ─────────── CHECKOUT & PAYMENT ───────────

@login_required(login_url='accounts:login')
def checkout(request):
    """
    Checkout page: shows cart summary, collects shipping info,
    and triggers Razorpay Checkout.js.
    """
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('tiles:tile_catalog')

    total = cart.get_total_price()

    # Pre-fill from user profile if available
    initial = {
        'customer_name': request.user.get_full_name() or request.user.username,
        'customer_email': request.user.email,
    }

    # Handle Razorpay order creation on POST
    razorpay_order = None
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()

        if not all([customer_name, customer_email, customer_phone, shipping_address]):
            messages.error(request, 'Please fill in all shipping details.')
        else:
            amount_paise = int(total * 100)  # ₹ → paise
            try:
                razorpay_order = create_razorpay_order(
                    amount_paise=amount_paise,
                    receipt=f'order_{request.user.id}_{int(time.time())}'
                )
                # Store shipping info + razorpay order id in session for verification step
                request.session['checkout'] = {
                    'order_id': razorpay_order['id'],
                    'amount': str(total),
                    'customer_name': customer_name,
                    'customer_email': customer_email,
                    'customer_phone': customer_phone,
                    'shipping_address': shipping_address,
                }
            except Exception as e:
                messages.error(request, f'Payment gateway error: {str(e)}')

    breadcrumbs = _build_breadcrumbs([
        ('Home', '/'),
        ('Cart', '/cart/'),
        ('Checkout', None),
    ])

    import os
    return render(request, 'tiles/cart/checkout.html', {
        'cart': cart,
        'total': total,
        'initial': initial,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': os.getenv('RAZORPAY_KEY_ID', ''),
        'breadcrumbs': breadcrumbs,
    })


@require_POST
@login_required(login_url='accounts:login')
def payment_verify(request):
    """
    Verify Razorpay payment after Checkout.js success callback.
    Creates Order, OrderItems, Payment records.
    """
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    checkout_data = request.session.get('checkout', {})

    if not checkout_data or checkout_data.get('order_id') != razorpay_order_id:
        messages.error(request, 'Session expired or invalid order. Please try again.')
        return redirect('tiles:cart_detail')

    # Verify signature
    try:
        verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        )
    except Exception:
        # Payment verification failed — record failure
        order = Order.objects.create(
            user=request.user,
            order_id=razorpay_order_id,
            amount=checkout_data.get('amount', 0),
            customer_name=checkout_data.get('customer_name', ''),
            customer_email=checkout_data.get('customer_email', ''),
            customer_phone=checkout_data.get('customer_phone', ''),
            shipping_address=checkout_data.get('shipping_address', ''),
            status='failed',
        )
        Payment.objects.create(
            order=order,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            amount=order.amount,
            status='failed',
        )
        return redirect('tiles:payment_failed')

    # Signature verified — save order
    from decimal import Decimal
    cart = Cart(request)

    order = Order.objects.create(
        user=request.user,
        order_id=razorpay_order_id,
        amount=Decimal(checkout_data.get('amount', 0)),
        customer_name=checkout_data.get('customer_name', ''),
        customer_email=checkout_data.get('customer_email', ''),
        customer_phone=checkout_data.get('customer_phone', ''),
        shipping_address=checkout_data.get('shipping_address', ''),
        status='paid',
    )

    # Create order items from cart
    for item in cart:
        OrderItem.objects.create(
            order=order,
            tile=item['tile'],
            tile_name=item['tile'].name,
            quantity=item['quantity'],
            price=item['price'],
            size_label=item.get('size_label', ''),
        )

    Payment.objects.create(
        order=order,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
        amount=order.amount,
        status='success',
    )

    # Clear cart + checkout session
    cart.clear()
    if 'checkout' in request.session:
        del request.session['checkout']

    request.session['last_order_id'] = order.id
    return redirect('tiles:payment_success')


def payment_success(request):
    """Payment success page."""
    order_id = request.session.pop('last_order_id', None)
    order = None
    if order_id:
        order = Order.objects.filter(id=order_id).first()
    return render(request, 'tiles/cart/payment_success.html', {'order': order})


def payment_failed(request):
    """Payment failure page."""
    return render(request, 'tiles/cart/payment_failed.html')


# ─────────── ORDER HISTORY ───────────

@login_required(login_url='accounts:login')
def order_history(request):
    """List all paid/failed orders for the current user."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    breadcrumbs = _build_breadcrumbs([
        ('Home', '/'),
        ('My Orders', None),
    ])
    return render(request, 'tiles/cart/orders.html', {
        'orders': orders,
        'breadcrumbs': breadcrumbs,
    })