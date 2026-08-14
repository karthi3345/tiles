from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from tiles.models import Notification
import re


# Register
def register(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # Full Name Validation
        if not full_name:
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Full name is required."}
            )

        # Email Validation
        if not email:
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Email is required."}
            )

        # Password Length
        if len(password1) < 8:
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must be at least 8 characters long."}
            )

        # Uppercase
        if not re.search(r"[A-Z]", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one uppercase letter."}
            )

        # Lowercase
        if not re.search(r"[a-z]", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one lowercase letter."}
            )

        # Number
        if not re.search(r"\d", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one number."}
            )

        # Special Character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one special character."}
            )

        # Confirm Password
        if password1 != password2:
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Passwords do not match."}
            )

        # Existing User
        if User.objects.filter(username=email).exists():
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "An account with this email already exists."}
            )

        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=full_name
        )

        # Auto Login
        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend"
        )

        # ── Notification: welcome on registration ──
        Notification.objects.create(
            user=user,
            notif_type='general',
            message=f"Welcome to Studio Mathri, {full_name}! Your account has been created successfully.",
            related_url='/accounts/profile/',
        )

        return redirect("accounts:profile")


    return render(
        request,
        "tiles/accounts/register.html"
    )



# Login
def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend"
            )

            # ── Notification: welcome back on login ──
            name = user.get_full_name() or user.username
            Notification.objects.create(
                user=user,
                notif_type='general',
                message=f"Welcome back, {name}! You have logged in successfully.",
                related_url='/accounts/profile/',
            )

            return redirect("accounts:profile")

        else:

            return render(
                request,
                "tiles/accounts/login.html",
                {
                    "error": "Invalid email or password"
                }
            )


    return render(
        request,
        "tiles/accounts/login.html"
    )

from .forms import ProfileForm
from tiles.models import UserProfile

# Profile
@login_required
def profile(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.first_name
        }
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()

            Notification.objects.create(
                user=request.user,
                notif_type='general',
                message="Profile updated successfully!",
                related_url='/accounts/profile/',
            )

            return redirect("accounts:profile")

    else:

        form = ProfileForm(
            instance=profile
        )

    # Countries + cities for the location pickers
    from tiles.models import Country, City
    countries = Country.objects.all().order_by("name")
    cities_by_country = {}
    for c in countries:
        cities_by_country[c.id] = list(
            City.objects.filter(state__country=c)
            .values("id", "name", "state__name")
            .order_by("name")
        )


    return render(
        request,
        "tiles/accounts/profile.html",
        {
            "form": form,
            "profile": profile,
            "countries": countries,
            "cities_by_country": cities_by_country,
        }
    )



# Logout
def logout_view(request):

    # ── Notification: record logout BEFORE session is destroyed ──
    if request.user.is_authenticated:
        Notification.objects.create(
            user=request.user,
            notif_type='general',
            message="You have been logged out. See you soon!",
            related_url='/',
        )

    logout(request)

    return redirect("tiles:home")