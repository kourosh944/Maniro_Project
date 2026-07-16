"""
پیکربندی ASGI برای پروژهٔ config — استفاده‌شده توسط سرورهای async
(مثل uvicorn/daphne) در صورت نیاز به قابلیت‌های async در آینده.

مرجع: https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
