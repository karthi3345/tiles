from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")[:10]

        unread_count = notifications.filter(is_read=False).count()

        return {
            "notifications": notifications,
            "unread_count": unread_count,
        }

    return {
        "notifications": [],
        "unread_count": 0,
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