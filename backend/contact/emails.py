"""
توابع ارسال ایمیل‌های اعلان اپ «تماس با ما».

دو ایمیل اعلان در این پروژه ارسال می‌شود:

    send_new_message_notification(msg)
        وقتی پیام جدیدی از فرم تماس سایت ثبت می‌شود، به ایمیل خودِ ادمین
        (settings.CONTACT_FORM_RECIPIENTS) اطلاع می‌دهد که «پیام جدید
        دارید». محتوای کامل پیام همچنان فقط داخل پنل ادمین قابل مشاهده
        است؛ این ایمیل صرفاً یک اعلان کوتاه + لینک است.

    send_reply_notification(msg)
        وقتی ادمین از داخل پنل به پیام کاربر پاسخ می‌دهد، به ایمیل خودِ
        فرستنده اطلاع می‌دهد که «پیام شما پاسخ داده شد» و متن پاسخ را
        هم داخل ایمیل می‌آورد.

هر دو ایمیل زیرشان یک لینک «برای مشاهده کلیک کنید» به آدرس سایت
(settings.SITE_URL) دارند. ایمیل‌ها به‌صورت HTML + نسخهٔ متنی ساده
(fallback) ارسال می‌شوند تا هم در کلاینت‌های مدرن دکمه دیده شود و هم در
کلاینت‌های صرفاً متنی، آدرس به‌صورت خام و قابل‌کلیک باشد.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def _cta_button_html(url, label="برای مشاهده کلیک کنید"):
    return (
        '<p style="margin-top:24px;">'
        f'<a href="{url}" '
        'style="display:inline-block;padding:10px 22px;background:#0b6e4f;'
        'color:#ffffff;text-decoration:none;border-radius:6px;'
        'font-family:tahoma,sans-serif;font-size:14px;">'
        f"{label}</a></p>"
    )


def _wrap_html(inner_html):
    return f'<div dir="rtl" style="font-family:tahoma,sans-serif;line-height:1.9;font-size:14px;color:#222;">{inner_html}</div>'


def _send(subject, text_body, html_body, recipients):
    if not recipients:
        logger.warning("ارسال ایمیل لغو شد چون لیست گیرندگان خالی است (%s).", subject)
        return
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)
    except Exception:
        logger.exception("ارسال ایمیل با خطا مواجه شد (%s).", subject)
        raise


def send_new_message_notification(contact_message):
    """اطلاع به ادمین: پیام جدیدی در سایت ثبت شده است."""
    link = settings.SITE_URL
    subject = "پیام جدید از فرم تماس سایت مانیرو"

    text_body = (
        "پیام جدیدی از فرم «تماس با ما» سایت ثبت شد.\n\n"
        f"نام: {contact_message.name}\n"
        f"موضوع: {contact_message.subject}\n"
        f"ایمیل فرستنده: {contact_message.email}\n"
        f"تلفن: {contact_message.phone or '-'}\n\n"
        f"برای مشاهده کلیک کنید: {link}\n"
    )

    html_body = _wrap_html(
        "<p>پیام جدیدی از فرم «تماس با ما» سایت ثبت شد.</p>"
        f"<p><b>نام:</b> {contact_message.name}<br>"
        f"<b>موضوع:</b> {contact_message.subject}<br>"
        f"<b>ایمیل فرستنده:</b> {contact_message.email}<br>"
        f"<b>تلفن:</b> {contact_message.phone or '-'}</p>"
        f"{_cta_button_html(link)}"
    )

    _send(subject, text_body, html_body, settings.CONTACT_FORM_RECIPIENTS)


def send_reply_notification(contact_message):
    """اطلاع به فرستنده: پیامش توسط ادمین پاسخ داده شد."""
    link = settings.SITE_URL
    subject = f"پیام شما پاسخ داده شد: {contact_message.subject}"

    text_body = (
        f"سلام {contact_message.name} عزیز،\n\n"
        "پیام شما پاسخ داده شد.\n\n"
        "متن پاسخ:\n"
        f"{contact_message.reply_text}\n\n"
        "----------------------------------------\n"
        "پیام اصلی شما:\n"
        f"{contact_message.message}\n\n"
        f"برای مشاهده کلیک کنید: {link}\n"
    )

    html_body = _wrap_html(
        f"<p>سلام {contact_message.name} عزیز،</p>"
        "<p>پیام شما پاسخ داده شد.</p>"
        '<p style="background:#f4f4f4;padding:12px 16px;border-radius:6px;">'
        f"{contact_message.reply_text}</p>"
        f"{_cta_button_html(link)}"
    )

    _send(subject, text_body, html_body, [contact_message.email])
