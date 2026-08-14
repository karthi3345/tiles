from django.urls import path
from . import views

app_name = 'tiles'

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Location browsing
    path('locations/', views.countries_list, name='countries'),
    path('locations/<slug:country_slug>/', views.states_list, name='states'),
    path('locations/<slug:country_slug>/<slug:state_slug>/', views.cities_list, name='cities'),
    path('locations/<slug:country_slug>/<slug:state_slug>/<slug:city_slug>/', views.villages_list, name='villages'),
    path('locations/<slug:country_slug>/<slug:state_slug>/<slug:city_slug>/<slug:village_slug>/', views.village_tiles, name='village_tiles'),

    # Tile catalog — literal/specific paths MUST come before the <slug:slug> catch-all below,
    # otherwise Django matches them as a tile slug and 404s (e.g. "generate-all-designs" was
    # being treated as a tile slug instead of hitting generate_all_tile_images).
    path('tiles/', views.tile_catalog, name='tile_catalog'),
    path('tiles/generate-all-designs/', views.generate_all_tile_images, name='generate_all_images'),
    path('tiles/<slug:slug>/generate-design/', views.generate_single_tile_image, name='generate_tile_design'),
    path('tiles/<slug:slug>/', views.tile_detail, name='tile_detail'),  # catch-all: keep this LAST among tiles/ routes

    # AI tools
    path('chat/', views.chat_view, name='chat'),
    path('generate-image/', views.generate_image_view, name='generate_image'),

    # Search API
    path('api/location-search/', views.location_search, name='location_search'),
    path('api/find-nearest/', views.find_nearest_location, name='find_nearest_location'),
    path(
    "download/<int:pk>/",
    views.download_generated_image,
    name="download_generated_image",
),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),

    # Shopping Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:tile_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:tile_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:tile_id>/', views.cart_remove, name='cart_remove'),

    # Checkout & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),

    # Order History
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),


]