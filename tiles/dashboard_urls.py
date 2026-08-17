"""
URL routes for the TailAdmin dashboard mounted at /admin/.
"""
from django.urls import path
from . import views_dashboard
from . import views_sections

app_name = 'dashboard'

urlpatterns = [
    # /admin/ → TailAdmin dashboard (redirects to login if not staff)
    path('', views_dashboard.tailadmin_dashboard, name='tailadmin_dashboard'),

    # In-dashboard sections (mirror Django admin model lists, no redirects)
    path('section/countries/', views_sections.section_countries, name='section_countries'),
    path('section/states/', views_sections.section_states, name='section_states'),
    path('section/cities/', views_sections.section_cities, name='section_cities'),
    path('section/villages/', views_sections.section_villages, name='section_villages'),
    path('section/categories/', views_sections.section_categories, name='section_categories'),
    path('section/effects/', views_sections.section_effects, name='section_effects'),
    path('section/finishes/', views_sections.section_finishes, name='section_finishes'),
    path('section/sizes/', views_sections.section_sizes, name='section_sizes'),
    path('section/products/', views_sections.section_products, name='section_products'),
    path('section/showrooms/', views_sections.section_showrooms, name='section_showrooms'),
    path('section/insights/', views_sections.section_insights, name='section_insights'),
    path('section/chats/', views_sections.section_chats, name='section_chats'),
    path('section/messages/', views_sections.section_messages, name='section_messages'),
    path('section/images/', views_sections.section_images, name='section_images'),
    path('section/users/', views_sections.section_users, name='section_users'),
    path('section/profiles/', views_sections.section_profiles, name='section_profiles'),
    path('section/notifications/', views_sections.section_notifications, name='section_notifications'),
    path('section/orders/', views_sections.section_orders, name='section_orders'),
    path('section/order-items/', views_sections.section_order_items, name='section_order_items'),
    path('section/payments/', views_sections.section_payments, name='section_payments'),

    # Excel export for any section (staff-only)
    path('section/<str:section>/export/', views_sections.section_export, name='section_export'),

    # Add Product (AJAX, staff-only)
    path('section/products/add/', views_sections.product_add, name='product_add'),

    # Login/logout using Django's built-in admin auth views so the
    # dashboard's staff gate works at the new mount point.
    path('login/', views_dashboard.admin_login_view, name='login'),
    path('logout/', views_dashboard.admin_logout_view, name='logout'),
]
