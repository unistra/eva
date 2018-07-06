# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Domaine', max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code composante', max_length=3)),
                ('is_on_duty', models.BooleanField(verbose_name='En service', default=True)),
                ('label', models.CharField(verbose_name='Libellé composante', max_length=85)),
                ('id_dircomp', models.CharField(verbose_name='Directeur de composante', max_length=65, blank=True)),
                ('id_rac', models.CharField(verbose_name='Responsable administratif', max_length=65, blank=True)),
                ('ROF_code', models.CharField(verbose_name='Code RNE', max_length=10, blank=True, null=True)),
                ('ROF_support', models.BooleanField(verbose_name='Appui ROF', default=False)),
                ('dircomp', models.ForeignKey(blank=True, null=True, related_name='dircomp', to='adm.MeccUser')),
                ('diretu', models.ManyToManyField(blank=True, related_name='diretu', to='adm.MeccUser')),
                ('field', models.ForeignKey(to='institute.AcademicField')),
                ('rac', models.ForeignKey(blank=True, null=True, related_name='racs', to='adm.MeccUser')),
                ('scol_manager', models.ManyToManyField(blank=True, related_name='scol_managers', to='adm.MeccUser')),
            ],
            options={
                'permissions': (('can_view_institute', 'Peut voir les composantes'),),
            },
        ),
    ]
