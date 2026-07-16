"""
مدل‌های اپ کاتالوگ (Category / Product).

فیلدهای Product دقیقاً مطابق درخواست تعریف شده‌اند:
    title, slug, category, code, image, description, pdf, created_at

چند فیلد کاربردی و متداول (is_active, updated_at) نیز به‌عنوان
best-practice برای مدیریت محتوا در Admin اضافه شده که هیچ‌کدام با
ساختار خواسته‌شده تداخلی ندارند و اختیاری/دارای مقدار پیش‌فرض هستند.
"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """دسته‌بندی محصولات (مثلاً «دکل‌های برق»، «تجهیزات صنعتی»)."""

    name = models.CharField("نام دسته‌بندی", max_length=100, unique=True)
    slug = models.SlugField(
        "اسلاگ", max_length=120, unique=True, allow_unicode=True
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


def product_image_upload_to(instance, filename):
    return f"products/images/{filename}"


def product_pdf_upload_to(instance, filename):
    return f"products/catalogs/{filename}"


class Product(models.Model):
    """یک قلم محصول/تجهیز در کاتالوگ."""

    title = models.CharField("عنوان", max_length=200)
    slug = models.SlugField(
        "اسلاگ",
        max_length=220,
        unique=True,
        allow_unicode=True,
        help_text="در صورت خالی گذاشتن، خودکار از روی عنوان ساخته می‌شود.",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="دسته‌بندی",
        related_name="products",
        on_delete=models.PROTECT,
    )
    code = models.CharField("کد محصول", max_length=50, unique=True, db_index=True)
    image = models.ImageField(
        "تصویر",
        upload_to=product_image_upload_to,
        blank=True,
        null=True,
    )
    description = models.TextField("توضیحات", blank=True)
    pdf = models.FileField(
        "فایل PDF (کاتالوگ فنی)",
        upload_to=product_pdf_upload_to,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    # فیلدهای کمکی برای مدیریت بهتر محتوا در پنل ادمین:
    is_active = models.BooleanField("فعال / نمایش در سایت", default=True)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})
