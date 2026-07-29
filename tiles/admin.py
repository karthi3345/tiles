from django.contrib import admin
from .models import (
    Country, State, City, Village,
    TileCategory, TileEffect, TileFinish, TileSize, TileProduct,
    TileShowroom, MarketInsight, ChatSession, ChatMessage, GeneratedImage,UserProfile
)


class StateInline(admin.TabularInline):
    model = State
    extra = 0
    show_change_link = True


class CityInline(admin.TabularInline):
    model = City
    extra = 0
    show_change_link = True


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'continent', 'ranking', 'is_top_producer', 'is_top_consumer', 'state_count']
    list_filter = ['continent', 'is_top_producer', 'is_top_consumer']
    search_fields = ['name']
    inlines = [StateInline]

    def state_count(self, obj):
        return obj.states.count()

    state_count.short_description = 'States'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state_type', 'is_tile_hub', 'city_count']
    list_filter = ['country', 'is_tile_hub', 'state_type']
    search_fields = ['name']
    inlines = [CityInline]

    def city_count(self, obj):
        return obj.cities.count()

    city_count.short_description = 'Cities'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'country_name', 'city_type', 'is_tile_hub', 'village_count']
    list_filter = ['state__country', 'is_tile_hub', 'city_type']
    search_fields = ['name']

    def country_name(self, obj):
        return obj.state.country.name
    country_name.short_description = 'Country'

    def village_count(self, obj):
        return obj.villages.count()

    village_count.short_description = 'Villages'


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state_name', 'country_name', 'area_type', 'pincode']
    list_filter = ['city__state__country', 'area_type']
    search_fields = ['name', 'pincode']

    def state_name(self, obj):
        return obj.city.state.name
    state_name.short_description = 'State'

    def country_name(self, obj):
        return obj.city.state.country.name
    country_name.short_description = 'Country'


@admin.register(TileCategory)
class TileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tile_type', 'usage_type', 'sort_order']
    list_filter = ['tile_type', 'usage_type']
    ordering = ['sort_order', 'name']


@admin.register(TileEffect)
class TileEffectAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(TileFinish)
class TileFinishAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(TileSize)
class TileSizeAdmin(admin.ModelAdmin):
    list_display = ['size_label', 'width_mm', 'height_mm', 'thickness_mm']
    ordering = ['width_mm']


@admin.register(TileProduct)
class TileProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_tile_type', 'category', 'material', 'price_display', 'is_featured', 'is_active']
    list_filter = ['category__tile_type', 'category', 'material', 'is_featured', 'is_active', 'countries']
    search_fields = ['name', 'material', 'description']
    filter_horizontal = ['countries', 'effects', 'finishes', 'sizes']
    ordering = ['-is_featured', 'name']

    def get_tile_type(self, obj):
        return obj.category.get_tile_type_display()
    get_tile_type.short_description = 'Type'
    get_tile_type.admin_order_field = 'category__tile_type'


@admin.register(TileShowroom)
class TileShowroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'village', 'city_name', 'state_name', 'is_active']
    list_filter = ['village__city__state__country', 'is_active']
    search_fields = ['name', 'village__name']

    def city_name(self, obj):
        return obj.village.city.name
    city_name.short_description = 'City'

    def state_name(self, obj):
        return obj.village.city.state.name
    state_name.short_description = 'State'


@admin.register(MarketInsight)
class MarketInsightAdmin(admin.ModelAdmin):
    list_display = ['country', 'title', 'year']
    list_filter = ['year', 'country']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'title', 'created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_short', 'created_at']
    list_filter = ['role']

    def content_short(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_short.short_description = 'Content'


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ['prompt_short', 'model_used', 'created_at']

    def prompt_short(self, obj):
        return obj.prompt[:80] + '...' if len(obj.prompt) > 80 else obj.prompt
    prompt_short.short_description = 'Prompt'


admin.site.register(UserProfile)