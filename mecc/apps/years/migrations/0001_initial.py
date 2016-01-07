# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PdfStored',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('filename', models.CharField(verbose_name='Nom du fichier', max_length=25)),
                ('upload', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='UniversityYear',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('code_year', models.IntegerField(verbose_name='Code Année', unique=True)),
                ('label_year', models.CharField(verbose_name='Libellée Année', max_length=9)),
                ('is_target_year', models.BooleanField(verbose_name='Année Cible', default=False)),
                ('date_validation', models.DateField(verbose_name='Date validation du cadre en CFVU')),
                ('date_expected', models.DateField(verbose_name='Date prévisionnelle de la CFVU MECC')),
                ('pdf_doc', models.CharField(verbose_name='Documents pdf', max_length=100)),
                ('is_year_init', models.BooleanField(verbose_name='Init Composante', default=False)),
            ],
        ),
    ]
