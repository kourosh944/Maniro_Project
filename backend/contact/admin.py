from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "email", "phone", "created_at", "is_read")
    list_display_links = ("name", "subject")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "phone", "subject", "message")
    list_editable = ("is_read",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    readonly_fields = ("name", "phone", "email", "subject", "message", "created_at")
    fieldsets = (
        ("اطلاعات فرستنده", {"fields": ("name", "phone", "email")}),
        ("پیام", {"fields": ("subject", "message", "created_at")}),
        ("وضعیت", {"fields": ("is_read",)}),
    )
    actions = ["mark_as_read", "mark_as_unread"]

    def has_add_permission(self, request):
        # پیام‌ها فقط از طریق فرم سایت ثبت می‌شوند، نه از پنل ادمین.
        return False

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌شده")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="علامت‌گذاری به‌عنوان خوانده‌نشده")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
