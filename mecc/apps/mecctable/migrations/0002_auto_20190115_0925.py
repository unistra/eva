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
            name='exam_template_label',
            field=models.CharField(verbose_name="Nom du garabit pour la saisie d'épreuves", max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='structureobject',
            name='is_exam_template',
            field=models.BooleanField(verbose_name="Gabarit pour la saisie d'épreuves", default=False),
        ),
    ]
