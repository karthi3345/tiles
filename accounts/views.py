from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

        messages.success(
            request,
            "Account created successfully!"
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

            messages.success(
                request,
                "Profile picture updated successfully!"
            )

            return redirect("accounts:profile")

    else:

        form = ProfileForm(
            instance=profile
        )


    return render(
        request,
        "tiles/accounts/profile.html",
        {
            "form": form,
            "profile": profile
        }
    )



# Logout
def logout_view(request):

    logout(request)

    return redirect("tiles:home")