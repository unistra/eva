# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0002_training_reappli_atb'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='published_mecc_url',
            field=models.URLField(verbose_name='URL publique', blank=True, null=True, default=None),
        ),
    ]
