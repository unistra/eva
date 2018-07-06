# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('id_attached', models.IntegerField(verbose_name='ID objet de rattachement (contexte)')),
                ('session', models.CharField(verbose_name="Session de l'épreuve", max_length=1, choices=[('1', 'Session unique'), ('2', '2 sessions')])),
                ('_id', models.IntegerField(verbose_name="ID interne de l'épreuve")),
                ('regime', models.CharField(verbose_name="Régime de l'épreuve", max_length=1, choices=[('E', 'ECI'), ('C', 'CC/CT')])),
                ('type_exam', models.CharField(verbose_name='', max_length=1, choices=[('E', 'Ecrit'), ('O', 'Oral'), ('A', 'Autre')])),
                ('label', models.CharField(verbose_name="Intitulé de l'épreuve", max_length=200)),
                ('additionnal_info', models.CharField(verbose_name='Complément d’information sur l’épreuve', max_length=200, blank=True, null=True)),
                ('exam_duration_h', models.IntegerField(verbose_name='Durée de l’épreuve-Heures', blank=True, null=True)),
                ('exam_duration_m', models.IntegerField(verbose_name='Durée de l’épreuve-Minutes', blank=True, null=True)),
                ('convocation', models.CharField(verbose_name='Convocation', max_length=1, blank=True, null=True, choices=[('O', 'Oui'), ('N', 'Non'), ('X', None)])),
                ('type_ccct', models.CharField(verbose_name='Type CC ou CT', max_length=1, blank=True, null=True, choices=[('C', 'CC'), ('T', 'CT'), ('X', None)])),
                ('coefficient', models.DecimalField(verbose_name="Coefficient de l'épreuve", blank=True, null=True, max_digits=4, decimal_places=2)),
                ('eliminatory_grade', models.IntegerField(verbose_name="Note seuil de l'épreuve", blank=True, null=True)),
                ('is_session_2', models.NullBooleanField(verbose_name='Témoin Report session 2')),
                ('threshold_session_2', models.IntegerField(verbose_name='Seuil de report session 2', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ObjectsLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('id_training', models.IntegerField(verbose_name='ID interne de la formation')),
                ('id_parent', models.IntegerField(verbose_name='ID objet père')),
                ('id_child', models.IntegerField(verbose_name='ID objet fils')),
                ('order_in_child', models.IntegerField(verbose_name="Numéro d'ordre fils (au sein du père)")),
                ('n_train_child', models.IntegerField(verbose_name='ID interne de la formation d’origine du fils')),
                ('nature_child', models.CharField(verbose_name='Nature du fils', max_length=3, choices=[('INT', 'ID formation d’origine = ID formation contexte'), ('EXT', 'ID formation d’origine ≠ ID formation contexte')])),
                ('coefficient', models.DecimalField(verbose_name='Coefficient de l’objet (au sein de ce père)', blank=True, null=True, max_digits=4, decimal_places=2)),
                ('eliminatory_grade', models.IntegerField(verbose_name='Note seuil sur cet objet (au sein de ce père)', blank=True, null=True, default=None)),
                ('is_imported', models.NullBooleanField(verbose_name='Est importé')),
            ],
        ),
        migrations.CreateModel(
            name='StructureObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('auto_id', models.IntegerField(verbose_name="ID automatique de l'objet", blank=True)),
                ('nature', models.CharField(verbose_name="Type d'objet", max_length=2, choices=[('SE', 'Semestre'), ('UE', 'UE'), ('EC', 'Élément constitutif'), ('ST', 'Stage'), ('PT', 'Projet tuteuré'), ('OP', 'Option'), ('LI', 'Liste')])),
                ('owner_training_id', models.IntegerField(verbose_name='ID de la formation propriétaire')),
                ('cmp_supply_id', models.CharField(verbose_name='ID de la composante porteuse de la formation propriétaire', max_length=3)),
                ('regime', models.CharField(verbose_name='Régime de l’objet (hérité de la formation propriétaire)', max_length=1, choices=[('E', 'ECI'), ('C', 'CC/CT')])),
                ('session', models.CharField(verbose_name='Session pour la formation (hérité de la formation propriétaire)', max_length=1, choices=[('1', 'Session unique'), ('2', '2 sessions')])),
                ('label', models.CharField(verbose_name="Intitulé de l'objet", max_length=200)),
                ('is_in_use', models.BooleanField(verbose_name='En service', default=True)),
                ('period', models.CharField(verbose_name="Période de l'objet", max_length=1, choices=[('I', 'Semestre impair'), ('P', 'Semestre pair'), ('A', 'Année')])),
                ('ECTS_credit', models.IntegerField(verbose_name='Crédits ECTS', blank=True, null=True)),
                ('RESPENS_id', models.CharField(verbose_name="Responsable d'enseignement", max_length=85, blank=True, null=True)),
                ('mutual', models.BooleanField(verbose_name='Mutualisé')),
                ('ROF_ref', models.CharField(verbose_name="Référence de l'objet ROF", max_length=20, blank=True, null=True)),
                ('ROF_code_year', models.CharField(verbose_name="Année de l'objet ROF", max_length=20, blank=True, null=True)),
                ('ROF_nature', models.CharField(verbose_name="Type de l'objet ROF", max_length=50, blank=True, null=True)),
                ('ROF_supply_program', models.CharField(verbose_name="Programme porteur de l'objet ROF", max_length=50, blank=True, null=True)),
                ('ref_si_scol', models.CharField(verbose_name='Référence SI Scolarité', max_length=20, blank=True, null=True)),
                ('external_name', models.CharField(verbose_name='Intervenant exterieur', max_length=240, blank=True, null=True)),
            ],
        ),
    ]
