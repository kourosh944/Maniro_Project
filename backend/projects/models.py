"""
مدل اپ پروژه‌ها.

نمونه‌کارها/پروژه‌های اجراشده توسط شرکت را نگه می‌دارد؛ فیلدها دقیقاً
مطابق درخواست: title, client, location, year, image, description.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from common.validators import MaxFileSizeValidator, validate_image_content


def current_year_plus_one():
    return timezone.now().year + 1


def project_image_upload_to(instance, filename):
    return f"projects/images/{filename}"


class Project(models.Model):
    """یک پروژهٔ اجراشده/در حال اجرا."""

    title = models.CharField("عنوان پروژه", max_length=200)
    slug = models.SlugField(
        "اسلاگ",
        max_length=220,
        unique=True,
        allow_unicode=True,
        blank=True,
        help_text="در صورت خالی گذاشتن، خودکار از روی عنوان ساخته می‌شود.",
    )
    client = models.CharField("کارفرما", max_length=200, blank=True)
    location = models.CharField("محل اجرا", max_length=200, blank=True)
    year = models.PositiveIntegerField(
        "سال اجرا",
        validators=[MinValueValidator(1300), MaxValueValidator(current_year_plus_one)],
    )
    image = models.ImageField(
        "تصویر",
        upload_to=project_image_upload_to,
        blank=True,
        null=True,
        validators=[MaxFileSizeValidator(5), validate_image_content],
        help_text="فرمت‌های تصویری معتبر، حداکثر حجم ۵ مگابایت.",
    )
    description = models.TextField("توضیحات", blank=True)

    # فیلدهای کمکی برای مدیریت بهتر محتوا در پنل ادمین:
    is_active = models.BooleanField("فعال / نمایش در سایت", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"
        ordering = ["-year", "-created_at"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return f"{self.title} ({self.year})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
