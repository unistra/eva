from io import BytesIO
from itertools import groupby

import xlsxwriter
from bs4 import BeautifulSoup
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django_cas.decorators import login_required

from mecc.decorators import group_required, profile_or_group_required
from mecc.decorators import has_cmp
from ..degree.models import DegreeType
from ..files.models import FileUpload
from ..institute.models import Institute
from ..rules.models import Rule
from ..training.models import Training, SpecificParagraph, AdditionalParagraph
from ..utils.pdfs import derogations, setting_up_pdf, NumberedCanvas
from ..utils.queries import currentyear
from ..years.models import InstituteYear, UniversityYear


@login_required
@group_required('DES1', 'VP')
def general_dashboard(request, template='dashboards/general_dashboard.html'):
    data = {}
    supply_filter = []
    cfvu_entries = []
    institutes_data = []
    # objects needed
    try:
        uy = UniversityYear.objects.get(is_target_year=True)
        if uy.date_validation:
            iy = InstituteYear.objects.filter(
                code_year=uy.code_year, date_expected_MECC__gt=uy.date_expected)
            institutes = Institute.objects.filter(
                training__code_year=uy.code_year).distinct()
        else:
            return render(request, 'msg.html', {'msg': _("Paramétrage de la date validation cadre en CFVU non effectuée")})

        for year in iy:
            inst = institutes.filter(pk=year.id_cmp).first()
            if inst:
                cfvu_entries.append(dict(domain=inst.field.name,
                                         cmp=inst.label,
                                         date=year.date_expected_MECC))

        institutes_with_rof_support = Institute.objects.filter(ROF_support=True).values_list('code', flat=True)

        t = Training.objects.filter(
            code_year=uy.code_year,
        )
        # ignore trainings disabled during ROF sync (cf di/mecc#124)
        t = t.exclude(
            Q(
                degree_type__ROF_code='EA',
                is_existing_rof=False)
            | Q(
                supply_cmp__in=institutes_with_rof_support,
                is_existing_rof=False)
        )
        t_eci = t.filter(MECC_type='E')
        t_cc_ct = t.filter(MECC_type='C')

        # get institutes who are supplier for a training
        for training in t:
            if training.supply_cmp in institutes.values_list('code', flat=True):
                supply_filter.append(training.supply_cmp)

        supply_institutes = institutes.filter(
            code__in=supply_filter).distinct()
        doc_cadre = FileUpload.objects.filter(object_id=uy.id).first()
        institutes_letters = FileUpload.objects.filter(object_id__in=institutes.values_list(
            'pk', flat=True), additional_type="letter_%s/%s" % (uy.code_year, uy.code_year + 1))
        rules = Rule.objects.filter(code_year=uy.code_year).filter(
            is_edited__in=('O', 'X')).order_by('display_order')

        t_uncompleted = t.filter(
            progress_rule="E") | t.filter(progress_table="E")
        t_completed_no_validation = t.filter(
            progress_rule="A", progress_table="A", date_val_cmp__isnull=True)
        t_validated_des_waiting = t.filter(
            date_val_cmp__isnull=False, date_visa_des__isnull=True)
        t_validated_no_cfvu_waiting = t.filter(
            date_val_cmp__isnull=True) | t.filter(date_visa_des__isnull=True)
        t_validated_cfvu_waiting = t.filter(
            date_val_cmp__isnull=False, date_visa_des__isnull=False, date_val_cfvu__isnull=True)
        t_validated_cfvu = t.filter(date_val_cfvu__isnull=False)

        institutes_trainings_completed_no_validation = institutes.filter(code__in=t_completed_no_validation.values_list(
            'supply_cmp', flat=True)).exclude(code__in=t_uncompleted.values_list('supply_cmp', flat=True))
        institutes_trainings_waiting_cfvu = institutes.filter(code__in=t_validated_cfvu_waiting.values_list(
            'supply_cmp', flat=True)).exclude(code__in=t_validated_no_cfvu_waiting.values_list('supply_cmp', flat=True))

        for s in supply_institutes:
            institutes_data.append(dict(institute=s.label,
                                        t_count=t.filter(
                                            supply_cmp=s.code).count(),
                                        t_uncompleted_count=t_uncompleted.filter(
                                            supply_cmp=s.code).count(),
                                        t_completed_no_val_count=t_completed_no_validation.filter(
                                            supply_cmp=s.code).count(),
                                        t_validated_des_waiting_count=t_validated_des_waiting.filter(
                                            supply_cmp=s.code).count(),
                                        t_validated_cfvu_waiting_count=t_validated_cfvu_waiting.filter(
                                            supply_cmp=s.code).count(),
                                        t_validated_cfvu_count=t_validated_cfvu.filter(
                                            supply_cmp=s.code).count(),
                                        ))

        derogations = SpecificParagraph.objects.filter(code_year=uy.code_year)

        d = []
        topten_d = []
        cmp_count = {}

        for e in derogations:
            d.append(dict(rule=Rule.objects.get(
                id=e.rule_gen_id).n_rule, cmp=e.training.supply_cmp))

        id_rules = [y.get('rule') for y in d]
        s = sorted(d, key=lambda d: d['rule'])
        g = groupby(s, lambda d: d['rule'])
        grouped_rules = []

        for k, v in g:
            grouped_rules.append(list(v))

        for item in grouped_rules:
            elm = set([(e['cmp'], e['rule']) for e in item])
            rule = set([(e['rule']) for e in item])
            for r in enumerate(rule):
                cmp_count.update({r[1]: len(elm)})

        rules_count = {e: id_rules.count(e) for e in id_rules}
        rules_sorted = sorted(
            rules_count, key=rules_count.get, reverse=True)[:10]

        for r in rules_sorted:
            topten_d.append(
                dict(rule=Rule.objects.get(n_rule=r, code_year=uy.code_year),
                     nb_derog=rules_count[r],
                     nb_cmp=cmp_count[r]))

        # set datas for view
        data['institutes_counter'] = supply_institutes.count()
        data['trainings_counter'] = t.count()
        data['trainings_eci_counter'] = t_eci.count()
        data['trainings_cc_ct_counter'] = t_cc_ct.count()
        data['institutes'] = supply_institutes
        data['rules'] = rules
        data['rules_counter'] = rules.count()
        data['doc_cadre'] = doc_cadre
        data['university_year'] = uy
        data['cfvu_entries'] = cfvu_entries
        data['trainings_uncompleted_counter'] = t_uncompleted.count()
        data['trainings_completed_no_validation_counter'] = t_completed_no_validation.count()
        data['institutes_trainings_completed_no_validation'] = institutes_trainings_completed_no_validation
        data['institutes_trainings_completed_no_validation_counter'] = institutes_trainings_completed_no_validation.count()
        data['trainings_validated_des_waiting_counter'] = t_validated_des_waiting.count()
        data['trainings_validated_cfvu_waiting_counter'] = t_validated_cfvu_waiting.count()
        data['trainings_validated_cfvu_counter'] = t_validated_cfvu.count()
        data['institutes_trainings_waiting_cfvu'] = institutes_trainings_waiting_cfvu
        data['institutes_trainings_waiting_cfvu_counter'] = institutes_trainings_waiting_cfvu.count()
        data['institutes_data'] = institutes_data
        data['institutes_letters'] = institutes_letters
        data['institutes_letters_counter'] = institutes_letters.count()
        data['topten_derog'] = topten_d
    except UniversityYear.DoesNotExist:
        return render(request, 'msg.html', {'msg': _("Initialisation de l'année non effectuée")})

    return render(request, template, data)


