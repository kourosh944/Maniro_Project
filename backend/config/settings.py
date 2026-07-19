"""
تنظیمات Django برای پروژهٔ مانیرو (config).

ساختار پروژه:
    backend/
        config/     -> تنظیمات، URLConf ریشه، WSGI/ASGI (این پکیج)
        catalog/    -> اپ کاتالوگ محصولات
        common/     -> ماژول‌های مشترک (validators, throttling, admin mixins)
        media/      -> فایل‌های آپلودی کاربر/ادمین (تصاویر محصولات و ...)
        manage.py

نکات production (چک‌لیست کامل در README.md نیز آمده):
    - SECRET_KEY، DEBUG، ALLOWED_HOSTS و سایر مقادیر حساس همگی از
      متغیرهای محیطی خوانده می‌شوند تا هیچ مقدار حساسی داخل کد commit
      نشود. برای development مقدار پیش‌فرض امن فراهم شده تا نیازی به
      تنظیم دستی نباشد.
    - اگر DEBUG=False باشد و DJANGO_SECRET_KEY تنظیم نشده باشد، اجرای
      پروژه با خطا متوقف می‌شود (fail-fast) تا هرگز با کلید پیش‌فرض
      ناامن روی سرور واقعی اجرا نشود.
    - حداقل متغیرهای محیطی لازم برای production:
        DJANGO_SECRET_KEY            -> با get_random_secret_key() بسازید
        DJANGO_DEBUG=False
        DJANGO_ALLOWED_HOSTS         -> دامنه‌های واقعی (comma-separated)
        DJANGO_CSRF_TRUSTED_ORIGINS  -> https://دامنه‌های واقعی
      نمونهٔ کامل در .env.example موجود است.

مرجع: https://docs.djangoproject.com/en/5.2/topics/settings/
مرجع امنیت production: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# PROJECT_ROOT -> ریشهٔ کل پروژه (شامل css/, js/, assets/, pages/, backend/)
# دارایی‌های فرانت‌اند (CSS/JS/تصاویر) از همین ریشه به Django معرفی می‌شوند
# تا نیازی به کپی یا بازنویسی آن‌ها نباشد.
PROJECT_ROOT = BASE_DIR.parent

# در development، در صورت وجود فایل backend/.env آن را بارگذاری می‌کند تا
# نیازی به export دستی متغیرهای محیطی در هر بار اجرا نباشد. در production
# این فایل معمولاً وجود ندارد و متغیرها توسط خود سرور/سیستم سرویس تنظیم
# می‌شوند؛ نبود پکیج python-dotenv (که فقط در requirements/development.txt
# است) هم نباید باعث خطا شود.
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


def env_bool(name, default=False):
    return os.environ.get(name, str(default)) == "True"


def env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# ==============================================================================
# Security
# ==============================================================================

DEBUG = env_bool("DJANGO_DEBUG", True)

_INSECURE_DEFAULT_KEY = "django-insecure-dev-only-change-me-in-production"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", _INSECURE_DEFAULT_KEY)

if not DEBUG and SECRET_KEY == _INSECURE_DEFAULT_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY باید در production از طریق متغیر محیطی تنظیم شود "
        "(هرگز از مقدار پیش‌فرض insecure استفاده نکنید). برای ساخت یک مقدار "
        "تصادفی و امن دستور زیر را اجرا کنید:\n"
        "    python -c \"from django.core.management.utils import "
        "get_random_secret_key; print(get_random_secret_key())\""
    )

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

# دامنه‌هایی که مجاز به ارسال درخواست‌های POST (مثل فرم تماس/ادمین) با در
# نظر گرفتن CSRF هستند. از Django 4 به بعد، برای هر دامنهٔ HTTPS الزامی است.
# مثال: DJANGO_CSRF_TRUSTED_ORIGINS=https://maniro.ir,https://www.maniro.ir
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

# مسیر پنل ادمین قابل تغییر است تا حدس زدن/اسکن خودکار آن سخت‌تر شود
# (security-through-obscurity به‌عنوان یک لایهٔ اضافه، نه جایگزین احراز
# هویت قوی). پیش‌فرض همان "admin/" باقی می‌ماند تا در development چیزی
# تغییر نکند.
ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", "admin/")


# ==============================================================================
# Application definition
# ==============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # اپ‌های پروژه
    "catalog.apps.CatalogConfig",
    "projects.apps.ProjectsConfig",
    "certificates.apps.CertificatesConfig",
    "contact.apps.ContactConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise بلافاصله بعد از SecurityMiddleware قرار می‌گیرد تا فایل‌های
    # استاتیک را مستقیماً از خود Django (فشرده و با کش صحیح) سرو کند و
    # نیازی به وب‌سرور جداگانه فقط برای static نباشد.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # قالب‌های اختصاصی هر اپ به‌صورت خودکار از پوشهٔ templates/ داخل
        # همان اپ خوانده می‌شوند (APP_DIRS=True). این پوشه برای قالب‌های
        # سراسری پروژه (404.html / 500.html سفارشی) است.
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ==============================================================================
# Database
# پیش‌فرض SQLite است (مناسب development، بدون نیاز به سرور جداگانه).
# با تنظیم DJANGO_DB_ENGINE=postgresql در متغیرهای محیطی، بدون هیچ تغییر
# کدی به PostgreSQL سوییچ می‌کند — مناسب production.
# مرجع: https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# ==============================================================================

if os.environ.get("DJANGO_DB_ENGINE") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DJANGO_DB_NAME"],
            "USER": os.environ["DJANGO_DB_USER"],
            "PASSWORD": os.environ["DJANGO_DB_PASSWORD"],
            "HOST": os.environ.get("DJANGO_DB_HOST", "localhost"),
            "PORT": os.environ.get("DJANGO_DB_PORT", "5432"),
            # استفادهٔ مجدد از کانکشن‌های دیتابیس به‌جای باز/بسته کردن در
            # هر درخواست (کاهش overhead در production).
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ==============================================================================
# Password validation
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==============================================================================
# Internationalization
# سایت مانیرو فارسی و راست‌به‌چپ است.
# ==============================================================================

LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


# ==============================================================================
# Static files (CSS, JavaScript, تصاویر ثابت سایت)
# دارایی‌های فرانت‌اند از قبل در ریشهٔ پروژه (css/, js/, assets/) آماده‌اند؛
# با معرفی آن‌ها به STATICFILES_DIRS (با پیشوند مشخص)، همان مسیرهای نسبی
# قبلی (../css/..., ../js/..., ../assets/...) به‌صورت {% static 'css/...' %}
# در قالب‌های Django قابل استفاده‌اند، بدون نیاز به کپی یا تغییر فایل‌ها.
# مرجع: https://docs.djangoproject.com/en/5.2/howto/static-files/
# ==============================================================================

STATIC_URL = "static/"

STATICFILES_DIRS = [
    ("css", PROJECT_ROOT / "css"),
    ("js", PROJECT_ROOT / "js"),
    ("assets", PROJECT_ROOT / "assets"),
]

# مقصد جمع‌آوری فایل‌های استاتیک هنگام اجرای `collectstatic` (فقط production)
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # در production از WhiteNoise با هش نام فایل (cache-busting) و
        # فشرده‌سازی gzip/brotli استفاده می‌شود؛ در development از
        # storage سادهٔ پیش‌فرض جنگو (بدون نیاز به collectstatic مکرر).
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# ==============================================================================
# Media files (فایل‌های آپلودی — مثلاً تصویر محصولات)
# مرجع: https://docs.djangoproject.com/en/5.2/topics/files/
# ==============================================================================

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# محدودیت حجم آپلود در سطح Django (جدا از محدودیت هر فیلد در
# common/validators.py) — از پر شدن حافظه توسط فایل‌های بسیار حجیم/مخرب
# جلوگیری می‌کند. باید هم‌تراز یا بیشتر از بزرگ‌ترین حد مجاز فیلد (فایل
# PDF محصول، ۱۵ مگابایت) باشد.
FILE_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024


# ==============================================================================
# Cache
# برای rate limiting فرم تماس (common/throttling.py) استفاده می‌شود. در
# development از حافظهٔ محلی پردازه (LocMemCache، بدون نیاز به سرویس
# جانبی) و در صورت تنظیم DJANGO_REDIS_URL (توصیه‌شده برای production با
# چند worker/سرور) از Redis استفاده می‌شود.
# ==============================================================================

REDIS_URL = os.environ.get("DJANGO_REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }


# ==============================================================================
# Email (ارسال ایمیل — مثلاً اعلان پیام‌های فرم تماس به مدیر سایت)
# مرجع: https://docs.djangoproject.com/en/5.2/topics/email/
#
# فقط تنظیمات SMTP واقعی (میزبان، پورت، یوزرنیم/پسورد) بعداً باید از طریق
# متغیرهای محیطی سرور مقداردهی شوند؛ هیچ مقدار حساسی اینجا هاردکد نشده.
# تا زمانی‌که این متغیرها تنظیم نشوند، در DEBUG=True ایمیل‌ها به‌جای ارسال
# واقعی، در کنسول/ترمینال چاپ می‌شوند (django.core.mail.backends.console)
# تا توسعه/تست بدون نیاز به SMTP واقعی امکان‌پذیر باشد.
# ==============================================================================

EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "")  # مثلاً smtp.gmail.com یا mail.maniro.ir
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "False") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = 10  # ثانیه — جلوگیری از هنگ کردن درخواست کاربر در صورت قطعی SMTP

# آدرسی که ایمیل‌های خروجی سایت (مثل اعلان فرم تماس) از طرف آن ارسال می‌شوند.
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@maniro.ir")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# آدرس/آدرس‌های ایمیل مدیر سایت که باید اعلان پیام‌های فرم تماس را دریافت کنند.
# چند آدرس را با کاما جدا کنید، مثلاً: "admin@maniro.ir,sales@maniro.ir"
CONTACT_FORM_RECIPIENTS = env_list("CONTACT_FORM_RECIPIENTS", "")

# آدرس اصلی سایت — در ایمیل‌های اعلان (پیام جدید برای ادمین / پاسخ برای
# فرستنده) به‌صورت لینک «برای مشاهده کلیک کنید» استفاده می‌شود.
SITE_URL = os.environ.get("SITE_URL", "https://manirou.com")

# مدیرانی که در صورت بروز خطای ۵۰۰ روی سرور production، ایمیل خودکار حاوی
# جزئیات خطا (traceback) دریافت می‌کنند. فرمت هر مورد "نام:ایمیل" است،
# چند مورد با کاما جدا می‌شوند، مثلاً: "Admin:admin@maniro.ir,Dev:dev@maniro.ir"
ADMINS = [
    tuple(pair.split(":", 1)) for pair in env_list("DJANGO_ADMINS", "") if ":" in pair
]
MANAGERS = ADMINS


# ==============================================================================
# HTTP Security Headers (production)
# برخی از این تنظیمات (SSL/HSTS/کوکی امن) فقط زمانی فعال می‌شوند که
# DEBUG=False باشد تا در توسعهٔ محلی روی HTTP ساده (127.0.0.1) مزاحم کار
# توسعه‌دهنده نشوند و ری‌دایرکت نامعتبر HTTPS رخ ندهد.
# مرجع: https://docs.djangoproject.com/en/5.2/topics/security/
# ==============================================================================

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # اگر پشت یک reverse proxy با SSL termination (مثل Nginx) قرار دارد،
    # این هدر باید توسط خود Nginx تنظیم شود تا Django بفهمد درخواست
    # اصلی روی HTTPS بوده (وگرنه SECURE_SSL_REDIRECT دچار حلقهٔ ری‌دایرکت
    # می‌شود).
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ==============================================================================
# Logging
# در production، خطاهای سطح ERROR (مثل استثناهای ۵۰۰) هم در کنسول (که
# توسط systemd/Docker/gunicorn جمع‌آوری می‌شود) لاگ می‌شوند و هم به
# ADMINS بالا ایمیل می‌شوند تا بدون نیاز به پایش دستی لاگ‌ها، از خطاهای
# production مطلع شوید.
# مرجع: https://docs.djangoproject.com/en/5.2/topics/logging/
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


# ==============================================================================
# Default primary key field type
# مرجع: https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
