# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('label', models.TextField(verbose_name='Libellé réglementaire')),
                ('degree_type_label', models.CharField(verbose_name='Libellé du type de diplôme', max_length=120)),
                ('is_used', models.BooleanField(verbose_name='En service', default=True)),
                ('start_year', models.IntegerField(verbose_name='Code année de début de validité')),
                ('end_year', models.IntegerField(verbose_name='Code année de fin de validité')),
                ('ROF_code', models.CharField(verbose_name='Référence Programme ROF', max_length=20)),
                ('APOGEE_code', models.CharField(verbose_name='Référence dans le SI Scolarité (APOGEE)', max_length=40)),
            ],
            options={
                'ordering': ['degree_type_label', 'label'],
            },
        ),
        migrations.CreateModel(
            name='DegreeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('display_order', models.IntegerField(verbose_name='Numéro ordre affichage')),
                ('is_in_use', models.BooleanField(verbose_name='En service')),
                ('short_label', models.CharField(verbose_name='Libellé court', max_length=40)),
                ('long_label', models.CharField(verbose_name='Libellé long', max_length=70)),
                ('ROF_code', models.CharField(verbose_name='Correspondance ROF', max_length=2, blank=True, null=True)),
            ],
            options={
                'ordering': ['display_order', 'short_label'],
                'permissions': (('can_view_degree_type', 'Peut voir les types de diplôme'),),
            },
        ),
        migrations.AddField(
            model_name='degree',
            name='degree_type',
            field=models.ForeignKey(verbose_name='Type de diplôme', to='degree.DegreeType'),
        ),
        migrations.AddField(
            model_name='degree',
            name='institutes',
            field=models.ManyToManyField(to='institute.Institute'),
        ),
    ]
