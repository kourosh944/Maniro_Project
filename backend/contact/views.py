"""
View اپ تماس با ما (Class-Based View).

ContactView:
    - فرم را با ContactMessageForm اعتبارسنجی می‌کند (سمت سرور، کامل).
    - در صورت معتبر بودن: رکورد در دیتابیس ذخیره می‌شود (CreateView).
    - سپس یک ایمیل اعلان به مدیر سایت ارسال می‌شود (تنظیمات SMTP در
      config/settings.py — بخش Email).
    - پیام موفقیت از طریق فریم‌ورک messages نمایش داده می‌شود.
    - از الگوی Post/Redirect/Get استفاده می‌شود تا با رفرش صفحه، پیام
      دوباره ارسال نشود.

CSRF: چون از فرم Django با {% csrf_token %} در تمپلیت استفاده می‌شود و
CsrfViewMiddleware در MIDDLEWARE فعال است، محافظت CSRF به‌صورت خودکار
روی این view اعمال می‌شود (نیازی به کد اضافه نیست).
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ContactMessageForm
from .models import ContactMessage

logger = logging.getLogger(__name__)


class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactMessageForm
    template_name = "contact/contact.html"
    success_url = reverse_lazy("contact:contact")

    def form_valid(self, form):
        # ذخیره در دیتابیس (رفتار پیش‌فرض CreateView؛ صریحاً فراخوانی می‌شود
        # تا self.object قبل از ارسال ایمیل مقداردهی شده باشد).
        response = super().form_valid(form)

        self._notify_admin(self.object)

        messages.success(
            self.request,
            "پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.",
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را برطرف کنید.")
        return super().form_invalid(form)

    def _notify_admin(self, contact_message):
        """ارسال ایمیل اعلان به مدیر سایت. خطای SMTP نباید کاربر را با خطای ۵۰۰ مواجه کند."""
        recipients = settings.CONTACT_FORM_RECIPIENTS
        if not recipients:
            logger.warning(
                "CONTACT_FORM_RECIPIENTS خالی است؛ ایمیل اعلان فرم تماس ارسال نشد."
            )
            return

        subject = f"پیام جدید از فرم تماس سایت: {contact_message.subject}"
        body = (
            f"نام: {contact_message.name}\n"
            f"تلفن: {contact_message.phone}\n"
            f"ایمیل: {contact_message.email}\n"
            f"موضوع: {contact_message.subject}\n\n"
            f"متن پیام:\n{contact_message.message}\n"
        )

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
        except Exception:
            # اگر SMTP هنوز پیکربندی نشده یا موقتاً در دسترس نیست، پیام کاربر
            # همچنان باید در دیتابیس ذخیره‌شده و صفحه موفق نشان داده شود؛
            # فقط خطا برای بررسی بعدی توسط توسعه‌دهنده لاگ می‌شود.
            logger.exception("ارسال ایمیل اعلان فرم تماس با خطا مواجه شد.")
