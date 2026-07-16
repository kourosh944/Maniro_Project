"""
View های اپ کاتالوگ — تماماً Class-Based View (CBV)، بدون داده Placeholder؛
هر view مستقیماً از پایگاه‌داده (مدل Product) می‌خواند.

    HomeView          -> صفحهٔ خانه                              (/)
    ProductListView    -> فهرست محصولات با جستجو/فیلتر/صفحه‌بندی  (/products/)
    ProductDetailView  -> صفحهٔ اختصاصی هر محصول                  (/products/<slug>/)
"""

from django.views.generic import DetailView, ListView, TemplateView

from .forms import ProductFilterForm
from .models import Product


class HomeView(TemplateView):
    template_name = "catalog/home.html"


class ProductListView(ListView):
    """فهرست محصولات فعال، مستقیماً از دیتابیس؛ با جستجو/فیلتر/صفحه‌بندی داخلی Django."""

    model = Product
    template_name = "catalog/catalog.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category")

        self.filter_form = ProductFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            query = self.filter_form.cleaned_data.get("q")
            category = self.filter_form.cleaned_data.get("category")

            if query:
                queryset = queryset.filter(title__icontains=query)
            if category:
                queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.filter_form
        return context


class ProductDetailView(DetailView):
    """صفحهٔ اختصاصی هر محصول؛ بر اساس اسلاگ از دیتابیس واکشی می‌شود."""

    model = Product
    template_name = "catalog/detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category")
