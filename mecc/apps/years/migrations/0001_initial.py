# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstituteYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('id_cmp', models.IntegerField(verbose_name='ID composante')),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('date_expected_MECC', models.DateField(verbose_name='Date prévisionnelle comp. MECC', blank=True, null=True)),
                ('date_last_notif', models.DateField(verbose_name='Date dernière notification MECC', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UniversityYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année', unique=True, error_messages={'unique': 'Ce code année est déjà utilisé.'})),
                ('label_year', models.CharField(verbose_name='Libellé année', max_length=35, blank=True)),
                ('is_target_year', models.BooleanField(verbose_name='Cible courante')),
                ('date_validation', models.DateField(verbose_name='Date validation cadre en CFVU', blank=True, null=True)),
                ('date_expected', models.DateField(verbose_name='Date prévisionnelle CFVU MECC', blank=True, null=True)),
                ('is_year_init', models.BooleanField(verbose_name='Initialisation des composantes effectuée', default=False)),
            ],
        ),
    ]
