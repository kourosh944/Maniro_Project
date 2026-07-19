import logging

from django.contrib import admin, messages
from django.utils import timezone

from .emails import send_reply_notification
from .models import ContactMessage

logger = logging.getLogger(__name__)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    صندوق داخلی پیام‌های «تماس با ما».

    پیام‌های ارسالی از سایت فقط همین‌جا (داخل پنل ادمین) دیده می‌شوند —
    هیچ ایمیلی به ایمیل شخصی ادمین ارسال نمی‌شود. اگر ادمین بخواهد به
    فرستنده جواب بدهد، کافی است متن پاسخ را در فیلد «متن پاسخ» بنویسد
    و رکورد را ذخیره کند؛ در همان لحظه یک ایمیل واقعی برای آدرس ایمیلِ
    فرستنده (همان ایمیلی که در فرم تماس وارد کرده) ارسال می‌شود.
    """

    list_display = (
        "name",
        "subject",
        "email",
        "phone",
        "created_at",
        "is_read",
        "replied",
    )
    list_display_links = ("name", "subject")
    list_filter = ("is_read", "replied", "created_at")
    search_fields = ("name", "email", "phone", "subject", "message")
    list_editable = ("is_read",)
    date_hierarchy = "created_at"
    ordering = ("is_read", "-created_at")
    list_per_page = 25
    readonly_fields = (
        "name",
        "phone",
        "email",
        "subject",
        "message",
        "created_at",
        "replied",
        "replied_at",
        "replied_by",
    )
    fieldsets = (
        ("اطلاعات فرستنده", {"fields": ("name", "phone", "email")}),
        ("پیام", {"fields": ("subject", "message", "created_at")}),
        ("وضعیت", {"fields": ("is_read",)}),
        (
            "پاسخ به فرستنده",
            {
                "fields": ("reply_text", "replied", "replied_at", "replied_by"),
                "description": (
                    "متن پاسخ را اینجا بنویسید و «ذخیره» را بزنید؛ یک ایمیل "
                    "شامل همین متن مستقیماً برای ایمیل فرستنده ارسال می‌شود."
                ),
            },
        ),
    )
    actions = ["mark_as_read", "mark_as_unread"]

    def has_add_permission(self, request):
        # پیام‌ها فقط از طریق فرم سایت ثبت می‌شوند، نه از پنل ادمین.
        return False

    def get_readonly_fields(self, request, obj=None):
        # وقتی از قبل پاسخ داده شده، دیگر متن پاسخ قابل ویرایش نیست
        # (برای جلوگیری از ارسال پاسخِ تصادفیِ دوباره). برای پاسخ جدید
        # باید یک پیام دیگر از کاربر دریافت شود.
        readonly = list(self.readonly_fields)
        if obj and obj.replied:
            readonly.append("reply_text")
        return readonly

    def save_model(self, request, obj, form, change):
        should_send_reply = (
            change
            and "reply_text" in form.changed_data
            and obj.reply_text.strip()
            and not obj.replied
        )

        if should_send_reply:
            obj.replied = True
            obj.replied_at = timezone.now()
            obj.replied_by = request.user
            obj.is_read = True

        super().save_model(request, obj, form, change)

        if should_send_reply:
            self._send_reply_email(request, obj)

    def _send_reply_email(self, request, contact_message):
        """اطلاع به فرستنده که پیامش پاسخ داده شده (شامل متن پاسخ + لینک سایت)."""
        try:
            send_reply_notification(contact_message)
            messages.success(
                request, f"پاسخ با موفقیت به {contact_message.email} ارسال شد."
            )
        except Exception:
            logger.exception("ارسال ایمیل پاسخ به فرستنده با خطا مواجه شد.")
            messages.error(
                request,
                "پیام ذخیره شد ولی ارسال ایمیل پاسخ با خطا مواجه شد؛ "
                "تنظیمات SMTP را بررسی کنید.",
            )

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌نشده")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