@login_required
@has_cmp
@profile_or_group_required(('DES1', 'RAC', 'DIRCOMP'), ('ECI'))
def institute_dashboard(request, code, template='dashboards/institute_dashboard.html'):
    data = {}
    supply_filter = []
    rules_filter = []
    cfvu_entries = []
    trainings_data = []
    # objects needed
    try:
        uy = UniversityYear.objects.get(is_target_year=True)
        if not uy.date_validation:
            iy = []
            # If we want a message instead of all
            # return render(request, 'msg.html', {
            #     'msg': _("Paramétrage de la date validation cadre en CFVU non effectuée")})
        else:
            iy = InstituteYear.objects.filter(
                code_year=uy.code_year, date_expected_MECC__gt=uy.date_validation)

        institute = Institute.objects.get(code=code)
        iycmp = InstituteYear.objects.get(
            code_year=uy.code_year, id_cmp=institute.pk)

        for year in iy:
            cfvu_entries.append(dict(domain=institute.field.name,
                                     cmp=institute.label, date=year.date_expected_MECC))

        t = Training.objects.filter(code_year=uy.code_year, supply_cmp=code)
        t_eci = t.filter(MECC_type='E')
        t_cc_ct = t.filter(MECC_type='C')

        # get institutes who are supplier for a training
        for training in t:

            if training.supply_cmp in code:
                supply_filter.append(training.supply_cmp)

        doc_cadre = FileUpload.objects.filter(object_id=uy.id).first()

        rules = Rule.objects.filter(code_year=uy.code_year).filter(
            is_edited__in=('O', 'X'),
            degree_type__in=t.values_list('degree_type', flat=True)).distinct()

        rules.order_by('display_order')

        t_uncompleted = t.filter(
            progress_rule="E") | t.filter(progress_table="E")
        t_completed_no_validation = t.filter(
            progress_rule="A", progress_table="A", date_val_cmp__isnull=True)
        t_validated_des_waiting = t.filter(
            date_val_cmp__isnull=False, date_visa_des__isnull=True)
        t_validated_no_cfvu_waiting = t.filter(
            date_val_cmp__isnull=True) | t.filter(date_visa_des__isnull=True)
        t_validated_cfvu_waiting = t.filter(
            date_val_cmp__isnull=False, date_visa_des__isnull=False, date_val_cfvu__isnull=True)
        t_validated_cfvu = t.filter(date_val_cfvu__isnull=False)

        trainings_data = t.values('degree_type').annotate(t_count=Count('pk'))

        derogations = SpecificParagraph.objects.filter(
            training__supply_cmp=code, code_year=uy.code_year)

        d = []
        topten_d = []
        train_count = {}

        for e in derogations:
            d.append(dict(rule=Rule.objects.get(
                id=e.rule_gen_id).n_rule, train=e.training.id))

        id_rules = [y.get('rule') for y in d]
        s = sorted(d, key=lambda d: d['rule'])
        g = groupby(s, lambda d: d['rule'])
        grouped_rules = []

        for k, v in g:
            grouped_rules.append(list(v))

        for item in grouped_rules:
            elm = set([(e['train'], e['rule']) for e in item])
            rule = set([(e['rule']) for e in item])
            for r in enumerate(rule):
                train_count.update({r[1]: len(elm)})

        rules_count = {e: id_rules.count(e) for e in id_rules}
        rules_sorted = sorted(
            rules_count, key=rules_count.get, reverse=True)

        for r in rules_sorted:
            topten_d.append(
                dict(
                    rule=Rule.objects.get(n_rule=r, code_year=uy.code_year),
                    nb_derog=rules_count[r],
                    nb_formations=train_count[r]))

        # set datas for view
        data['institute'] = institute
        data['trainings_counter'] = t.count()
        data['trainings_eci_counter'] = t_eci.count()
        data['trainings_cc_ct_counter'] = t_cc_ct.count()
        data['rules'] = rules
        data['rules_counter'] = rules.count()
        data['doc_cadre'] = doc_cadre
        data['university_year'] = uy
        data['university_year_cmp'] = iycmp
        data['cfvu_entries'] = cfvu_entries
        data['institute_cfvu_counter'] = iy.count() if iy else 0
        data['trainings_uncompleted_counter'] = t_uncompleted.count()
        data['trainings_completed_no_validation_counter'] = t_completed_no_validation.count()
        data['trainings_validated_des_waiting_counter'] = t_validated_des_waiting.count()
        data['trainings_validated_cfvu_waiting_counter'] = t_validated_cfvu_waiting.count()
        data['trainings_validated_cfvu_counter'] = t_validated_cfvu.count()
        data['institute_data'] = trainings_data
        data['trainings_eci_counter'] = t_eci.count()
        data['trainings_cc_ct_counter'] = t_cc_ct.count()
        data['topten_derog'] = topten_d
        data['first_cfvu'] = uy.date_expected

        for td in trainings_data:
            td['degree_type_label'] = DegreeType.objects.get(
                id=td['degree_type'])
            td['t_eci_count'] = t_eci.filter(
                degree_type=td['degree_type']).count()
            td['t_cc_ct_count'] = t_cc_ct.filter(
                degree_type=td['degree_type']).count()

        return render(request, template, data)

    except UniversityYear.DoesNotExist:
        return render(request, 'msg.html', {'msg': _("Initialisation de l'année non effectuée")})


