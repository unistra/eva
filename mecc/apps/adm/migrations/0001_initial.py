# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MeccUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cmp', models.CharField(verbose_name='Composante', max_length=5, blank=True)),
                ('status', models.CharField(verbose_name='Statut', max_length=4, blank=True, choices=[('STU', 'Étudiant'), ('ADM', 'Administratif'), ('PROF', 'Enseignant')])),
                ('is_ref_app', models.BooleanField(verbose_name='Référent application', default=False)),
            ],
            options={
                'verbose_name': 'Utilisateur',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code du profil', max_length=10)),
                ('label', models.TextField(verbose_name='Libellé du profil')),
                ('year', models.IntegerField(verbose_name='Année', blank=True, null=True)),
                ('cmp', models.CharField(verbose_name='Composante', max_length=3)),
            ],
            options={
                'permissions': (('DES1', 'Donne accès à un large panel de fonctionnalité'), ('DES2', 'Donne accès à un panel restreint'), ('DES3', "Peut usurper l'identité des utilisateurs")),
            },
        ),
        migrations.AddField(
            model_name='meccuser',
            name='profile',
            field=models.ManyToManyField(to='adm.Profile'),
        ),
        migrations.AddField(
            model_name='meccuser',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
