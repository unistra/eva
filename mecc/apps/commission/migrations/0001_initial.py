# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ECICommissionMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('username', models.CharField(verbose_name='ID Membre', max_length=35, unique=True)),
                ('last_name', models.CharField(verbose_name='Nom', max_length=35)),
                ('first_name', models.CharField(verbose_name='Prénom', max_length=35)),
                ('member_type', models.CharField(verbose_name='Type', max_length=20, choices=[('commission', 'Commission ECI'), ('tenured', 'Etudiant CFVU titulaire'), ('supply', 'Etudiant CFVU suppléant')])),
                ('email', models.CharField(verbose_name='Mail', max_length=256)),
            ],
            options={
                'permissions': (('can_view_eci_commission_member', 'Peut voir les membres de la commission ECI'),),
            },
        ),
    ]
