# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mecctable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='coefficient',
            field=models.DecimalField(blank=True, max_digits=2, decimal_places=2, verbose_name="Coefficient de l'épreuve", null=True),
        ),
    ]
