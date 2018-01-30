# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mecctable', '0002_auto_20180130_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='coefficient',
            field=models.DecimalField(null=True, verbose_name="Coefficient de l'épreuve", decimal_places=2, max_digits=4, blank=True),
        ),
    ]
