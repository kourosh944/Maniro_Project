from django.contrib import admin

from common.admin_mixins import ThumbnailAdminMixin

from .models import Category, Product


class HasProductsFilter(admin.SimpleListFilter):
    """فیلتر دسته‌بندی‌ها بر اساس داشتن/نداشتن محصول (برای پاک‌سازی محتوا)."""

    title = "دارای محصول"
    parameter_name = "has_products"

    def lookups(self, request, model_admin):
        return (
            ("yes", "دارای محصول"),
            ("no", "بدون محصول"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(products__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(products__isnull=True)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    list_filter = (HasProductsFilter,)
    search_fields = ("name", "slug")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}  # تولید خودکار اسلاگ در فرم
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("products")

    @admin.display(description="تعداد محصولات")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(ThumbnailAdminMixin, admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "title",
        "code",
        "category",
        "is_active",
        "created_at",
    )
    list_display_links = ("thumbnail", "title")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("title", "code", "description")
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("title",)}  # تولید خودکار اسلاگ در فرم
    autocomplete_fields = ("category",)
    list_editable = ("is_active",)
    list_select_related = ("category",)
    date_hierarchy = "created_at"
    save_on_top = True
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "code")}),
        ("محتوا", {"fields": ("description", "image", "image_preview", "pdf")}),
        ("وضعیت", {"fields": ("is_active", "created_at", "updated_at")}),
    )
