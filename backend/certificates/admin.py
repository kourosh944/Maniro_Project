from django.contrib import admin

from common.admin_mixins import ThumbnailAdminMixin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = ("thumbnail", "title", "issue_date", "is_active")
    list_display_links = ("thumbnail", "title")
    list_filter = ("is_active", "issue_date")
    search_fields = ("title",)
    ordering = ("-issue_date",)
    list_editable = ("is_active",)
    date_hierarchy = "issue_date"
    save_on_top = True
    list_per_page = 25
    readonly_fields = ("image_preview",)
    fields = ("title", "image", "image_preview", "issue_date", "is_active")
