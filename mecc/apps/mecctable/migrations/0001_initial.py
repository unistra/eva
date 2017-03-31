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
                ('session', models.CharField(choices=[('1', 'Session unique'), ('2', '2 sessions')], max_length=1, verbose_name="Session de l'épreuve")),
                ('_id', models.IntegerField(verbose_name="ID interne de l'épreuve")),
                ('regime', models.CharField(choices=[('E', 'ECI'), ('C', 'CC/CT')], max_length=1, verbose_name="Régime de l'épreuve")),
                ('type_exam', models.CharField(choices=[('E', 'Écrit'), ('O', 'Oral'), ('A', 'Autre')], max_length=1, verbose_name='')),
                ('label', models.CharField(max_length=25, verbose_name="Intitulé de l'épreuve")),
                ('additionnal_info', models.CharField(max_length=200, verbose_name='Complément d’information sur l’épreuve')),
                ('exam_duration_h', models.IntegerField(verbose_name='Durée de l’épreuve-Heures')),
                ('exam_duration_m', models.IntegerField(verbose_name='Durée de l’épreuve-Minutes')),
                ('convocation', models.CharField(choices=[('O', 'Oui'), ('N', 'Aucun(e)'), ('X', None)], max_length=1, verbose_name='Convocation')),
                ('type_ccct', models.CharField(choices=[('C', 'CC'), ('T', 'CT'), ('X', None)], max_length=1, verbose_name='Type CC ou CT')),
                ('coefficient', models.DecimalField(max_digits=2, verbose_name="Coefficient de l'épreuve", decimal_places=1)),
                ('eliminatory_grade', models.IntegerField(null=True, verbose_name="Note seuil de l'épreuve")),
                ('is_session_2', models.BooleanField(verbose_name='Témoin Report session 2')),
                ('threshold_session_2', models.IntegerField(verbose_name='Seuil de report session 2')),
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
                ('nature_child', models.CharField(choices=[('INT', 'ID formation d’origine = ID formation contexte'), ('EXT', 'ID formation d’origine ≠ ID formation contexte')], max_length=3, verbose_name='Nature du fils')),
                ('coefficient', models.DecimalField(max_digits=4, null=True, blank=True, verbose_name='Coefficient de l’objet (au sein de ce père)', decimal_places=2)),
                ('eliminatory_grade', models.IntegerField(null=True, blank=True, verbose_name='Note seuil sur cet objet (au sein de ce père)', default=None)),
            ],
        ),
        migrations.CreateModel(
            name='StructureObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code_year', models.IntegerField(verbose_name='Code année')),
                ('auto_id', models.IntegerField(verbose_name="ID automatique de l'objet", blank=True)),
                ('nature', models.CharField(choices=[('SE', 'Semestre'), ('UE', 'UE'), ('EC', 'Élément constitutif'), ('ST', 'Stage'), ('PT', 'Projet tuteuré'), ('OP', 'Option'), ('LI', 'Liste')], max_length=2, verbose_name="Type d'objet")),
                ('owner_training_id', models.IntegerField(verbose_name='ID de la formation propriétaire')),
                ('cmp_supply_id', models.CharField(max_length=3, verbose_name='ID de la composante porteuse de la formation propriétaire')),
                ('regime', models.CharField(choices=[('E', 'ECI'), ('C', 'CC/CT')], max_length=1, verbose_name='Régime de l’objet (hérité de la formation propriétaire)')),
                ('session', models.CharField(choices=[('1', 'Session unique'), ('2', '2 sessions')], max_length=1, verbose_name='Sessions pour la formation (hérité de la formation propriétaire)')),
                ('label', models.CharField(max_length=120, verbose_name="Intitulé de l'objet")),
                ('is_in_use', models.BooleanField(verbose_name='En service', default=True)),
                ('period', models.CharField(choices=[('I', 'Semestre impair'), ('P', 'Semestre pair'), ('A', 'Année')], max_length=1, verbose_name="Période de l'objet")),
                ('ECTS_credit', models.IntegerField(null=True, blank=True, verbose_name='Crédits ECTS')),
                ('RESPENS_id', models.CharField(verbose_name="Responsable d'enseignement", max_length=85, blank=True, null=True)),
                ('mutual', models.BooleanField(verbose_name='Mutualisé')),
                ('ROF_ref', models.CharField(verbose_name="Référence de l'objet ROF", max_length=20, blank=True, null=True)),
                ('ROF_code_year', models.IntegerField(null=True, blank=True, verbose_name="Année de l'objet ROF")),
                ('ROF_nature', models.CharField(choices=[('SE', 'Semestre'), ('UE', 'UE'), ('EC', 'Élément constitutif'), ('ST', 'Stage'), ('PT', 'Projet tuteuré'), ('OP', 'Option'), ('LI', 'Liste')], max_length=2, blank=True, null=True, verbose_name="Type de l'objet ROF")),
                ('ROF_supply_program', models.CharField(verbose_name="Programme porteur de l'objet ROF", max_length=20, blank=True, null=True)),
                ('ref_si_scol', models.CharField(verbose_name='Référence SI Scolarité', max_length=20, blank=True, null=True)),
            ],
        ),
    ]
