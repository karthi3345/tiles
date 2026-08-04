from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import re

import re
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


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

        # Strong Password Validation
        if len(password1) < 8:
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must be at least 8 characters long."}
            )

        if not re.search(r"[A-Z]", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one uppercase letter."}
            )

        if not re.search(r"[a-z]", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one lowercase letter."}
            )

        if not re.search(r"\d", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one number."}
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Password must contain at least one special character."}
            )

        # Confirm Password Match
        if password1 != password2:
            return render(
                request,
                "tiles/accounts/register.html",
                {"error": "Passwords do not match."}
            )

        # Check Existing User
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
            first_name=full_name,
        )

        # Auto Login
        login(
    request,
    user,
    backend="django.contrib.auth.backends.ModelBackend"
)

        messages.success(request, "Account created successfully!")

        return redirect("accounts:profile")

    return render(request, "tiles/accounts/register.html")


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



# Profile
@login_required
def profile(request):

    return render(
        request,
        "tiles/accounts/profile.html"
    )



# Logout
def logout_view(request):

    logout(request)

    return redirect("tiles:home")