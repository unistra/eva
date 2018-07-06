# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '__first__'),
        ('degree', '__first__'),
        ('adm', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalParagraph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('rule_gen_id', models.IntegerField(verbose_name='ID règle générale')),
                ('origin_id', models.IntegerField(verbose_name='ID original', blank=True, null=True, default=None)),
                ('text_additional_paragraph', models.TextField(verbose_name="Texte d'alinéa additionnel")),
            ],
        ),
        migrations.CreateModel(
            name='SpecificParagraph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('rule_gen_id', models.IntegerField(verbose_name='ID règle générale')),
                ('paragraph_gen_id', models.IntegerField(verbose_name='ID alinéa général')),
                ('type_paragraph', models.CharField(verbose_name='Type alinéa', max_length=1, choices=[('D', 'Dérogatoire'), ('C', 'Composante')])),
                ('text_specific_paragraph', models.TextField(verbose_name="Texte d'alinéa spécifique")),
                ('text_motiv', models.TextField(verbose_name='Texte de motivation')),
                ('origin_id', models.IntegerField(verbose_name='ID original', blank=True, null=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('label', models.TextField(verbose_name='Intitulé de formation')),
                ('is_used', models.BooleanField(verbose_name='En service', default=True)),
                ('MECC_tab', models.BooleanField(verbose_name='Témoin Tableau MECC', default=True)),
                ('MECC_type', models.CharField(verbose_name='Régime MECC de la formation', max_length=1, choices=[('E', 'ECI'), ('C', 'CC/CT'), ('N', 'Non applicable')])),
                ('session_type', models.CharField(verbose_name='Session pour la formation', max_length=1, choices=[('1', 'Session unique'), ('2', '2 sessions'), ('0', 'Non applicable')])),
                ('ref_cpa_rof', models.CharField(verbose_name='Référence CP Année ROF', max_length=20, blank=True, null=True)),
                ('ref_si_scol', models.CharField(verbose_name='Référence SI Scol', max_length=20, blank=True, null=True)),
                ('progress_rule', models.CharField(verbose_name='Avancement de la saisie des règles', max_length=1, default='E', choices=[('E', 'En cours'), ('A', 'Achevée')])),
                ('progress_table', models.CharField(verbose_name='Avancement de la saisie du tableau MECC', max_length=1, default='E', choices=[('E', 'En cours'), ('A', 'Achevée')])),
                ('date_val_cmp', models.DateField(verbose_name='Date de validation en conseil de composante', blank=True, null=True)),
                ('date_res_des', models.DateField(verbose_name='Date de réserve DES', blank=True, null=True)),
                ('date_visa_des', models.DateField(verbose_name='Date de visa DES', blank=True, null=True)),
                ('date_val_cfvu', models.DateField(verbose_name='Date de validation en CFVU', blank=True, null=True)),
                ('supply_cmp', models.CharField(verbose_name='porteuse', max_length=3, blank=True)),
                ('n_train', models.IntegerField(verbose_name='Numéro de règle', null=True)),
                ('degree_type', models.ForeignKey(verbose_name='Type de diplôme', related_name='degree_type', to='degree.DegreeType')),
                ('institutes', models.ManyToManyField(to='institute.Institute')),
                ('resp_formations', models.ManyToManyField(to='adm.MeccUser')),
            ],
        ),
        migrations.AddField(
            model_name='specificparagraph',
            name='training',
            field=models.ForeignKey(to='training.Training'),
        ),
        migrations.AddField(
            model_name='additionalparagraph',
            name='training',
            field=models.ForeignKey(to='training.Training'),
        ),
    ]
