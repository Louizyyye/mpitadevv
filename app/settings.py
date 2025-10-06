import os
from pathlib import Path

# ---------------------------------------------------------
# BASE CONFIGURATION
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key secret in production!
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

# SECURITY WARNING: don’t run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# ---------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------
INSTALLED_APPS = [
    # Django Core Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local Apps
    "core",
]

# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------
# URL & WSGI CONFIG
# ---------------------------------------------------------
ROOT_URLCONF = "mpitasite.urls"
WSGI_APPLICATION = "mpitasite.wsgi.application"

# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------
# DATABASE CONFIGURATION (PostgreSQL for Render)
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "mpita_admin"),
        "USER": os.environ.get("DB_USER", "mpita_admin"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "ZdPfoG4xvhvaWQDTqY5YpNqEtTnJxIy7"),
        "HOST": os.environ.get("DB_HOST", "dpg-d3goj6ili9vc73faa8a0-a"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# ---------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
# STATIC & MEDIA FILES
# ---------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------
# SECURITY (Production Hardening)
# ---------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"

    # Optional: add HSTS for stronger HTTPS enforcement
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ---------------------------------------------------------
# LOGGING (Helpful for Render Logs)
# ---------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
