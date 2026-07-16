"""
URLConf ریشهٔ پروژه.

مسیرها:
    /admin/   -> پنل مدیریت Django
    /         -> شامل URLهای اپ catalog (خانه، فهرست محصولات، جزئیات محصول)

مرجع: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contact/", include("contact.urls")),
    path("", include("catalog.urls")),
]

# سرو کردن فایل‌های media (تصاویر آپلودی) فقط در حالت DEBUG.
# در production فایل‌های media باید توسط Nginx/CDN سرو شوند، نه Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
