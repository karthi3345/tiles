"""
TailAdmin-style admin dashboard view.
Pulls ALL data from existing models — read-only, no mutations.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.contrib.auth.models import User
from collections import OrderedDict

from .models import (
    Country, State, City, Village,
    TileCategory, TileEffect, TileFinish, TileSize,
    TileProduct, TileShowroom, MarketInsight,
    ChatSession, ChatMessage, GeneratedImage,
    UserProfile, Notification, Order, OrderItem, Payment,
)


@staff_member_required(login_url='/admin/login/')
def tailadmin_dashboard(request):
    # ── Stat cards ──
    total_users = User.objects.count()
    total_products = TileProduct.objects.count()
    total_countries = Country.objects.count()
    total_ai_chats = ChatSession.objects.count()
    total_ai_images = GeneratedImage.objects.count()
    total_categories = TileCategory.objects.count()

    # Revenue (safe — orders table may not exist yet)
    try:
        total_revenue = Payment.objects.filter(status='success').aggregate(
            t=Sum('amount')
        )['t'] or 0
        total_orders = Order.objects.count()
        # Order status distribution for pie chart
        order_status_data = list(
            Order.objects.values('status').annotate(c=Count('id')).order_by('-c')
        )
        order_status_labels = [s['status'].capitalize() for s in order_status_data]
        order_status_values = [s['c'] for s in order_status_data]
    except Exception:
        total_revenue = 0
        total_orders = 0
        order_status_labels = []
        order_status_values = []

    # ── Bar chart: Products per Category (top 10) ──
    cat_data = (
        TileCategory.objects
        .annotate(pc=Count('products'))
        .filter(pc__gt=0)
        .order_by('-pc')[:10]
    )
    cat_labels = [c.name for c in cat_data]
    cat_values = [c.pc for c in cat_data]

    # ── Donut chart: Products per Material ──
    mat_data = (
        TileProduct.objects
        .values('material')
        .annotate(c=Count('id'))
        .order_by('-c')
    )
    mat_labels = [m['material'] for m in mat_data]
    mat_values = [m['c'] for m in mat_data]

    # ── Area chart: Monthly registrations + product additions ──
    user_monthly = (
        User.objects
        .annotate(mo=TruncMonth('date_joined'))
        .values('mo')
        .annotate(c=Count('id'))
        .order_by('mo')
    )
    prod_monthly = (
        TileProduct.objects
        .annotate(mo=TruncMonth('created_at'))
        .values('mo')
        .annotate(c=Count('id'))
        .order_by('mo')
    )
    # Build combined month list
    all_months = sorted(set(
        list(user_monthly.values_list('mo', flat=True)) +
        list(prod_monthly.values_list('mo', flat=True))
    ))
    user_dict = {m['mo']: m['c'] for m in user_monthly}
    prod_dict = {m['mo']: m['c'] for m in prod_monthly}
    month_labels = [m.strftime('%b %Y') for m in all_months]
    user_series = [user_dict.get(m, 0) for m in all_months]
    prod_series = [prod_dict.get(m, 0) for m in all_months]

    # ── Countries for map + table ──
    countries = list(
        Country.objects
        .annotate(pc=Count('tile_products'))
        .order_by('ranking')
    )
    country_table = []
    for c in countries:
        country_table.append({
            'name': c.name,
            'flag': c.flag_emoji or '',
            'ranking': c.ranking,
            'is_producer': c.is_top_producer,
            'is_consumer': c.is_top_consumer,
            'continent': c.continent or '',
            'product_count': c.pc,
            'key_stats': c.key_stats or {},
        })

    # ── City markers for Leaflet map (real lat/long) ──
    city_markers = []
    cities_qs = (
        City.objects
        .select_related('state__country')
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .order_by('state__country__ranking', 'state__name', 'name')
    )
    for city in cities_qs:
        city_markers.append({
            'lat': city.latitude,
            'lng': city.longitude,
            'city': city.name,
            'state': city.state.name,
            'country': city.state.country.name,
            'flag': city.state.country.flag_emoji or '',
            'is_hub': city.is_tile_hub,
        })

    # ── User markers (only users who set a city on their profile) ──
    user_markers = []
    user_profiles = (
        UserProfile.objects
        .filter(city__isnull=False)
        .select_related('user', 'city__state__country')
    )
    for up in user_profiles:
        if up.city.latitude is None or up.city.longitude is None:
            continue
        user_markers.append({
            'lat': up.city.latitude,
            'lng': up.city.longitude,
            'name': up.full_name or up.user.username,
            'email': up.user.email,
            'city': up.city.name,
            'state': up.city.state.name,
            'country': up.city.state.country.name,
            'flag': up.city.state.country.flag_emoji or '',
            'is_staff': up.user.is_staff,
            'avatar': up.profile_picture.url if up.profile_picture else '',
        })

    # ── Country-level markers (centroid of cities in each country) ──
    country_markers = []
    for c in countries:
        cities_in_country = (
            City.objects
            .filter(state__country=c)
            .exclude(latitude__isnull=True)
            .exclude(longitude__isnull=True)
        )
        if cities_in_country.exists():
            avg_lat = sum(ci.latitude for ci in cities_in_country) / cities_in_country.count()
            avg_lng = sum(ci.longitude for ci in cities_in_country) / cities_in_country.count()
            country_markers.append({
                'lat': round(avg_lat, 4),
                'lng': round(avg_lng, 4),
                'country': c.name,
                'flag': c.flag_emoji or '',
                'ranking': c.ranking,
                'products': c.pc,
                'cities': cities_in_country.count(),
                'is_producer': c.is_top_producer,
                'is_consumer': c.is_top_consumer,
            })

    # ── Recent products ──
    recent_products = []
    for p in TileProduct.objects.select_related('category').order_by('-created_at')[:8]:
        recent_products.append({
            'name': p.name,
            'category': p.category.name if p.category else '—',
            'material': p.material or '—',
            'price': p.price_display,
            'image': p.image or '',
            'is_featured': p.is_featured,
            'is_active': p.is_active,
        })

    # ── Recent users ──
    recent_users = []
    for u in User.objects.select_related('user_profile').order_by('-date_joined')[:8]:
        profile = getattr(u, 'user_profile', None)
        recent_users.append({
            'email': u.email,
            'name': profile.full_name if profile and profile.full_name else u.username,
            'date': u.date_joined,
            'is_staff': u.is_staff,
            'avatar': profile.profile_picture.url if profile and profile.profile_picture else '',
        })

    # ── Recent AI chats ──
    recent_chats = []
    for s in ChatSession.objects.annotate(msg_count=Count('messages')).order_by('-updated_at')[:5]:
        last_msg = s.messages.order_by('-created_at').first()
        recent_chats.append({
            'title': s.title or '(untitled)',
            'msg_count': s.msg_count,
            'last_message': (last_msg.content[:80] + '...') if last_msg and len(last_msg.content) > 80 else (last_msg.content if last_msg else ''),
            'updated': s.updated_at,
        })

    # ── Recent generated images ──
    recent_images = []
    for gi in GeneratedImage.objects.select_related('user').order_by('-created_at')[:6]:
        recent_images.append({
            'prompt': gi.prompt[:60] + ('...' if len(gi.prompt) > 60 else ''),
            'image': gi.image or '',
            'model': gi.model_used or '',
            'user': gi.user.email if gi.user else 'Anonymous',
            'date': gi.created_at,
        })

    # ── Notifications summary ──
    unread_notifs = Notification.objects.filter(is_read=False).count()

    # ── Extra sidebar counts ──
    total_messages = ChatMessage.objects.count()
    total_profiles = UserProfile.objects.count()
    total_notifications = Notification.objects.count()
    try:
        total_order_items = OrderItem.objects.count()
        total_payments = Payment.objects.count()
    except Exception:
        total_order_items = 0
        total_payments = 0

    # ── Geographic breakdown ──
    total_states = State.objects.count()
    total_cities = City.objects.count()
    total_villages = Village.objects.count()
    total_effects = TileEffect.objects.count()
    total_finishes = TileFinish.objects.count()
    total_sizes = TileSize.objects.count()
    total_insights = MarketInsight.objects.count()
    total_showrooms = TileShowroom.objects.count()

    context = {
        # Stats
        'total_users': total_users,
        'total_products': total_products,
        'total_countries': total_countries,
        'total_ai_chats': total_ai_chats,
        'total_ai_images': total_ai_images,
        'total_categories': total_categories,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'unread_notifs': unread_notifs,
        # Extra sidebar counts
        'total_messages': total_messages,
        'total_profiles': total_profiles,
        'total_notifications': total_notifications,
        'total_order_items': total_order_items,
        'total_payments': total_payments,
        # Geographic
        'total_states': total_states,
        'total_cities': total_cities,
        'total_villages': total_villages,
        'total_effects': total_effects,
        'total_finishes': total_finishes,
        'total_sizes': total_sizes,
        'total_insights': total_insights,
        'total_showrooms': total_showrooms,
        # Chart data (raw Python — template uses json_script)
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'mat_labels': mat_labels,
        'mat_values': mat_values,
        'month_labels': month_labels,
        'user_series': user_series,
        'prod_series': prod_series,
        # Order status pie
        'order_status_labels': order_status_labels,
        'order_status_values': order_status_values,
        # Table data
        'country_table': country_table,
        'city_markers': city_markers,
        'country_markers': country_markers,
        'user_markers': user_markers,
        'located_users': len(user_markers),
        'recent_products': recent_products,
        'recent_users': recent_users,
        'recent_chats': recent_chats,
        'recent_images': recent_images,
        # User
        'admin_user': request.user,
    }

    return render(request, 'tiles/dashboard.html', context)


# ── Auth views for the /admin/ mount point ──

admin_login_view = auth_views.LoginView.as_view(template_name='tiles/admin_login.html')
admin_logout_view = auth_views.LogoutView.as_view(next_page='/admin/login/')
