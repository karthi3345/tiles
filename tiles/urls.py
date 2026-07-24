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
]