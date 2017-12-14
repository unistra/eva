import re
from itertools import groupby

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from reportlab.platypus import Paragraph, Spacer, Image, SimpleDocTemplate, \
    Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape, A2


from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import ObjectsLink, StructureObject, Exam
from mecc.apps.rules.models import Rule, Paragraph as ParagraphRules
from mecc.apps.training.models import Training, SpecificParagraph
from mecc.apps.utils.queries import rules_degree_for_year, currentyear, \
    get_mecc_table_order
from mecc.apps.years.models import UniversityYear
from reportlab.platypus.flowables import Flowable


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='Bullet_1', bulletIndent=25, bulletText="•"))
styles.add(ParagraphStyle(name='CenterBalek', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='CenterSmall', alignment=TA_CENTER, fontSize=9))
logo_uds = Image('mecc/static/img/signature_uds_02.png', 160, 60)


class verticalText(Flowable):
    '''
    Rotates a text in a table cell.
    '''

    def __init__(self, text):
        Flowable.__init__(self)
        self.text = text

    def draw(self):
        canvas = self.canv
        canvas.rotate(90)
        fs = canvas._fontsize
        canvas.translate(1, -fs / 1.2)  # canvas._leading?
        canvas.drawString(0, 0, self.text)

    def wrap(self, aW, aH):
        canv = self.canv
        fn, fs = canv._fontname, canv._fontsize
        return canv._leading, 1 + canv.stringWidth(self.text, fn, fs)


