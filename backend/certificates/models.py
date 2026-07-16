"""
مدل اپ گواهینامه‌ها.

گواهینامه‌ها/استانداردهای شرکت (مانند ISO 9001، ISO 45001) را نگه
می‌دارد. فیلدها دقیقاً مطابق درخواست: title, image, issue_date.
"""

from django.db import models


def certificate_image_upload_to(instance, filename):
    return f"certificates/images/{filename}"


class Certificate(models.Model):
    """یک گواهینامه/مدرک صادرشده برای شرکت."""

    title = models.CharField("عنوان گواهینامه", max_length=200)
    image = models.ImageField(
        "تصویر", upload_to=certificate_image_upload_to, blank=True, null=True
    )
    issue_date = models.DateField("تاریخ صدور")

    # فیلد کمکی برای مدیریت بهتر محتوا در پنل ادمین:
    is_active = models.BooleanField("فعال / نمایش در سایت", default=True)

    class Meta:
        verbose_name = "گواهینامه"
        verbose_name_plural = "گواهینامه‌ها"
        ordering = ["-issue_date"]

    def __str__(self):
        return self.title
