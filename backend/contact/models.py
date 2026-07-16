"""
مدل اپ تماس با ما.

پیام‌های ارسالی از فرم تماس سایت را ذخیره می‌کند. فیلدها دقیقاً مطابق
درخواست: name, phone, email, subject, message, created_at.
"""

from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^[0-9+\-\s()]{7,20}$",
    message="شماره تماس معتبر نیست. فقط عدد، فاصله، خط تیره، پرانتز یا + مجاز است.",
)


class ContactMessage(models.Model):
    """یک پیام ارسال‌شده از فرم «تماس با ما»."""

    name = models.CharField("نام و نام خانوادگی", max_length=150)
    phone = models.CharField(
        "شماره تماس",
        max_length=20,
        blank=True,
        validators=[phone_validator],
    )
    email = models.EmailField("ایمیل")
    subject = models.CharField("موضوع", max_length=200)
    message = models.TextField("متن پیام")
    created_at = models.DateTimeField("تاریخ ارسال", auto_now_add=True)

    # فیلد کمکی برای مدیریت گردش‌کار پیام‌ها در پنل ادمین:
    is_read = models.BooleanField("خوانده‌شده", default=False)

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"
