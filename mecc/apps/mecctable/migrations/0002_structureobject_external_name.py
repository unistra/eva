# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mecctable', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='structureobject',
            name='external_name',
            field=models.CharField(max_length=240, null=True, verbose_name='Intervenant exterieur', blank=True),
        ),
    ]