@login_required
@group_required('DES1', 'VP')
def general_derog_pdf(request):
    year = currentyear().code_year
    title = "MECC - %s - %s" % (
        year, year)
    response, doc = setting_up_pdf(title, margin=42)
    story = derogations(title, year)
    doc.build(story, canvasmaker=NumberedCanvas)

    return response


def training_is_excluded_by_rof_sync(training, institute):
    if institute.ROF_support and training.is_existing_rof is False:
        return True
    if training.degree_type.ROF_code == 'EA' and training.is_existing_rof is False:
        return True
    return False


@login_required
@group_required('DES1', 'VP')
def derogations_export_excel(request):

    # create workbook with worksheet
    doc_name = "eva_derogations_%s" % currentyear().code_year
    output = BytesIO()
    book = xlsxwriter.Workbook(output)
    sheet = book.add_worksheet(_('Dérogations'))

    # Formats
    bold = book.add_format({'bold': True})
    main = book.add_format()
    main.set_align('left')

    # Headers rows
    headers = [
        _('Régime'),
        _('ID règle'),
        _('Nom de règle'),
        _('ID alinéa'),
        _('Composante'),
        _('ID formation'),
        _('Intitulé formation'),
        _('Dérogation'),
        _('Motivation')
    ]

    # Datas fetching
    data = []
    derogations = SpecificParagraph.objects.filter(
        code_year=currentyear().code_year
    ).select_related('training__degree_type')

    if derogations:
        for v in derogations:
            institute = Institute.objects.get(code=v.training.supply_cmp)
            if not training_is_excluded_by_rof_sync(v.training, institute):
                clean_paragraph = BeautifulSoup(
                    v.text_specific_paragraph, 'html.parser').get_text()
                clean_motivation = BeautifulSoup(
                    v.text_motiv, 'html.parser').get_text()

                rule = Rule.objects.get(id=v.rule_gen_id)

                if rule:
                    if rule.is_eci and rule.is_ccct:
                        regime = "ECI et CC/CT"
                    elif rule.is_eci:
                        regime = "ECI"
                    elif rule.is_ccct:
                        regime = "CC/CT"
                else:
                    regime = ""

                data.append([regime,
                             v.rule_gen_id,
                             rule.label,
                             v.paragraph_gen_id,
                             institute.label,
                             v.training.pk,
                             v.training.label,
                             " ".join(clean_paragraph.split()),
                             " ".join(clean_motivation.split())
                             ])

                sheet.set_column('A:A', 15)
                sheet.set_column('B:C', 14)
                sheet.set_column('E:E', 55)
                sheet.set_column('F:F', 12)
                sheet.set_column('G:G', 45)
                sheet.set_column('H:I', 80)

                row = 0
                for i, header in enumerate(headers):
                    sheet.write(row, i, header, bold)
                row += 1

                for r, columns in enumerate(data):
                    for column, cell_data in enumerate(columns):
                        sheet.write(row, column, cell_data, main)
                    row += 1
    else:
        sheet.write('B1', _('Pas de données'), bold)

    book.close()
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % doc_name
    return response


