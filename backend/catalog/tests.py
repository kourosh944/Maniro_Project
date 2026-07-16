from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="دکل‌های برق", slug="towers")
        self.product = Product.objects.create(
            name="دکل مشبک فولادی",
            slug="steel-lattice-tower",
            category=self.category,
            code="SKU-001",
            short_description="توضیح کوتاه نمونه",
        )

    def test_str_representation(self):
        self.assertEqual(str(self.product), "دکل مشبک فولادی")

    def test_get_absolute_url(self):
        expected = reverse("catalog:product_detail", kwargs={"slug": self.product.slug})
        self.assertEqual(self.product.get_absolute_url(), expected)


class CatalogViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="تجهیزات صنعتی", slug="equipment")
        self.product = Product.objects.create(
            name="کراس‌آرم فولادی",
            slug="steel-crossarm",
            category=self.category,
            code="SKU-004",
            short_description="توضیح کوتاه نمونه",
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)

    def test_product_list_status_code_and_content(self):
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_list_search_filter(self):
        response = self.client.get(reverse("catalog:product_list"), {"q": "کراس‌آرم"})
        self.assertContains(response, self.product.name)

    def test_product_detail_status_code(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.code)
