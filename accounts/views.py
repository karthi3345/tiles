from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# Register
def register(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")


        if password1 != password2:
            return render(
                request,
                "tiles/accounts/register.html",
                {
                    "error": "Passwords do not match"
                }
            )


        if User.objects.filter(username=email).exists():

            return render(
                request,
                "tiles/accounts/register.html",
                {
                    "error": "Email already exists"
                }
            )


        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=full_name
        )


        # auto login after register
        user.backend = "django.contrib.auth.backends.ModelBackend"

        login(request, user)


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