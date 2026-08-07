import os
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-studio-mathri-change-me-xyz')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Allow the workspace preview domain plus the original Vercel domain and localhost
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()] or [
    "*",
]
# Always allow the Vercel deployment domain
if "tiles-sigma.vercel.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("tiles-sigma.vercel.app")

# CSRF: trust the preview domain and https scheme
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]
# Always trust the Vercel deployment origin
CSRF_TRUSTED_ORIGINS.append("https://tiles-sigma.vercel.app")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',   # <-- Add this
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tiles',
    'accounts',
    'cloudinary',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'allauth.account.middleware.AccountMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
  
]
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
ROOT_URLCONF = 'studiomathri.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tiles', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                 "tiles.context_processors.user_profile",
                 "tiles.context_processors.notification_context",
                 "tiles.context_processors.cart_context",
            ],
        },
    },
]



# Database — MySQL (workspace-provisioned)
# PyMySQL is installed as the MySQL driver (see studiomathri/__init__.py for the shim)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", os.environ.get("DATABASE_NAME")),
        "USER": os.environ.get("DB_USER", os.environ.get("DATABASE_USER")),
        "PASSWORD": os.environ.get("DB_PASSWORD", os.environ.get("DATABASE_PASSWORD")),
        "HOST": os.environ.get("DB_HOST", os.environ.get("DATABASE_HOST", "127.0.0.1")),
        "PORT": os.environ.get("DB_PORT", os.environ.get("DATABASE_PORT", "3306")),
        "OPTIONS": {
            "init_command": "SET sql_mode=STRICT_TRANS_TABLES, NAMES utf8mb4",
            "charset": "utf8mb4",
        },
    }
}

# Use SQLite in-memory for tests (dev MySQL user lacks CREATE DATABASE privilege)
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'tiles', 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (downloaded tile images) configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cloudflare AI Settings
CF_ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID', '')
CF_API_TOKEN = os.getenv('CF_API_TOKEN', '')
CF_CHAT_MODEL = "@cf/google/gemma-4-26b-a4b-it"
CF_IMAGE_MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"
CF_BASE_URL = f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run'

WSGI_APPLICATION = 'studiomathri.wsgi.application'
ASGI_APPLICATION = 'studiomathri.asgi.application'

# Cloudinary Configuration (For manual uploads in views.py)
# Only configure when credentials are present — the app runs fine without it
# (image upload features will gracefully fail, but auth/home/catalog all work).
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    import cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )



GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")




SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret": GOOGLE_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
    }
}

# Bypass intermediate confirmation screens for Google login & logout
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'none'

# REMOVED THE STORAGES DICTIONARY - Not needed since you use URLField now!