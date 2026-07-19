"""
View اپ تماس با ما (Class-Based View).

ContactView:
    - فرم را با ContactMessageForm اعتبارسنجی می‌کند (سمت سرور، کامل).
    - در صورت معتبر بودن: رکورد در دیتابیس ذخیره می‌شود (CreateView) و
      بلافاصله در «صندوق داخلی» پنل ادمین سایت
      (/admin/contact/contactmessage/) قابل مشاهده است.
    - سپس یک ایمیل کوتاه اعلان («پیام جدید دارید» + لینک) به ایمیل خودِ
      ادمین (settings.CONTACT_FORM_RECIPIENTS) ارسال می‌شود — نگاه کنید
      به contact/emails.py -> send_new_message_notification.
    - پاسخ‌دادن به فرستنده از داخل پنل ادمین انجام می‌شود؛ در آن لحظه
      یک ایمیل «پیام شما پاسخ داده شد» برای فرستنده ارسال می‌شود —
      نگاه کنید به contact/admin.py -> ContactMessageAdmin.save_model.
    - پیام موفقیت از طریق فریم‌ورک messages نمایش داده می‌شود.
    - از الگوی Post/Redirect/Get استفاده می‌شود تا با رفرش صفحه، پیام
      دوباره ارسال نشود.

CSRF: چون از فرم Django با {% csrf_token %} در تمپلیت استفاده می‌شود و
CsrfViewMiddleware در MIDDLEWARE فعال است، محافظت CSRF به‌صورت خودکار
روی این view اعمال می‌شود (نیازی به کد اضافه نیست).

Rate limiting: چون این فرم بدون احراز هویت و در دسترس عموم است، در
برابر اسپم/ارسال انبوه با RateLimitMixin (common/throttling.py) محدود
شده است.
"""

import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from common.throttling import RateLimitMixin

from .emails import send_new_message_notification
from .forms import ContactMessageForm
from .models import ContactMessage

logger = logging.getLogger(__name__)


class ContactView(RateLimitMixin, CreateView):
    model = ContactMessage
    form_class = ContactMessageForm
    template_name = "contact/contact.html"
    success_url = reverse_lazy("contact:contact")

    # حداکثر ۵ ارسال موفق در هر ۵ دقیقه برای هر IP.
    rate_limit_count = 5
    rate_limit_window = 300

    def form_valid(self, form):
        # ذخیره در دیتابیس؛ همین رکورد در پنل ادمین به‌عنوان پیام جدید
        # در «صندوق تماس‌ها» دیده می‌شود.
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
        """اعلان ایمیلی کوتاه به ادمین. خطای SMTP نباید کاربر را با خطای ۵۰۰ مواجه کند."""
        try:
            send_new_message_notification(contact_message)
        except Exception:
            # اگر SMTP هنوز پیکربندی نشده یا موقتاً در دسترس نیست، پیام کاربر
            # همچنان باید در دیتابیس ذخیره‌شده و صفحه موفق نشان داده شود؛
            # فقط خطا برای بررسی بعدی توسط توسعه‌دهنده لاگ می‌شود.
            logger.exception("ارسال ایمیل اعلان پیام جدید به ادمین با خطا مواجه شد.")
