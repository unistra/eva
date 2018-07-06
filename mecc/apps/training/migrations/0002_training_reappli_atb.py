# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='reappli_atb',
            field=models.BooleanField(verbose_name='Témoin de réapplication des attributs en mode ROF', default=False),
        ),
    ]
