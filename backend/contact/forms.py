"""
فرم فرم تماس با ما — ModelForm روی ContactMessage با اعتبارسنجی کامل
سمت سرور (هرگز نباید فقط به اعتبارسنجی سمت کلاینت اعتماد کرد).
"""

from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "id": "cf-name",
                    "placeholder": " ",
                    "autocomplete": "name",
                    "aria-describedby": "cf-name-error",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "id": "cf-phone",
                    "placeholder": " ",
                    "dir": "ltr",
                    "autocomplete": "tel",
                    "aria-describedby": "cf-phone-error",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "id": "cf-email",
                    "placeholder": " ",
                    "dir": "ltr",
                    "autocomplete": "email",
                    "aria-describedby": "cf-email-error",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "id": "cf-subject",
                    "placeholder": " ",
                    "autocomplete": "off",
                    "aria-describedby": "cf-subject-error",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "id": "cf-message",
                    "placeholder": " ",
                    "autocomplete": "off",
                    "aria-describedby": "cf-message-error",
                    "rows": 6,
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("لطفاً نام خود را کامل وارد کنید (حداقل ۲ حرف).")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise forms.ValidationError("لطفاً شماره تماس خود را وارد کنید.")
        return phone

    def clean_subject(self):
        subject = self.cleaned_data["subject"].strip()
        if len(subject) < 3:
            raise forms.ValidationError("لطفاً موضوع پیام را کامل‌تر وارد کنید (حداقل ۳ حرف).")
        return subject

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("متن پیام باید حداقل ۱۰ حرف باشد.")
        return message
