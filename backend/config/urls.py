"""
URLConf ریشهٔ پروژه.

مسیرها:
    /<ADMIN_URL>/   -> پنل مدیریت Django (پیش‌فرض admin/، قابل تغییر با
                       متغیر محیطی DJANGO_ADMIN_URL — به config/settings.py
                       مراجعه کنید)
    /               -> شامل URLهای اپ catalog (خانه، فهرست محصولات، جزئیات محصول)

خطاهای ۴۰۴/۵۰۰: وقتی DEBUG=False است، Django به‌صورت خودکار قالب‌های
templates/404.html و templates/500.html (در ریشهٔ backend/) را به‌جای
صفحهٔ پیش‌فرض خام نمایش می‌دهد؛ نیازی به handler اضافه نیست.

مرجع: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("contact/", include("contact.urls")),
    path("", include("catalog.urls")),
]

# سرو کردن فایل‌های media (تصاویر آپلودی) فقط در حالت DEBUG.
# در production فایل‌های media باید توسط Nginx/CDN سرو شوند، نه Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