@login_required
@group_required('DES1', 'VP')
def alineas_export_excel(request):

    # create workbook with worksheet
    doc_name = "eva_alineas_%s" % currentyear().code_year
    output = BytesIO()
    book = xlsxwriter.Workbook(output)
    sheet = book.add_worksheet(_('Alineas'))

    # Formats
    bold = book.add_format({'bold': True})
    main = book.add_format()
    main.set_align('left')

    # Headers rows
    headers = [
        _('Régime'),
        _('ID règle'),
        _('Nom de règle'),
        _('Composante'),
        _('ID formation'),
        _('Intitulé formation'),
        _('Alinéa additionnel')

    ]

    # Datas fetching
    alineas = AdditionalParagraph.objects.filter(
        code_year=currentyear().code_year
    ).select_related('training__degree_type')

    if alineas:
        clean_additionals = ""
        data = []
        for a in alineas:
            institute = Institute.objects.get(code=a.training.supply_cmp)
            if not training_is_excluded_by_rof_sync(a.training, institute):
                rule = Rule.objects.get(id=a.rule_gen_id)

                clean_additionals = BeautifulSoup(
                    a.text_additional_paragraph, 'html.parser').get_text()

                if rule:
                    if rule.is_eci and rule.is_ccct:
                        regime = "ECI et CC/CT"
                    elif rule.is_eci:
                        regime = "ECI"
                    elif rule.is_ccct:
                        regime = "CC/CT"
                else:
                    regime = ""

                data.append([regime,
                             a.rule_gen_id,
                             rule.label,
                             institute.label,
                             a.training.pk,
                             a.training.label,
                             " ".join(clean_additionals.split())
                             ])

        sheet.set_column('A:B', 10)
        sheet.set_column('C:D', 75)
        sheet.set_column('E:E', 12)
        sheet.set_column('F:F', 55)
        sheet.set_column('G:G', 65)

        row = 0
        for i, header in enumerate(headers):
            sheet.write(row, i, header, bold)
        row += 1

        for r, columns in enumerate(data):
            for column, cell_data in enumerate(columns):
                sheet.write(row, column, cell_data, main)
            row += 1
    else:
        sheet.write('B1', _('Pas de données'), bold)

    book.close()
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % doc_name
    return response