def setting_up_pdf(title, margin=72, portrait=True):
    """
    Create the HttpResponse object with the appropriate PDF headers.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ('filename="%s.pdf"' % title)
    page_size = A4 if portrait else landscape(A4)
    doc = SimpleDocTemplate(response, pagesize=page_size,
                            topMargin=margin, bottomMargin=18)
    return response, doc


def watermark_do_not_distribute(canvas, doc):
    """
    Add a watermark NE PAS DIFFUSER
    """
    canvas.saveState()
    canvas.setFont("Helvetica", 45)
    canvas.setFillGray(0.80)
    canvas.rotate(45)
    canvas.drawCentredString(550, 100, "NE PAS DIFFUSER")
    canvas.restoreState()


def custom_watermark(canvas, watermak_string, font='Helvetica', font_size=45, position_x=550, position_y=100, rotation=45):
    """
    Add a custom watermark
    """
    canvas.saveState()
    canvas.setFont(font, font_size)
    canvas.setFillGray(0.80)
    canvas.rotate(rotation)
    canvas.drawCentredString(position_x, position_y, watermak_string)
    canvas.restoreState()


def canvas_for_mecctable(canvas, doc):
    """
    canvas for mecctable: set to landscape with watermark
    """
    custom_watermark(canvas, "Document intermédiaire")


def canvas_for_preview_mecctable(canvas, doc):
    """
    canvas for preview mecctable
    """
    custom_watermark(canvas, "Prévisualisation", rotation=40,
                     font_size=40, position_x=500, position_y=-75)


class NumberedCanvas_landscape(canvas.Canvas):
    """
    Canvas allowing to count pages
    """

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count, position_x=285, position_y=5):
        """
        drow page number with custom format and position
        """
        if page_count > 0:
            self.setFillGray(0.2)
            self.setFont("Helvetica", 8.5)
            self.drawRightString(
                position_x * mm, position_y * mm, "Page %d/%d" %
                (self._pageNumber, page_count))


class NumberedCanvas(canvas.Canvas):
    """
    Canvas allowing to count pages
    """

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count, position_x=205, position_y=5):
        """
        drow page number with custom format and position
        """
        if page_count > 0:
            self.setFillGray(0.2)
            self.setFont("Helvetica", 8.5)
            self.drawRightString(
                position_x * mm, position_y * mm, "Page %d/%d" %
                (self._pageNumber, page_count))


def block_rules(title, rules, story, styled=True):
    style = [
        ('BOX', (0, 1), (-1, 1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
    ]
    if len(rules) > 0:
        t = [
            [""],
            [Paragraph(title, styles["Normal"])]
        ]

        table = Table(t, colWidths=(550), style=style if styled else [])
        story.append(table)

        for paragraph in rules:
            add_paragraph(paragraph, story)

    return story


def list_of_parag_with_bullet(text):
    """
    Return correct string in order to be displayed as list
    """
    reg = re.compile(r'>(.*?)</(p|li)>')
    r = reg.findall(text.replace('r\\n\\', '<br><\\br>'))
    _list = []
    for t, v in r:
        if v == 'li':
            _list.append(Paragraph(
                "<para leftIndent=40>%s</para>" % (
                    t), styles['Bullet_1']))
        else:
            _list.append(Paragraph(
                "<para >%s</para>" % (
                    t), styles['Justify']))
    return _list


def add_simple_paragraph(story, rule, sp, ap):
    """
    print content of paragraph with Specific and additionnel values in state of
    standard values
    """

    def append_text(story, text, style, special=False, spacer=6):
        """
        print content of paragraph or list with bullet
        """
        # REGEX ME !
        reg = re.compile(r'>(.*?)</(p|li)>')
        # r_p = re.compile(r'<p>(.*?)</p>')
        # r_ul = re.compile(r'<ul>(.*?)</ul>')
        # r_ol = re.compile(r'<ol>(.*?)</ol>')
        # r_li = re.compile(r'<li>(.*?)</li>')

        r = reg.findall(text.replace('r\\n\\', '<br><\\br>'))

        if special == 'motiv':
            story.append(
                Paragraph(
                    "<para textColor=red leftIndent=20><u>Motifs de la dérogation</u> :\
                    </para>", styles["Justify"]))
        for t, v in r:
            if v == 'li':
                story.append(Paragraph(
                    "<para %s leftIndent=40>%s</para>" % (
                        style, t), styles['Bullet_1']))
            else:
                story.append(Paragraph(
                    "<para %s leftIndent=20>%s</para>" % (
                        style, t), styles['Justify']))
        story.append(Spacer(0, spacer))

    story.append(Spacer(0, 6))
    story.append(Paragraph("<para fontSize=11><strong>%s</strong></para>\
        " % rule.label, styles['Normal']))
    story.append(Spacer(0, 6))

    paragraphs = ParagraphRules.objects.filter(Q(rule=rule))

    for p in paragraphs:
        if p.is_in_use:
            if p.id in [e.paragraph_gen_id for e in sp]:
                text = sp.filter(paragraph_gen_id=p.id).first(
                ).text_specific_paragraph
                append_text(
                    story, text,
                    "textColor=blue", spacer=0)
                text = sp.filter(paragraph_gen_id=p.id).first().text_motiv
                style = 'textColor=red'
                append_text(story, text, style, special="motiv")
            else:
                text = p.text_standard
                style = ''
                append_text(story, text, style)

    if ap:
        text = ap.get(rule_gen_id=rule.n_rule).text_additional_paragraph
        style = "textColor=green"
        append_text(story, text, style)


def add_paragraph(e, story, sp=None, ap=None, styled=True):
    t = [["", ""]]

    t.append([
        Paragraph("<para textColor=darkblue><b>%s</b></para>" % e.label,
                  styles['Normal']),
        Paragraph("<para align=right textColor=darkblue fontSize=8>\
                  ID %s</para>" % e.pk, styles['Normal']) if styled else ' '])

    paragraphs = ParagraphRules.objects.filter(Q(rule=e))
    for p in paragraphs:
        if p.is_in_use:
            txt = ''
            derog = _("Dérogation <br></br> possible") if \
                p.is_interaction else ''
            if p.is_interaction:
                txt = derog

            t.append(
                [
                    list_of_parag_with_bullet(p.text_standard),
                    Paragraph("<para align=right textColor=grey fontSize=8>\
                        %s</para>" % txt, styles['Normal'])
                ]
            )

    table = Table(t, colWidths=(400, 125), style=[
        ('VALIGN', (0, 0), (0, -1), 'TOP'),
        ('VALIGN', (1, 1), (1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 2), (-1, -1), 0.75, colors.lightgrey),

    ])
    story.append(table)
    return story


def preview_mecctable_story(training, story=[]):
    """
    Story for previewing mecctable
    """
    import itertools

    # ############ USEFULL STUFF ################################
    current_year = currentyear().code_year
    # struct_object = StructureObject.objects.filter(
    #     id__in=[e.id_child for e in object_links])
    current_structures = StructureObject.objects.filter(code_year=current_year)
    current_links = ObjectsLink.objects.filter(code_year=current_year)
    current_exams = Exam.objects.filter(code_year=current_year)
    root_link = current_links.filter(
        id_parent='0', id_training=training.id).order_by(
        'order_in_child').distinct()

    links = get_mecc_table_order([e for e in root_link], [],
                                 current_structures, current_links,
                                 current_exams, all_exam=True)

    # ############ TABLE STRUCUTURE ################################

    # Title
    red_title = "PREVISUALISATION du TABLEAU"

    # - Ugly but tables are almost always ugly
    big_table = [['OBJETS', '', '', '', '', '', 'EPREUVES'],
                 ['Intitulé', 'Responsable', Paragraph(
                     '<para textColor=steelblue><strong>Référence APOGEE \
                     <br></br><br></br> Référence ROF</strong></para>',
                     styles['CenterSmall']),
                  verticalText('Crédit ECTS'), verticalText('Coefficient'),
                  verticalText('Note seuil'), 'Session principale',
                     '', '', '', '', '', '', 'Session de rattrapage'],
                 ['Intitulé',
                  'Responsable',
                  'Référence APOGEE',
                  verticalText('Crédit ECTS'),
                  verticalText('Coefficient'),
                  verticalText('Note seuil'),
                  verticalText('Coefficient'),
                  'Intitulé',
                  verticalText('Type'),
                  verticalText('Durée'),
                  verticalText('Convocation'),
                  verticalText('Note seuil'),
                  verticalText(' Report session 2 '),
                  verticalText('Coefficient'),
                  'Intitulé',
                  verticalText('Type'),
                  verticalText('Durée'),
                  verticalText('Note seuil')],
                 ]

    col_width = [6 * cm, 2.25 * cm, 1.8 * cm, .6 * cm, .6 * cm, .6 * cm]
    widht_exam_1 = [0.85 * cm, 4 * cm, .6 *
                    cm, 1.1 * cm, .6 * cm, .7 * cm, .7 * cm, ]
    widht_exam_2 = [0.85 * cm, 4 * cm, .6 * cm, 1.1 * cm, .7 * cm]
    widht_exams = widht_exam_1
    widht_exams.extend(widht_exam_2)
    col_width.extend(widht_exam_1)
    col_width.extend(widht_exam_2)

    title_length = len(big_table)
    global count_row
    count_row = 2
    background_blue = []
    bold_text = []

    # ############ POPULATING TABLE ################################

    def write_the_table(what):
        """
        Recursively add data in strucuture
        """
        global count_row
        count_row += 1

        if what.get('rank') == 0:
            background_blue.append(count_row)
        if what.get('rank') == 1:
            bold_text.append(count_row)

        struct = what.get('structure')
        link = what.get('link')
        exams_1 = what.get('exams_1')
        exams_2 = what.get('exams_2')
        exams_empty = [['', '', '', '', '', '', '', '', '', '', '', '']]

        def write_exams(list_1, list_2):
            exam_table = []
            for ex_1, ex_2 in itertools.zip_longest(list_1, list_2):
                ex_1_table = [
                    str('{0:.2f}'.format(ex_1.coefficient)
                        ) if ex_1 is not None else '',
                    [Paragraph(ex_1.label if ex_1 is not None else '', styles[
                        'Normal']), Paragraph("<para textColor=grey\
                        >" + ex_1.additionnal_info + "</para\
                        >" if ex_1.additionnal_info is not None else "",
                                              styles['Normal'])],
                    ex_1.type_exam if ex_1 is not None else '',
                    ex_1.text_duration if ex_1 is not None else '',
                    ex_1.convocation if ex_1 is not None else '',
                    ex_1.eliminatory_grade if ex_1 is not None else '',
                    ex_1.threshold_session_2 if ex_1 is not None else '',
                ]

                ex_2_table = [
                    str('{0:.2f}'.format(ex_2.coefficient)
                        ) if ex_2 is not None else '',
                    [Paragraph(ex_2.label if ex_2 is not None else '', styles[
                        'Normal']), Paragraph("<para textColor=grey\
                        >" + ex_2.additionnal_info + "</para\
                        >" if ex_2.additionnal_info is not None else "",
                                              styles['Normal'])],
                    ex_2.type_exam if ex_2 is not None else '',
                    ex_2.text_duration if ex_2 is not None else '',
                    ex_2.eliminatory_grade if ex_2 is not None else '',
                ] if ex_2 is not None else ['', '', '', '', '']
                ex_1_table.extend(ex_2_table)
                exam_table.append(ex_1_table)
            exam_table = exam_table if len(exam_table) > 0 else exams_empty
            inner_table = Table(exam_table, colWidths=widht_exams)
            inner_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.1, colors.black),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                 ]))
            return inner_table

        # def table_exam(exam_list, exam1=True):
        #     exam_table = []
        #     for e in exam_list:
        #         regular = [
        #             '{0:.2f}'.format(e.coefficient),
        #             Paragraph(e.label, styles['Normal']),
        #             e.type_exam,
        #             e.text_duration,

        #         ]
        #         if exam1:
        #             regular.extend([
        #                 e.convocation,
        #                 e.eliminatory_grade,
        #                 e.threshold_session_2,
        #             ])
        #         else:
        #             regular.extend([
        #                 e.eliminatory_grade,

        #             ])
        #         exam_table.append(regular)

        #     exam_table = exam_table if exam_table else exam_1_empty if exam1 else exam_2_empty
        #     inner_table = Table(
        #         exam_table, colWidths=widht_exam_1 if exam1 else widht_exam_2)
        #     inner_table.setStyle(TableStyle(
        #         [('INNERGRID', (0, 0), (-1, -1), 0.1, colors.black),
        #          ]))
        #     return inner_table

        big_table.append([
            "%s%s " % ("    " * what.get('rank'), struct.label),
            Paragraph(
                struct.get_respens_name_small,
                styles['CenterSmall']),
            [Paragraph(struct.ROF_ref, styles['CenterSmall']), Paragraph(
                struct.ref_si_scol, styles['CenterSmall'])],
            struct.ECTS_credit if struct.ECTS_credit else '-',
            '{0:.0f}'.format(link.coefficient) if link.coefficient else '',
            link.eliminatory_grade,
            # table_exam(exams_1), '', '', '', '', '', '',
            # table_exam(exams_2, exam1=False),
            write_exams(exams_1, exams_2)

        ])
        for e in what.get('children'):
            write_the_table(e)

    for e in links:
        write_the_table(e)

    # ############ STYLE ################################
    # Static style
    style_table = [
        # BASIC
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 2), 'CENTER'),
        ('ALIGN', (3, 3), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),

        # SPAN
        ('SPAN', (0, 0), (5, 0)),
        ('SPAN', (6, 0), (-1, 0)),
        ('SPAN', (0, 1), (5, 1)),
        ('SPAN', (6, 1), (12, 1)),
        ('SPAN', (13, 1), (-1, 1)),
        ('SPAN', (0, 2), (0, 1)),
        ('SPAN', (1, 2), (1, 1)),
        ('SPAN', (2, 2), (2, 1)),
        ('SPAN', (3, 2), (3, 1)),
        ('SPAN', (4, 2), (4, 1)),
        ('SPAN', (5, 2), (5, 1)),
        # BACKGROUND
        ('BACKGROUND', (6, 0), (-1, 0), colors.steelblue),
        ('BACKGROUND', (6, 1), (12, 2), colors.lightgrey),
        ('BACKGROUND', (13, 1), (-1, 2), colors.grey),
        # PADDING
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        # BOLD
        ('FACE', (0, 0), (5, 2), 'Helvetica-Bold'),
        ('FACE', (6, 0), (-1, 1), 'Helvetica-Bold'),
        # TEXT COLOR
        ('TEXTCOLOR', (6, 0), (-1, 0), colors.white),
    ]
    # Dynamic style
    for e in range(title_length, len(big_table)):
        style_table.append(('SPAN', (6, e), (-1, e)))

    for e in background_blue:
        style_table.append(
            ('BACKGROUND', (0, e), (-1, e), colors.lightsteelblue))
        style_table.append(('FACE', (0, e), (0, e), 'Helvetica-Bold'))

    for e in bold_text:
        style_table.append(('FACE', (0, e), (0, e), 'Helvetica-Bold'))

    # ############ CREATE TABLE ################################
    final_table = Table(big_table, colWidths=col_width,
                        style=style_table, repeatRows=3)
    story.append(final_table)

    return story


def complete_rule(year, title, training, rules, specific, add):
    """
    Story to get all rule for a selected training
    """
    # ############ define usefull stuff ################################
    story = []
    id_ap = [e.rule_gen_id for e in add]

    # ############ TITLE ################################
    header = [
        _("Année universitaire %s/%s" % (year, year + 1)),
        _("%s" % training.label),
        _("Récapitulatif des règles de la formation"),
    ]
    ttle = []
    for e in header:
        ttle.append(Paragraph("<para align=right fontSize=14 spaceAfter=14 textColor=\
            darkblue><strong>%s</strong></para>" % e, styles['Normal']))

    t = [[logo_uds, ttle]]
    table = Table(t, colWidths=(145, 405))
    story.append(table)
    story.append(Spacer(0, 24))

    # ############ No rules case ################################
    if not rules:
        story.append(Spacer(0, 12))
        story.append(Paragraph(_("Aucune règle."), styles['Normal']))
        return story

    # ############ add rules one by one ################################
    for e in rules:
        a = add if e.n_rule in id_ap else None
        add_simple_paragraph(story, e, specific, a)

    return story


def one_rule(title, rule):
    story = []
    year = rule.code_year
# ############ TITLE ################################

    header = [
        _("Modalités d'évaluation des connaissances et compétences"),
        rule.label,
        _("Année universitaire %s/%s" % (year, year + 1))
    ]
    ttle = []
    for e in header:
        ttle.append(Paragraph("<para align=center fontSize=14 spaceAfter=14 textColor=\
            darkblue><strong>%s</strong><" % e, styles['Normal']))

    t = [[logo_uds, ttle]]

    table = Table(t, colWidths=(145, 405))

    story.append(table)

    story.append(Spacer(0, 12))
    degrees = str([e.short_label for e in rule.degree_type.all()])[1:-1]
    applies = _("RÈGLE APPLICABLE aux diplômes de type : <br></br> \
        %s" % degrees)
    if rule.is_eci and rule.is_ccct:
        applies = _("RÈGLE APPLICABLE à tous les diplômes de type : <br></br> \
        %s" % degrees)
    if rule.is_eci and not rule.is_ccct:
        applies = _("RÈGLE APPLICABLE aux diplômes de type : <br></br> %s <br></br> en  \
        évaluation continue intégrale" % degrees)
    if not rule.is_eci and rule.is_ccct:
        applies = _("RÈGLE APPLICABLE aux diplômes de type : <br></br>%s<br></br> en contrôle \
        terminal, combiné ou non avec un contrôle continu" % degrees)

    block_rules(applies, [rule], story)

    return story


def degree_type_rules(title, degreetype, year):
    degree_type = degreetype.short_label.upper()

    cr = rules_degree_for_year(degreetype.id, year)

    story = []

# ############ TITLE ################################

    header = [
        _("Modalités d'évaluation des connaissances et compétences"),
        _("Règles générales - %s" % degreetype.short_label),
        _("Année universitaire %s/%s" % (year, year + 1))
    ]
    ttle = []
    for e in header:
        ttle.append(Paragraph("<para align=center fontSize=14 spaceAfter=14 textColor=\
            darkblue><strong>%s</strong></para>" % e, styles['Normal']))

    t = [[logo_uds, ttle]]

    table = Table(t, colWidths=(145, 405))

    story.append(table)

    story.append(Spacer(0, 12))

# ############ No rules case ################################

    if cr is None:
        story.append(Spacer(0, 24))
        story.append(Paragraph(_("Aucune règle."), styles['Normal']))
        return story

# ############ ECI/CCT ################################

    block_rules(
        _("RÈGLES APPLICABLES à tous les diplômes de type \
        %s" % degree_type),
        cr.filter(Q(is_eci=True, is_ccct=True)),
        story
    )

# ############ ECI ################################

    block_rules(
        _("RÈGLES APPLICABLES aux diplômes de type %s en  \
         évaluation continue intégrale" % degree_type),
        cr.filter(Q(is_eci=True, is_ccct=False)),
        story
    )

# ############ CCCT ################################
    block_rules(
        _("RÈGLES APPLICABLES aux diplômes de type %s en contrôle terminal, \
        combiné ou non avec un contrôle continu" % degree_type),
        cr.filter(Q(is_eci=False, is_ccct=True)),
        story
    )
    return story


def derogations(title, year):
    # TODO: Add breakpage when first block use nearly the whole space !
    # TODO: REFACTOR data fetching in model!
    toptend = None
    story = []
    supply_filter = []
    derog_eci_ccct = []
    derog_eci = []
    derog_ccct = []

    # ############ DATAS ################################
    uy = UniversityYear.objects.get(is_target_year=True)
    institutes = Institute.objects.filter(
        training__code_year=uy.code_year).distinct()

    t = Training.objects.filter(code_year=uy.code_year)

    for training in t:
        if training.supply_cmp in institutes.values_list('code', flat=True):
            supply_filter.append(training.supply_cmp)

    derogations = SpecificParagraph.objects.filter(code_year=uy.code_year)

    d = []
    toptend = []
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
    rules_sorted = sorted(rules_count, key=rules_count.get, reverse=True)

    for r in rules_sorted:
        toptend.append(
            dict(rule=Rule.objects.get(n_rule=r, code_year=uy.code_year),
                 nb_derog=rules_count[r],
                 nb_cmp=cmp_count[r]))

    for d in toptend:
        d['supply_cmps'] = derogations.filter(rule_gen_id=d['rule'].id).values_list(
            'training__supply_cmp', flat=True)
        d['cmps'] = institutes.filter(
            code__in=d['supply_cmps']).values_list('label', flat=True)
        d['is_eci'] = d['rule'].is_eci
        d['is_ccct'] = d['rule'].is_ccct

        if d['rule'].is_eci and d['rule'].is_ccct:
            derog_eci_ccct.append(d)
        elif d['rule'].is_eci:
            derog_eci.append(d)
        elif d['rule'].is_ccct:
            derog_ccct.append(d)
    # ############ TITLE ################################

    header = [
        _("MECC"),
        _("Année universitaire %s/%s" % (year, year + 1)),
        _("Synthèse des dérogations")
    ]
    ttle = []
    for e in header:
        ttle.append(Paragraph("<para align=center fontSize=14 spaceAfter=14 textColor=\
            darkblue><strong>%s</strong></para>" % e, styles['Normal']))

    t = [[logo_uds, ttle]]

    table = Table(t, colWidths=(145, 405))

    story.append(table)
    story.append(Spacer(0, 22))

    # ############ NO DEROG ################################
    if toptend is None:
        story.append(Spacer(0, 24))
        story.append(Paragraph(_("Aucune dérogation."), styles['Normal']))
        return story

    # ############ ECI+CC/CT ###############################
    if derog_eci_ccct:
        block_derogations(
            _("Régime ECI et CC/CT"),
            derog_eci_ccct,
            story
        )

    # ############ ECI ##########{{}}#######################
    if derog_eci:
        block_derogations(
            _("Régime ECI"),
            derog_eci,
            story
        )

    # ############ CCCT ##########{{}}######################
    if derog_ccct:
        block_derogations(
            _("Régime CCCT"),
            derog_ccct,
            story
        )

    return story


def block_derogations(title, derogations, story):

    style = [
        ('TEXTCOLOR', (0, -1), (0, -1), colors.darkblue),
    ]
    if len(derogations) > 0:
        t = [
            [""],
            [Paragraph("<para fontSize=13 spaceAfter=14 textColor=\
                darkblue><strong>%s</strong></para>" % title, styles["Normal"])]
        ]

        table = Table(t, colWidths=(550))
        story.append(table)
        story.append(Spacer(0, 6))

    headers = [_('Nom de la règle'), _('NB composantes'),
               _('Liste des composantes')]

    style = TableStyle([
        # ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
        # ('ALIGN', (1, -1), (-1, -1), 'CENTER'),
        # ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    colWidth = (200, 90, 260)

    data = []
    data.append(headers)

    for d in derogations:
        data += [(str(d['rule']), "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; " +
                  str(d['nb_cmp']), "<br />".join(d['cmps']))]

    data = [[Paragraph(cell, styles['Justify'])
             for cell in row] for row in data]
    table = Table(data, colWidths=colWidth, style=style)

    story.append(table)

    return story
