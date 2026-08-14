from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    # TailAdmin custom dashboard at /admin/
    path('admin/', include('tiles.dashboard_urls')),

    # Django default admin (model CRUD) moved to /django-admin/
    path('django-admin/', admin.site.urls),

    # Home, tiles pages
    path('', include('tiles.urls')),

    # Login/Profile/Logout
    path('accounts/', include('accounts.urls')),

    # Google login, signup etc
    path('accounts/', include('allauth.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)