@login_required
@has_cmp
@profile_or_group_required(('DES1', 'RAC', 'DIRCOMP'), ('ECI'))
def institute_derogations_export_excel(request, code):
    # TODO: refactor with derogations_export_excel
    # create workbook with worksheet
    doc_name = "eva_derogations_%s" % currentyear().code_year
    output = BytesIO()
    book = xlsxwriter.Workbook(output)
    sheet = book.add_worksheet(_('Dérogations'))

    # Formats
    bold = book.add_format({'bold': True})
    main = book.add_format()
    main.set_align('left')

    # Headers rows
    headers = [
        _('Régime'),
        _('ID règle'),
        _('Nom de règle'),
        _('ID alinéa'),
        _('Composante'),
        _('ID formation'),
        _('Intitulé formation'),
        _('Dérogation'),
        _('Motivation')
    ]

    # Datas fetching
    data = []
    derogations = SpecificParagraph.objects.filter(
        code_year=currentyear().code_year, training__supply_cmp=code)

    if derogations:
        for v in derogations:
            cmp = Institute.objects.get(code=v.training.supply_cmp).label
            clean_paragraph = BeautifulSoup(
                v.text_specific_paragraph, 'html.parser').get_text()
            clean_motivation = BeautifulSoup(
                v.text_motiv, 'html.parser').get_text()

            rule = Rule.objects.get(id=v.rule_gen_id)

            if rule:
                if rule.is_eci and rule.is_ccct:
                    regime = "ECI et CC/CT"
                elif rule.is_eci:
                    regime = "ECI"
                elif rule.is_ccct:
                    regime = "CC/CT"
            else:
                regime = ""

            data.append([regime,
                         v.rule_gen_id,
                         rule.label,
                         v.paragraph_gen_id,
                         cmp,
                         v.training.pk,
                         v.training.label,
                         " ".join(clean_paragraph.split()),
                         " ".join(clean_motivation.split())
                         ])

            sheet.set_column('A:A', 15)
            sheet.set_column('B:C', 14)
            sheet.set_column('E:E', 55)
            sheet.set_column('F:F', 12)
            sheet.set_column('G:G', 45)
            sheet.set_column('H:I', 80)

            row = 0
            for i, header in enumerate(headers):
                sheet.write(row, i, header, bold)
            row += 1

            for r, columns in enumerate(data):
                for column, cell_data in enumerate(columns):
                    sheet.write(row, column, cell_data, main)
                row += 1
    else:
        sheet.write('B1', _('Pas de données'), bold)

    book.close()
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % doc_name
    return response


