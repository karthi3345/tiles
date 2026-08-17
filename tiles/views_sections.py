"""
In-dashboard section views for all models — replaces Django admin redirects.
Each view renders a purpose-built template under tiles/sections/.
Context shared by all: section, section_label, section_icon, section_desc,
page_obj, total (dict of counts for sidebar).
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from .models import (
    Country, State, City, Village,
    TileCategory, TileEffect, TileFinish, TileSize,
    TileProduct, TileShowroom, MarketInsight,
    ChatSession, ChatMessage, GeneratedImage,
    UserProfile, Notification, Order, OrderItem, Payment,
)
from django.contrib.auth.models import User


def _table_exists(table):
    from django.db import connection
    try:
        with connection.cursor() as cur:
            cur.execute(f'SELECT 1 FROM {table} LIMIT 1')
        return True
    except Exception:
        return False


def _total_counts():
    """Counts for the sidebar badges — safe against missing commerce tables."""
    counts = {
        'countries': Country.objects.count(),
        'states': State.objects.count(),
        'cities': City.objects.count(),
        'villages': Village.objects.count(),
        'products': TileProduct.objects.count(),
        'categories': TileCategory.objects.count(),
        'effects': TileEffect.objects.count(),
        'finishes': TileFinish.objects.count(),
        'sizes': TileSize.objects.count(),
        'showrooms': TileShowroom.objects.count(),
        'insights': MarketInsight.objects.count(),
        'chats': ChatSession.objects.count(),
        'messages': ChatMessage.objects.count(),
        'images': GeneratedImage.objects.count(),
        'users': User.objects.count(),
        'profiles': UserProfile.objects.count(),
        'notifications': Notification.objects.count(),
        'orders': 0,
        'order_items': 0,
        'payments': 0,
    }
    if _table_exists('tiles_order'):
        counts['orders'] = Order.objects.count()
        counts['order_items'] = OrderItem.objects.count()
    if _table_exists('tiles_payment'):
        counts['payments'] = Payment.objects.count()
    return counts


def _paginate(request, qs, per_page=25):
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1
    return Paginator(qs, per_page).get_page(page_num)


def _base_ctx(section, label, icon, desc, page_obj):
    return {
        'section': section,
        'section_label': label,
        'section_icon': icon,
        'section_desc': desc,
        'page_obj': page_obj,
        'total': _total_counts(),
    }


# ───────────────────────── Locations ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def section_countries(request):
    qs = Country.objects.annotate(
        pc=Count('tile_products'),
        sc=Count('states', distinct=True),
    ).order_by('ranking')
    return render(request, 'tiles/sections/countries.html',
                  _base_ctx('countries', 'Countries', 'fa-globe', 'Global tile markets', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_states(request):
    qs = State.objects.select_related('country').annotate(
        num_cities=Count('cities'),
    ).order_by('country__name', 'name')
    return render(request, 'tiles/sections/states.html',
                  _base_ctx('states', 'States', 'fa-map-location-dot', 'States / provinces', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_cities(request):
    qs = City.objects.select_related('state__country').order_by('state__country__name', 'name')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(state__name__icontains=q) | Q(state__country__name__icontains=q))
    return render(request, 'tiles/sections/cities.html',
                  _base_ctx('cities', 'Cities', 'fa-city', 'Cities with coordinates', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_villages(request):
    qs = Village.objects.select_related('city__state__country').annotate(
        showroom_count=Count('showrooms'),
    ).order_by('city__name', 'name')
    return render(request, 'tiles/sections/villages.html',
                  _base_ctx('villages', 'Areas / Villages', 'fa-map-pin', 'Local areas and villages', _paginate(request, qs)))


# ───────────────────────── Catalog ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def section_products(request):
    qs = TileProduct.objects.select_related('category').prefetch_related('sizes').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(material__icontains=q) | Q(category__name__icontains=q))
    ctx = _base_ctx('products', 'Products', 'fa-box', 'Tile product catalog', _paginate(request, qs))
    ctx['categories'] = TileCategory.objects.all().order_by('sort_order', 'name')
    return render(request, 'tiles/sections/products.html', ctx)


@staff_member_required(login_url='/admin/login/')
def section_categories(request):
    qs = TileCategory.objects.annotate(product_count=Count('products')).order_by('sort_order', 'name')
    return render(request, 'tiles/sections/categories.html',
                  _base_ctx('categories', 'Categories', 'fa-shapes', 'Product categories', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_effects(request):
    qs = TileEffect.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'tiles/sections/effects.html',
                  _base_ctx('effects', 'Effects', 'fa-wand-magic-sparkles', 'Tile visual effects', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_finishes(request):
    qs = TileFinish.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'tiles/sections/finishes.html',
                  _base_ctx('finishes', 'Finishes', 'fa-gem', 'Tile finishes', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_sizes(request):
    qs = TileSize.objects.annotate(product_count=Count('products')).order_by('width_mm', 'height_mm')
    return render(request, 'tiles/sections/sizes.html',
                  _base_ctx('sizes', 'Sizes', 'fa-ruler-combined', 'Tile size options', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_showrooms(request):
    qs = TileShowroom.objects.select_related('village__city__state__country').annotate(
        product_count=Count('products'),
    ).order_by('name')
    return render(request, 'tiles/sections/showrooms.html',
                  _base_ctx('showrooms', 'Showrooms', 'fa-store', 'Physical store locations', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_insights(request):
    qs = MarketInsight.objects.select_related('country').order_by('-year', 'country__name')
    return render(request, 'tiles/sections/insights.html',
                  _base_ctx('insights', 'Market Insights', 'fa-chart-line', 'Country market intelligence', _paginate(request, qs)))


# ───────────────────────── AI ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def section_chats(request):
    qs = ChatSession.objects.annotate(message_count=Count('messages')).order_by('-updated_at')
    return render(request, 'tiles/sections/chats.html',
                  _base_ctx('chats', 'Chat Sessions', 'fa-comments', 'AI assistant conversations', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_messages(request):
    qs = ChatMessage.objects.select_related('session').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(content__icontains=q) | Q(session__title__icontains=q))
    return render(request, 'tiles/sections/messages.html',
                  _base_ctx('messages', 'Chat Messages', 'fa-message', 'Individual AI messages', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_images(request):
    qs = GeneratedImage.objects.select_related('user').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(prompt__icontains=q) | Q(user__email__icontains=q))
    return render(request, 'tiles/sections/images.html',
                  _base_ctx('images', 'Generated Images', 'fa-image', 'AI-generated tile designs', _paginate(request, qs)))


# ───────────────────────── People ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def section_users(request):
    qs = User.objects.select_related('user_profile').annotate(
        order_count=Count('orders', distinct=True),
        image_count=Count('generatedimage', distinct=True),
    ).order_by('-date_joined')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(email__icontains=q) | Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    ctx = _base_ctx('users', 'Users', 'fa-users', 'Registered accounts', _paginate(request, qs))
    ctx['search'] = q
    return render(request, 'tiles/sections/users.html', ctx)


@staff_member_required(login_url='/admin/login/')
def section_profiles(request):
    qs = UserProfile.objects.select_related('user', 'country', 'city').order_by('user__email')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(user__email__icontains=q))
    return render(request, 'tiles/sections/profiles.html',
                  _base_ctx('profiles', 'User Profiles', 'fa-id-card', 'Extended profile data', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_notifications(request):
    qs = Notification.objects.select_related('user').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(message__icontains=q) | Q(notif_type__icontains=q) | Q(user__email__icontains=q))
    return render(request, 'tiles/sections/notifications.html',
                  _base_ctx('notifications', 'Notifications', 'fa-bell', 'User notifications', _paginate(request, qs)))


# ───────────────────────── Commerce ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def section_orders(request):
    if not _table_exists('tiles_order'):
        return render(request, 'tiles/sections/orders.html',
                      _base_ctx('orders', 'Orders', 'fa-cart-shopping', 'Customer orders', _paginate(request, Order.objects.none())))
    qs = Order.objects.select_related('user').prefetch_related('items__tile').annotate(
        item_count=Count('items'),
    ).order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(order_id__icontains=q) | Q(customer_name__icontains=q) | Q(customer_email__icontains=q))
    return render(request, 'tiles/sections/orders.html',
                  _base_ctx('orders', 'Orders', 'fa-cart-shopping', 'Customer orders', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_order_items(request):
    if not _table_exists('tiles_orderitem'):
        return render(request, 'tiles/sections/order_items.html',
                      _base_ctx('order-items', 'Order Items', 'fa-list-check', 'Line items in orders', _paginate(request, OrderItem.objects.none())))
    qs = OrderItem.objects.select_related('order', 'tile').order_by('-order__created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(tile_name__icontains=q) | Q(order__order_id__icontains=q))
    return render(request, 'tiles/sections/order_items.html',
                  _base_ctx('order-items', 'Order Items', 'fa-list-check', 'Line items in orders', _paginate(request, qs)))


@staff_member_required(login_url='/admin/login/')
def section_payments(request):
    if not _table_exists('tiles_payment'):
        return render(request, 'tiles/sections/payments.html',
                      _base_ctx('payments', 'Payments', 'fa-credit-card', 'Razorpay payments', _paginate(request, Payment.objects.none())))
    qs = Payment.objects.select_related('order__user').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(razorpay_payment_id__icontains=q) | Q(order__order_id__icontains=q))
    return render(request, 'tiles/sections/payments.html',
                  _base_ctx('payments', 'Payments', 'fa-credit-card', 'Razorpay payments', _paginate(request, qs)))


# ───────────────────────── Excel export ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def section_export(request, section):
    """Stream the section's data as an .xlsx download (honors ?q= filter)."""
    from . import export
    try:
        return export.export_response(section, request.GET.get('q', '').strip())
    except KeyError:
        from django.http import Http404
        raise Http404('Unknown section')


