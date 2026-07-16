"""
پیکربندی WSGI برای پروژهٔ config — استفاده‌شده توسط سرورهای production
(مثل gunicorn) برای اجرای اپلیکیشن Django.

مرجع: https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
