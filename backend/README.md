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

### راه‌اندازی سریع

1. `cp .env.example .env` و تمام مقادیر (خصوصاً `DJANGO_SECRET_KEY`،
   `DJANGO_ALLOWED_HOSTS`، `DJANGO_CSRF_TRUSTED_ORIGINS`) را با مقادیر
   واقعی پر کنید. در production خود این فایل روی سرور commit/آپلود
   نمی‌شود؛ متغیرها را در systemd/Docker/پنل هاست تنظیم کنید.
2. `pip install -r requirements/production.txt`
3. `python manage.py migrate`
4. `python manage.py collectstatic --noinput`
5. اجرا با یک WSGI server واقعی (هرگز `runserver` در production):
   `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3`

### چک‌لیست امنیتی که در این نسخه اعمال شده

- **SECRET_KEY / DEBUG / ALLOWED_HOSTS**: از env خوانده می‌شوند؛ اگر
  `DEBUG=False` باشد و `DJANGO_SECRET_KEY` تنظیم نشده باشد، برنامه با
  خطا بالا نمی‌آید (fail-fast) تا هرگز با کلید پیش‌فرض ناامن اجرا نشود.
- **CSRF**: `CsrfViewMiddleware` فعال است و همهٔ فرم‌ها (`{% csrf_token %}`)
  از آن استفاده می‌کنند. برای HTTPS در production حتماً
  `DJANGO_CSRF_TRUSTED_ORIGINS` را با دامنه‌های واقعی پر کنید.
- **XSS**: تمام قالب‌ها Django Template Language هستند که به‌صورت
  پیش‌فرض auto-escape دارند؛ در هیچ‌جای پروژه از `mark_safe`/`|safe`
  روی ورودی کاربر استفاده نشده است.
- **SQL Injection**: تمام کوئری‌ها از طریق Django ORM انجام می‌شوند؛
  هیچ SQL خام (`raw()`/`extra()`) در پروژه وجود ندارد.
- **اعتبارسنجی (Validation)**: همهٔ فرم‌ها (`ContactMessageForm`,
  `ProductFilterForm`) سمت سرور اعتبارسنجی می‌شوند. فیلدهای آپلود فایل
  (تصویر/PDF محصولات، پروژه‌ها، گواهینامه‌ها) هم محدودیت حجم و هم بررسی
  محتوای واقعی فایل دارند (`common/validators.py`) — نه فقط پسوند.
- **Rate limiting**: فرم عمومی تماس با `RateLimitMixin`
  (`common/throttling.py`) در برابر اسپم/سیل ایمیل محدود شده است
  (پیش‌فرض ۵ درخواست در ۵ دقیقه برای هر IP).
- **هدرهای امنیتی HTTP**: در production به‌صورت خودکار فعال می‌شوند:
  HSTS، `X-Frame-Options: DENY`، `X-Content-Type-Options: nosniff`،
  ری‌دایرکت اجباری HTTPS، کوکی‌های Secure/HttpOnly/SameSite.
- **خطاها (Error Handling)**: در `DEBUG=False` صفحات سفارشی
  `templates/404.html` و `templates/500.html` نمایش داده می‌شوند
  (بدون افشای جزئیات فنی)؛ خطاهای ۵۰۰ هم لاگ و هم به `DJANGO_ADMINS`
  ایمیل می‌شوند. ارسال ایمیل فرم تماس هم خطای SMTP را catch می‌کند تا
  کاربر با صفحهٔ ۵۰۰ مواجه نشود.
- **ساختار قابل استفاده مجدد (Reusable)**: منطق مشترک در پکیج `common/`
  نگه داشته می‌شود (`admin_mixins.py` برای پیش‌نمایش تصویر،
  `validators.py` برای اعتبارسنجی فایل، `throttling.py` برای rate
  limit) و توسط چند اپ به‌جای تکرار کد استفاده می‌شود.
- **پنل ادمین**: مسیر آن با `DJANGO_ADMIN_URL` قابل تغییر است.

### موارد دیگر

- پیش از استقرار: `python manage.py collectstatic` را اجرا کنید تا
  فایل‌های استاتیک در `STATIC_ROOT` جمع‌آوری شوند؛ سرو آن‌ها در
  production توسط WhiteNoise (فشرده و با cache-busting) انجام می‌شود،
  بدون نیاز به وب‌سرور جداگانه فقط برای static.
- فایل‌های media (تصاویر آپلودی) در production باید توسط Nginx/CDN سرو
  شوند، نه توسط Django (سرو مستقیم media فقط در `DEBUG=True` فعال است).
- دیتابیس SQLite فقط برای development مناسب است. با تنظیم
  `DJANGO_DB_ENGINE=postgresql` (و متغیرهای `DJANGO_DB_*` مرتبط) بدون
  هیچ تغییر کدی به PostgreSQL سوییچ می‌کنید.
- برای rate limiting در production با بیش از یک worker/سرور، حتماً
  `DJANGO_REDIS_URL` را تنظیم کنید (کش پیش‌فرض LocMemCache بین
  process/سرورهای مختلف مشترک نیست).
- بعد از هر تغییر در فیلدهای مدل (مثل اعتبارسنج‌های جدید این نسخه):
  `python manage.py makemigrations && python manage.py migrate`
