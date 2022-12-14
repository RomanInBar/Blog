# Generated by Django 4.1.2 on 2022-12-23 13:24

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False, verbose_name="Проверено"),
        ),
        migrations.AddField(
            model_name="user",
            name="verification_uuid",
            field=models.UUIDField(
                default=uuid.uuid4, verbose_name="Код подтверждения"
            ),
        ),
    ]
