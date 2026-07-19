"""
محدودکنندهٔ نرخ درخواست (Rate Limiting) سبک، مبتنی بر فریم‌ورک cache خود
جنگو — بدون نیاز به وابستگی خارجی مثل django-ratelimit.

برای فرم‌های عمومی و بدون احراز هویت (مثل فرم تماس) که در معرض ارسال
انبوه/اسپم یا حتی حملهٔ سیل ایمیل (از طریق send_mail در ContactView) قرار
دارند، استفاده می‌شود. کلید محدودیت بر اساس IP کاربر ساخته می‌شود.

نکته: اگر پروژه پشت یک reverse proxy (مثل Nginx) قرار دارد، باید هدر
X-Forwarded-For توسط خود Nginx به‌درستی تنظیم شود تا IP واقعی کاربر (و نه
IP خود پراکسی) خوانده شود.
"""

from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect


def get_client_ip(request):
    """استخراج IP واقعی کاربر با در نظر گرفتن هدر X-Forwarded-For (پشت پراکسی)."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class RateLimitMixin:
    """
    Mixin برای Class-Based View ها؛ تعداد درخواست‌های POST هر IP را در یک
    بازهٔ زمانی مشخص محدود می‌کند. استفاده:

        class ContactView(RateLimitMixin, CreateView):
            rate_limit_count = 5      # حداکثر تعداد درخواست مجاز
            rate_limit_window = 300   # طول بازهٔ زمانی به ثانیه
    """

    rate_limit_count = 5
    rate_limit_window = 300  # ۵ دقیقه
    rate_limit_message = (
        "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً چند دقیقه دیگر دوباره تلاش کنید."
    )

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and self._is_rate_limited(request):
            messages.error(request, self.rate_limit_message)
            return redirect(request.path)
        return super().dispatch(request, *args, **kwargs)

    def _cache_key(self, request):
        return f"ratelimit:{self.__class__.__name__}:{get_client_ip(request)}"

    def _is_rate_limited(self, request):
        key = self._cache_key(request)
        count = cache.get(key, 0)
        if count >= self.rate_limit_count:
            return True
        # timeout بازهٔ زمانی را روی اولین درخواست تنظیم می‌کند تا پنجرهٔ
        # محدودیت به‌صورت "غلتان" (نه دقیقاً ثابت) رفتار کند؛ برای این
        # مورد استفاده (جلوگیری از اسپم) کفایت می‌کند.
        cache.add(key, 0, timeout=self.rate_limit_window)
        try:
            count = cache.incr(key)
        except ValueError:
            # کلید بین add و incr منقضی شده؛ دوباره از صفر شروع می‌شود.
            cache.set(key, 1, timeout=self.rate_limit_window)
            count = 1
        return count > self.rate_limit_count
