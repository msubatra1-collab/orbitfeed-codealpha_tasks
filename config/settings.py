"""Django settings for ShopEase.

Local runserver uses ordinary HTTP cookies. Managed HTTPS preview is explicitly
identified by its injected project ID; it needs cross-site cookies for the embedded UI.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-only-shopease-key-change-before-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "store.apps.StoreConfig",
    "orders.apps.OrdersConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "store.context_processors.shop_context",
    ], "builtins": ["store.templatetags.shop_money"]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": Path(os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3")),
    "OPTIONS": {"timeout": 20},
}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "home"

# Only enable cross-site secure cookies when running behind managed HTTPS preview
# (the host injects MANUS_PROJECT_ID). Plain-HTTP local runserver remains usable.
MANAGED_HTTPS_PREVIEW = bool(os.environ.get("MANUS_PROJECT_ID"))
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:3000"] if MANAGED_HTTPS_PREVIEW else []
SESSION_COOKIE_SECURE = MANAGED_HTTPS_PREVIEW or os.environ.get("DJANGO_SESSION_COOKIE_SECURE", "false").lower() == "true"
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SESSION_COOKIE_SAMESITE = "None" if SESSION_COOKIE_SECURE else "Lax"
CSRF_COOKIE_SAMESITE = "None" if SESSION_COOKIE_SECURE else "Lax"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Intentionally omit clickjacking middleware/X-Frame-Options; Preview is embedded cross-origin.

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
