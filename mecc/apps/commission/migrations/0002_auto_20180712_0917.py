# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commission', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecicommissionmember',
            name='member_type',
            field=models.CharField(verbose_name='Type', max_length=20, choices=[('commission', 'Commission ECI'), ('tenured', 'Etudiant CFVU titulaire'), ('supply', 'Etudiant CFVU suppléant'), ('catit', 'Etudiant CA titulaire'), ('casup', 'Etudiant CA suppléant')]),
        ),
    ]
