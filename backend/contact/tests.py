"""
تست‌های اپ تماس با ما — تمرکز روی محافظت CSRF، اعتبارسنجی سمت سرور و
rate limiting (که این اپ به‌دلیل عمومی/بدون احراز هویت بودن به آن نیاز دارد).
"""

from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactFormValidationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("contact:contact")
        self.valid_payload = {
            "name": "علی رضایی",
            "phone": "09121234567",
            "email": "ali@example.com",
            "subject": "استعلام قیمت",
            "message": "سلام، لطفاً کاتالوگ محصولات را برایم ارسال کنید.",
        }

    def test_valid_submission_creates_message_and_redirects(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, 302)  # Post/Redirect/Get
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_short_message_is_rejected(self):
        payload = {**self.valid_payload, "message": "کوتاه"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)  # form_invalid -> همان صفحه
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        payload = {**self.valid_payload, "email": "not-an-email"}
        response = self.client.post(self.url, payload)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_missing_required_field_is_rejected(self):
        payload = {**self.valid_payload, "name": ""}
        response = self.client.post(self.url, payload)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_admin_notification_email_sent_when_recipients_configured(self):
        with self.settings(CONTACT_FORM_RECIPIENTS=["admin@maniro.ir"]):
            self.client.post(self.url, self.valid_payload)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("admin@maniro.ir", mail.outbox[0].to)


class ContactFormCsrfTests(TestCase):
    """بررسی این‌که CsrfViewMiddleware واقعاً روی این view فعال است."""

    def setUp(self):
        cache.clear()
        self.url = reverse("contact:contact")
        # کلاینت پیش‌فرض Django CSRF را نادیده می‌گیرد؛ برای تست واقعی
        # محافظت CSRF باید enforce_csrf_checks=True فعال شود.
        self.csrf_client = Client(enforce_csrf_checks=True)

    def test_post_without_csrf_token_is_rejected(self):
        response = self.csrf_client.post(
            self.url,
            {
                "name": "کاربر تست",
                "phone": "09120000000",
                "email": "test@example.com",
                "subject": "موضوع تست",
                "message": "این یک پیام تستی برای بررسی CSRF است.",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_csrf_token_present_in_rendered_form(self):
        response = self.client.get(self.url)
        self.assertContains(response, "csrfmiddlewaretoken")


class ContactFormRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("contact:contact")

    def _payload(self, suffix):
        return {
            "name": "کاربر تست",
            "phone": "09120000000",
            "email": f"test{suffix}@example.com",
            "subject": f"موضوع تست {suffix}",
            "message": "این یک پیام تستی برای بررسی محدودیت نرخ ارسال است.",
        }

    def test_requests_beyond_limit_are_blocked(self):
        for i in range(5):
            response = self.client.post(self.url, self._payload(i))
            self.assertEqual(response.status_code, 302)

        # درخواست ششم در همان بازهٔ زمانی باید مسدود شود.
        response = self.client.post(self.url, self._payload("blocked"))
        self.assertEqual(response.status_code, 302)  # ری‌دایرکت به همان صفحه، نه ذخیره
        self.assertEqual(ContactMessage.objects.count(), 5)
