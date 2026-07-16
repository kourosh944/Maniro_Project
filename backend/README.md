# Maniro Backend (Django)

بک‌اند سایت مانیرو — پیاده‌سازی‌شده با Django، برای development با SQLite.

## ساختار

```
backend/
├── manage.py
├── requirements.txt
├── db.sqlite3          (پس از اجرای migrate ساخته می‌شود)
├── config/              # تنظیمات پروژه، URLConf ریشه، WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── catalog/              # اپ کاتالوگ محصولات
│   ├── models.py         # Category, Product
│   ├── admin.py
│   ├── forms.py          # فرم جستجو/فیلتر
│   ├── views.py          # HomeView, product_list, ProductDetailView
│   ├── urls.py
│   ├── templates/catalog/ # base.html, home.html, catalog.html, detail.html
│   └── static/catalog/    # نقطهٔ توسعهٔ استایل/اسکریپت اختصاصی اپ
└── media/                 # فایل‌های آپلودی (تصاویر محصولات)
```

استایل‌ها و اسکریپت‌های اصلی سایت (پوشه‌های `css/`, `js/`, `assets/` در
ریشهٔ پروژه) کپی نشده‌اند و مستقیماً از طریق `STATICFILES_DIRS` در
`config/settings.py` به Django معرفی شده‌اند.

## راه‌اندازی (Development)

```bash
cd backend

# ۱) ساخت و فعال‌سازی virtual environment (در صورتی که هنوز نساخته‌اید)
python3 -m venv .venv
source .venv/bin/activate        # ویندوز: .venv\Scripts\activate

# ۲) نصب وابستگی‌ها
pip install -r requirements.txt

# ۳) اجرای مایگریشن‌ها (ساخت جداول در SQLite)
python manage.py makemigrations catalog
python manage.py migrate

# ۴) ساخت کاربر ادمین
python manage.py createsuperuser

# ۵) اجرای سرور توسعه
python manage.py runserver
```

سپس:

- سایت: http://127.0.0.1:8000/
- کاتالوگ: http://127.0.0.1:8000/products/
- پنل ادمین: http://127.0.0.1:8000/admin/

## نکات Production

- مقادیر `DJANGO_SECRET_KEY`، `DJANGO_DEBUG=False` و
  `DJANGO_ALLOWED_HOSTS` را به‌عنوان متغیر محیطی سرور تنظیم کنید (هرگز
  در کد commit نشوند).
- پیش از استقرار: `python manage.py collectstatic` را اجرا کنید تا
  فایل‌های استاتیک در `STATIC_ROOT` جمع‌آوری شوند.
- در production فایل‌های media باید توسط Nginx/CDN سرو شوند، نه توسط
  خود Django (تنظیم فعلی سرو media فقط در `DEBUG=True` فعال است).
- دیتابیس SQLite فقط برای development مناسب است؛ برای production
  می‌توان بخش `DATABASES` در `config/settings.py` را به PostgreSQL
  سوییچ کرد.