# ───────────────────────── Add Product (dynamic) ─────────────────────────

@staff_member_required(login_url='/admin/login/')
def product_add(request):
    """AJAX create a TileProduct. POST only, returns JSON."""
    import json
    from decimal import Decimal, InvalidOperation
    from django import forms
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST

    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)

    class ProductForm(forms.Form):
        name = forms.CharField(max_length=300, required=True)
        category = forms.ModelChoiceField(
            queryset=TileCategory.objects.all(), required=False)
        material = forms.CharField(max_length=100, required=False)
        price_min = forms.DecimalField(
            min_value=0, max_digits=8, decimal_places=2, required=True)
        price_max = forms.DecimalField(
            min_value=0, max_digits=8, decimal_places=2, required=True)
        description = forms.CharField(required=False)
        image = forms.URLField(required=False)
        is_featured = forms.BooleanField(required=False)
        is_active = forms.BooleanField(required=False)

    form = ProductForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    data = form.cleaned_data
    if data['price_max'] < data['price_min']:
        return JsonResponse({'ok': False, 'errors': {
            'price_max': ['Price max must be greater than or equal to price min.']
        }}, status=400)

    from django.utils.text import slugify
    base_slug = slugify(data['name']) or 'tile'
    slug = base_slug
    suffix = 2
    while TileProduct.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{suffix}'
        suffix += 1

    product = TileProduct.objects.create(
        name=data['name'],
        slug=slug,
        category=data['category'],
        material=data['material'] or '',
        price_range_min=data['price_min'],
        price_range_max=data['price_max'],
        description=data['description'] or '',
        image=data['image'] or None,
        is_featured=data['is_featured'],
        is_active=data['is_active'],
    )
    return JsonResponse({
        'ok': True, 'id': product.id, 'name': product.name, 'slug': product.slug,
    })
