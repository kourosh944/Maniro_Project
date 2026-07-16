"""
تنظیمات Django برای پروژهٔ مانیرو (config).

ساختار پروژه:
    backend/
        config/     -> تنظیمات، URLConf ریشه، WSGI/ASGI (این پکیج)
        catalog/    -> اپ کاتالوگ محصولات
        media/      -> فایل‌های آپلودی کاربر/ادمین (تصاویر محصولات و ...)
        manage.py

نکات production:
    - SECRET_KEY و DEBUG از متغیرهای محیطی خوانده می‌شوند تا هیچ مقدار
      حساسی داخل کد commit نشود. برای development مقدار پیش‌فرض امن
      فراهم شده تا نیازی به تنظیم دستی نباشد.
    - در production حتماً باید:
        DJANGO_SECRET_KEY   -> یک مقدار تصادفی و طولانی
        DJANGO_DEBUG        -> False
        DJANGO_ALLOWED_HOSTS-> دامنه‌های واقعی (comma-separated)
      به‌صورت متغیر محیطی سرور تنظیم شوند.

مرجع: https://docs.djangoproject.com/en/5.2/topics/settings/
"""

import os
from pathlib import Path

# BASE_DIR -> backend/  (دایرکتوری حاوی manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# PROJECT_ROOT -> ریشهٔ کل پروژه (شامل css/, js/, assets/, pages/, backend/)
# دارایی‌های فرانت‌اند (CSS/JS/تصاویر) از همین ریشه به Django معرفی می‌شوند
# تا نیازی به کپی یا بازنویسی آن‌ها نباشد.
PROJECT_ROOT = BASE_DIR.parent


# ==============================================================================
# Security
# ==============================================================================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    # مقدار پیش‌فرض فقط برای development؛ در production همیشه از env بخوانید.
    "django-insecure-dev-only-change-me-in-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]


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
        # همان اپ خوانده می‌شوند (APP_DIRS=True). این پوشه فقط برای
        # قالب‌های سراسری پروژه (مثلاً 404.html سفارشی) است.
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
# برای development از SQLite استفاده می‌شود (بدون نیاز به سرور جداگانه).
# برای production می‌توان با override کردن این تنظیم (مثلاً از طریق
# متغیرهای محیطی) به PostgreSQL/MySQL سوییچ کرد.
# مرجع: https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# ==============================================================================

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


# ==============================================================================
# Media files (فایل‌های آپلودی — مثلاً تصویر محصولات)
# مرجع: https://docs.djangoproject.com/en/5.2/topics/files/
# ==============================================================================

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


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

# آدرس/آدرس‌های ایمیل مدیر سایت که باید اعلان پیام‌های فرم تماس را دریافت کنند.
# چند آدرس را با کاما جدا کنید، مثلاً: "admin@maniro.ir,sales@maniro.ir"
CONTACT_FORM_RECIPIENTS = [
    email.strip()
    for email in os.environ.get("CONTACT_FORM_RECIPIENTS", "").split(",")
    if email.strip()
]


# ==============================================================================
# Default primary key field type
# مرجع: https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
