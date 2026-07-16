"""
میکسین‌های عمومی و قابل‌استفادهٔ مجدد برای پنل ادمین Django.

این ماژول یک اپ جداگانه نیست؛ صرفاً یک پکیج پایتونی مشترک است که
تمام اپ‌های پروژه (catalog, projects, certificates, ...) می‌توانند
از آن برای جلوگیری از تکرار کد استفاده کنند.
"""

from django.contrib import admin
from django.utils.html import format_html


class ThumbnailAdminMixin:
    """
    پیش‌نمایش تصویر در پنل ادمین (best-practice برای مدیریت محتوا
    بدون نیاز به برنامه‌نویسی):

    - ``thumbnail``     : تصویر کوچک در ستون لیست (list_display)
    - ``image_preview`` : تصویر بزرگ‌تر در فرم ویرایش (readonly_fields)

    برای استفاده کافیست ``ThumbnailAdminMixin`` را قبل از
    ``admin.ModelAdmin`` اضافه کنید و در صورت متفاوت بودن نام فیلد
    تصویر، ``thumbnail_field`` را override کنید.
    """

    thumbnail_field = "image"
    thumbnail_list_size = 48
    thumbnail_preview_size = 320

    @admin.display(description="تصویر")
    def thumbnail(self, obj):
        image = getattr(obj, self.thumbnail_field, None)
        if image:
            return format_html(
                '<img src="{}" style="width:{size}px;height:{size}px;'
                'object-fit:cover;border-radius:6px;" />',
                image.url,
                size=self.thumbnail_list_size,
            )
        return "—"

    @admin.display(description="پیش‌نمایش تصویر")
    def image_preview(self, obj):
        image = getattr(obj, self.thumbnail_field, None)
        if image:
            return format_html(
                '<img src="{}" style="max-width:{size}px;max-height:{size}px;'
                'border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.18);" />',
                image.url,
                size=self.thumbnail_preview_size,
            )
        return "بدون تصویر"
