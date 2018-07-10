# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degree', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paragraph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('text_standard', models.TextField(verbose_name="Texte de l'alinéa standard")),
                ('is_in_use', models.BooleanField(verbose_name='En service', default=True)),
                ('display_order', models.IntegerField(verbose_name='Numéro ordre affichage')),
                ('is_interaction', models.BooleanField(verbose_name='Dérogation')),
                ('text_derog', models.TextField(verbose_name="Texte de consigne pour la saisie de         l'alinéa dérogatoire", blank=True)),
                ('text_motiv', models.TextField(verbose_name='Texte de consigne pour la saisie des         motivations', blank=True)),
                ('origin_parag', models.IntegerField(verbose_name="Num. de paragraph d'orgin", null=True)),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('display_order', models.IntegerField(verbose_name='Numéro ordre affichage', default=0)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('label', models.CharField(verbose_name='Libellé', max_length=255)),
                ('is_in_use', models.BooleanField(verbose_name='En service', default=True)),
                ('is_edited', models.CharField(verbose_name='Modifiée', max_length=4, default='X', choices=[('O', 'Oui'), ('N', 'Non'), ('X', 'Nouvelle')])),
                ('is_eci', models.BooleanField(verbose_name='ECI', default=False)),
                ('is_ccct', models.BooleanField(verbose_name='CC/CT', default=False)),
                ('n_rule', models.IntegerField(verbose_name='Numéro de règle')),
                ('degree_type', models.ManyToManyField(to='degree.DegreeType')),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.AddField(
            model_name='paragraph',
            name='rule',
            field=models.ManyToManyField(to='rules.Rule'),
        ),
        migrations.AlterUniqueTogether(
            name='rule',
            unique_together=set([('n_rule', 'code_year')]),
        ),
    ]
