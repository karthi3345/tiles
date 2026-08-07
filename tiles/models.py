
# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    flag_emoji = models.CharField(max_length=10, blank=True)
    continent = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    market_overview = models.TextField(blank=True)
    key_stats = models.JSONField(default=dict, blank=True)
    is_top_producer = models.BooleanField(default=False)
    is_top_consumer = models.BooleanField(default=False)
    ranking = models.PositiveIntegerField(default=0)
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ranking']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, blank=True)
    state_type = models.CharField(max_length=50, default='State',
        help_text="State, Province, Region, Community, etc.")
    description = models.TextField(blank=True)
    is_tile_hub = models.BooleanField(default=False, help_text="Major tile manufacturing hub")

    class Meta:
        ordering = ['name']
        unique_together = ['country', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    @property
    def city_count(self):
        return self.cities.count()


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    city_type = models.CharField(max_length=50, default='City',
        help_text="City, Town, District, Municipality, etc.")
    description = models.TextField(blank=True)
    is_tile_hub = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        unique_together = ['state', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.state.name}"

    @property
    def village_count(self):
        return self.villages.count()

    @property
    def country(self):
        return self.state.country


class Village(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='villages')
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, blank=True)
    area_type = models.CharField(max_length=50, default='Area',
        help_text="Village, Area, Neighborhood, Ward, District, etc.")
    description = models.TextField(blank=True)
    pincode = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ['city', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.city.name}"

    @property
    def state(self):
        return self.city.state

    @property
    def country(self):
        return self.city.state.country


class TileCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    usage_type = models.CharField(
        max_length=20,
        choices=[
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
        ],
        default='residential',
        help_text='Whether the category is for residential or commercial projects',
    )
    tile_type = models.CharField(max_length=20, default='both',
        choices=[
            ('floor', 'Floor'),
            ('wall', 'Wall'),
            ('both', 'Floor & Wall'),
            ('special', 'Special Purpose'),
        ])
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TileEffect(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TileFinish(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TileSize(models.Model):
    size_label = models.CharField(max_length=50, unique=True)
    width_mm = models.PositiveIntegerField()
    height_mm = models.PositiveIntegerField()
    thickness_mm = models.FloatField(default=8.0)

    class Meta:
        ordering = ['width_mm', 'height_mm']

    def __str__(self):
        return self.size_label


class TileProduct(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)

    category = models.ForeignKey(
        TileCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )

    effects = models.ManyToManyField(
        TileEffect,
        blank=True,
        related_name='products'
    )

    finishes = models.ManyToManyField(
        TileFinish,
        blank=True,
        related_name='products'
    )

    sizes = models.ManyToManyField(
        TileSize,
        blank=True,
        related_name='products'
    )

    countries = models.ManyToManyField(
        Country,
        blank=True,
        related_name='tile_products'
    )

    description = models.TextField(blank=True)
    material = models.CharField(max_length=100, blank=True)

    price_range_min = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    price_range_max = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    image = models.URLField(
    blank=True,
    null=True
)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name

    @property
    def price_display(self):
        return f"${self.price_range_min}-{self.price_range_max}"


class TileShowroom(models.Model):
    """Physical showroom/dealer locations linked to villages/areas"""
    name = models.CharField(max_length=300)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='showrooms')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    products = models.ManyToManyField(TileProduct, blank=True, related_name='showrooms')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.village.name}"
    
    


class MarketInsight(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='insights')
    title = models.CharField(max_length=300)
    content = models.TextField()
    year = models.PositiveIntegerField(default=2024)
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-created_at']

    def __str__(self):
        return f"{self.country.name} - {self.title}"


class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or self.session_id


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('user','User'),('assistant','Assistant'),('system','System')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"


class GeneratedImage(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    prompt = models.TextField()
    image = models.URLField(blank=True, null=True)
    model_used = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Generated: {self.prompt[:50]}"


from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile"
    )

    full_name = models.CharField(
        max_length=200,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.user.username

from django.conf import settings

class Notification(models.Model):
    NOTIF_TYPES = [
        ('image_generated', 'Image Generated'),
        ('image_failed', 'Image Failed'),
        ('download_ready', 'Download Ready'),
        ('download_complete', 'Download Complete'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notif_type = models.CharField(
        max_length=30, choices=NOTIF_TYPES, default='general'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_url = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return self.related_url if self.related_url else '#'

    def __str__(self):
        return f"{self.notif_type} — {self.user.username}"


# ─────────── E-COMMERCE: ORDERS & PAYMENTS ───────────


class Order(models.Model):
    """Represents a customer order — created at checkout, linked to a Razorpay order."""

    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    order_id = models.CharField(max_length=100, unique=True, help_text="Razorpay order ID")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')

    # Shipping info captured at checkout
    customer_name = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} — {self.status}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Line item in an order — snapshots the tile price at purchase time."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    tile = models.ForeignKey(TileProduct, on_delete=models.SET_NULL, null=True, blank=True)
    tile_name = models.CharField(max_length=300, help_text="Snapshot of tile name")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    size_label = models.CharField(max_length=50, blank=True)

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.tile_name} x{self.quantity}"


class Payment(models.Model):
    """Records the Razorpay payment transaction for an order."""

    PAYMENT_STATUS = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=300, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='success')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.razorpay_payment_id} — {self.status}"