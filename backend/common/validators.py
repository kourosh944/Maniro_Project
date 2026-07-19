"""
اعتبارسنج‌های عمومی و قابل‌استفادهٔ مجدد برای فیلدهای آپلود فایل (تصویر/PDF).

این ماژول یک اپ جداگانه نیست؛ صرفاً یک پکیج پایتونی مشترک است که تمام
اپ‌های پروژه (catalog, projects, certificates, ...) می‌توانند برای
اعتبارسنجی سمت سرور فایل‌های آپلودی از آن استفاده کنند تا کد تکرار نشود.

نکتهٔ امنیتی مهم: هرگز نباید فقط به پسوند فایل اعتماد کرد؛ یک فایل مخرب
می‌تواند به‌سادگی با پسوند ".jpg" یا ".pdf" ارسال شود. اعتبارسنج‌های این
ماژول محتوای واقعی فایل را نیز بررسی می‌کنند (Content Validation)، علاوه
بر محدودیت حجم که از upload شدن فایل‌های حجیم/مخرب روی دیسک جلوگیری می‌کند.
"""

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible


@deconstructible
class MaxFileSizeValidator:
    """رد کردن فایل‌های بزرگ‌تر از حد مجاز (جلوگیری از مصرف بی‌رویهٔ فضای دیسک)."""

    def __init__(self, max_size_mb):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if value.size > self.max_size_bytes:
            raise ValidationError(
                "حجم فایل (%(size)s) بیشتر از حد مجاز (%(limit)s مگابایت) است.",
                params={"size": filesizeformat(value.size), "limit": self.max_size_mb},
            )

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_size_mb == other.max_size_mb


@deconstructible
class FileContentValidator:
    """پایهٔ مشترک برای اعتبارسنج‌هایی که محتوای واقعی فایل را می‌خوانند."""

    def _reset(self, value):
        value.seek(0)


def validate_image_content(value):
    """
    بررسی می‌کند فایل ارسالی واقعاً یک تصویر معتبر و سالم است (نه صرفاً
    دارای پسوند تصویر). از Pillow -که پیش‌نیاز ImageField است و از قبل در
    requirements موجود است- برای باز و verify کردن فایل استفاده می‌شود.
    """
    from PIL import Image, UnidentifiedImageError

    try:
        value.seek(0)
        with Image.open(value) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError("فایل ارسالی یک تصویر معتبر نیست یا خراب است.")
    finally:
        value.seek(0)


def validate_pdf_content(value):
    """
    بررسی می‌کند فایل ارسالی واقعاً با امضای باینری استاندارد PDF
    (b"%PDF-") شروع می‌شود؛ اعتماد صرف به پسوند ".pdf" کافی نیست.
    """
    value.seek(0)
    header = value.read(5)
    value.seek(0)
    if header != b"%PDF-":
        raise ValidationError("فایل ارسالی یک PDF معتبر نیست.")
