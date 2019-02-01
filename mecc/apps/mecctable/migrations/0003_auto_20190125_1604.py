# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mecctable', '0002_auto_20190115_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectslink',
            name='is_existing_rof',
            field=models.BooleanField(verbose_name="Témoin d'existence dans ROF", default=True),
        ),
        migrations.AddField(
            model_name='structureobject',
            name='is_existing_rof',
            field=models.BooleanField(verbose_name="Témoin d'existence dans ROF", default=True),
        ),
    ]
