from django.contrib import admin

from common.admin_mixins import ThumbnailAdminMixin

from .models import Project


@admin.register(Project)
class ProjectAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "title",
        "client",
        "location",
        "year",
        "is_active",
    )
    list_display_links = ("thumbnail", "title")
    list_filter = ("year", "is_active", "location")
    search_fields = ("title", "client", "location", "description")
    ordering = ("-year", "-created_at")
    prepopulated_fields = {"slug": ("title",)}  # تولید خودکار اسلاگ در فرم
    list_editable = ("is_active",)
    save_on_top = True
    list_per_page = 25
    readonly_fields = ("created_at", "image_preview")
    fieldsets = (
        (None, {"fields": ("title", "slug", "client", "location", "year")}),
        ("محتوا", {"fields": ("description", "image", "image_preview")}),
        ("وضعیت", {"fields": ("is_active", "created_at")}),
    )
