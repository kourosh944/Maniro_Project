# Generated manually (Pillow not available in this sandbox to run makemigrations
# automatically) but follows the exact format Django's migration writer produces.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='reply_text',
            field=models.TextField(blank=True, verbose_name='متن پاسخ'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='replied',
            field=models.BooleanField(default=False, verbose_name='پاسخ داده\u200cشده'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='replied_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پاسخ'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='replied_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='contact_replies',
                to=settings.AUTH_USER_MODEL,
                verbose_name='پاسخ\u200cدهنده',
            ),
        ),
    ]
