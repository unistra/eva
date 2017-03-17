# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='additional_type',
            field=models.CharField(null=True, max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='comment',
            field=models.TextField(null=True, default='', blank=True),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='uploaded_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 16, 9, 11, 17, 285558, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
