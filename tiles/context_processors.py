from .models import Notification
from .cart import Cart

def notification_context(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(user=request.user)
        unread_count = qs.filter(is_read=False).count()
        notifications = qs.order_by("-created_at")[:10]

        return {
            "notifications": notifications,
            "unread_count": unread_count,
        }

    return {
        "notifications": [],
        "unread_count": 0,
    }


def cart_context(request):
    """Provide cart item count to all templates (navbar badge)."""
    cart = Cart(request)
    return {
        "cart_item_count": len(cart),
    }


from tiles.models import UserProfile


def user_profile(request):

    profile = None

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": request.user.first_name
            }
        )

    return {
        "user_profile": profile
    }