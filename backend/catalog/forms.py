"""
فرم فیلتر/جستجوی کاتالوگ.

این فرم روی querystring (GET) کار می‌کند تا لینک قابل اشتراک‌گذاری
(?q=...&category=...) تولید شود.
"""

from django import forms

from .models import Category


class ProductFilterForm(forms.Form):
    q = forms.CharField(
        label="جستجو",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "جستجوی محصول..."}),
    )
    category = forms.ModelChoiceField(
        label="دسته‌بندی",
        queryset=Category.objects.all(),
        required=False,
        empty_label="همه دسته‌ها",
    )
