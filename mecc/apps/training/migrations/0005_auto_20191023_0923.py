# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0004_auto_20190125_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='sync_create',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='training',
            name='sync_deactiv',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='training',
            name='sync_update_reactiv',
            field=models.DateField(null=True),
        ),
    ]
