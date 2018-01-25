# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mecctable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='structureobject',
            name='ROF_code_year',
            field=models.CharField(max_length=20, blank=True, null=True, verbose_name="Année de l'objet ROF"),
        ),
    ]