@login_required
@has_cmp
@profile_or_group_required(('DES1', 'RAC', 'DIRCOMP'), ('ECI'))
def institute_alineas_export_excel(request, code):
    # TODO: refactor with alineas_export_excel
    # create workbook with worksheet
    #

    doc_name = "eva_alineas_%s" % currentyear().code_year
    output = BytesIO()
    book = xlsxwriter.Workbook(output)
    sheet = book.add_worksheet(_('Alineas'))

    # Formats
    bold = book.add_format({'bold': True})
    main = book.add_format()
    main.set_align('left')

    # Headers rows
    headers = [
        _('Régime'),
        _('ID règle'),
        _('Nom de règle'),
        _('Composante'),
        _('ID formation'),
        _('Intitulé formation'),
        _('Alinéa additionnel')

    ]

    # Datas fetching

    data = []
    alineas = AdditionalParagraph.objects.filter(
        code_year=currentyear().code_year,
        training__supply_cmp=code)

    if alineas:
        clean_additionals = ""

        for a in alineas:

            rule = Rule.objects.get(id=a.rule_gen_id)
            cmp = a.training.supply_cmp_label

            clean_additionals = BeautifulSoup(
                a.text_additional_paragraph, 'html.parser').get_text()

            if rule:
                if rule.is_eci and rule.is_ccct:
                    regime = "ECI et CC/CT"
                elif rule.is_eci:
                    regime = "ECI"
                elif rule.is_ccct:
                    regime = "CC/CT"
            else:
                regime = ""

            data.append([regime,
                         a.rule_gen_id,
                         rule.label,
                         cmp,
                         a.training.pk,
                         a.training.label,
                         " ".join(clean_additionals.split())
                         ])

        sheet.set_column('A:B', 10)
        sheet.set_column('C:D', 75)
        sheet.set_column('E:E', 12)
        sheet.set_column('F:F', 55)
        sheet.set_column('G:G', 65)

        row = 0
        for i, header in enumerate(headers):
            sheet.write(row, i, header, bold)
        row += 1

        for r, columns in enumerate(data):
            for column, cell_data in enumerate(columns):
                sheet.write(row, column, cell_data, main)
            row += 1
    else:
        sheet.write('B1', _('Pas de données'), bold)

    book.close()
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % doc_name
    return response
