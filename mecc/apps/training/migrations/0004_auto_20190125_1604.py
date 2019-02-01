# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_training_published_mecc_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='training',
            name='is_existing_rof',
            field=models.BooleanField(verbose_name="Témoin d'existence dans ROF", default=True),
        ),
        migrations.AddField(
            model_name='training',
            name='recup_atb_ens',
            field=models.BooleanField(verbose_name='Témoin de récupération des responsables, coef. et notes seuil', default=False),
        ),
    ]
