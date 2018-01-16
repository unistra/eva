import collections
import datetime
import re
from itertools import groupby

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from reportlab.platypus import Paragraph, Spacer, Image, SimpleDocTemplate, \
    Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape


from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import ObjectsLink, StructureObject, Exam
from mecc.apps.rules.models import Rule, Paragraph as ParagraphRules
from mecc.apps.training.models import Training, SpecificParagraph, \
    AdditionalParagraph, SpecificParagraph
from mecc.apps.utils.queries import rules_degree_for_year, currentyear, \
    get_mecc_table_order
from mecc.apps.years.models import UniversityYear
from reportlab.platypus.flowables import Flowable


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='Bullet_1', bulletIndent=25, bulletText="•"))
styles.add(ParagraphStyle(name='CenterBalek', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='CenterSmall', alignment=TA_CENTER, fontSize=8))
styles.add(ParagraphStyle(name='CenterSmallItalic',
                          alignment=TA_CENTER, fontSize=8, fontName="Times-Italic"))
styles.add(ParagraphStyle(name='SmallNormal', fontSize=8))
logo_uds = Image('mecc/static/img/signature_uds_02.png', 160, 60)
logo_uds_small = Image('mecc/static/img/signature_uds_02.png', 80, 30)


class DocGenerator(object):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.width, self.height = landscape(A4)
        self.styles = getSampleStyleSheet()

    # ----------------------------------------------------------------------
    def run(self, request, trainings):
        """
        Run the report
        """
        # BLOAT STUFF ---------------------
        trainings = request.GET.getlist('selected')
        date = request.GET.get('date')
        self.target = target = request.GET.get('target')
        standard = True if request.GET.get('standard') == "yes" else False
        ref = request.GET.get('ref')
        gen_type = request.GET.get('gen_type')
        model = request.GET.get('model')
        if 'review' in target:
            goal = _("Relecture")
        elif 'publish' in target:
            goal = _("Publication")
        elif target == 'prepare_cfvu':
            goal = "%s %s" % (_('CFVU du '), date)
        elif 'prepare_cc' in target:
            goal = "%s %s" % (_('Conseil de composante du '), date)
        else:
            goal = target

        # response ---------------------
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('filename="%s .pdf"' % goal)

        # writing in document ---------------------
        self.watermark = _('Document')
        if trainings:
            i = datetime.datetime.now()
            today = "%s/%s/%s" % (i.day, i.month, i.year)
            concerned_trainings = Training.objects.filter(
                id__in=[e for e in trainings])

            self.left_footer = "%s - %s - %s - %s - %s" % (
                _("MECC"),
                "%s/%s" % (concerned_trainings.first().code_year,
                           concerned_trainings.first().code_year + 1),
                concerned_trainings.first().institutes.filter(
                    code=concerned_trainings.first().supply_cmp).first().label,
                "%s %s" % (_("Edition du "), today),
                goal
            )
            self.story = gen_model_story(
                concerned_trainings,
                model, date, target, standard, ref,
                gen_type, request.user)
        else:
            self.story = []

        self.doc = SimpleDocTemplate(response, pagesize=landscape(A4),
                                     topMargin=24, bottomMargin=24)

        # building doc according to target -----------------------

        if 'publish' in target:
            self.left_footer = _(
                "Ces MECC sont définitives et ne peuvent pas être modifiées en cours d'année universitaire")

            self.doc.build(self.story, onFirstPage=self.publish_mecc,
                           onLaterPages=self.mecc_canvas,
                           canvasmaker=NumberedCanvas_landscape)
        else:
            self.doc.build(self.story, onLaterPages=self.mecc_canvas,
                           canvasmaker=NumberedCanvas_landscape)

        return self.doc, response

    # ----------------------------------------------------------------------
    def mecc_canvas(self, canvas, doc):
        """
        Create the document
        """
        print(self.target)
        if self.target != 'publish':
            custom_watermark(canvas, "Document intermédiaire", rotation=40,
                             font_size=40, position_x=550, position_y=-70)
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.setFillGray(0.3)
        canvas.drawString(20, 10, self.left_footer)
        canvas.restoreState()

    # ----------------------------------------------------------------------
    def publish_mecc(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 12)
        canvas.setFillColor(colors.steelblue)
        canvas.drawCentredString(425, 50, self.left_footer)
        canvas.restoreState()


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


def canvas_for_gen_pdf(canvas, doc):
    """
    canvas for generated pdfs: set to landscape with watermark
    """
    custom_watermark(canvas, "Document intermédiaire",
                     position_x=600, position_y=-75)


def canvas_for_preview_mecctable(canvas, doc):
    """
    canvas for preview mecctable
    """
    custom_watermark(canvas, "Prévisualisation", rotation=40,
                     font_size=40, position_x=500, position_y=-75)
    NumberedCanvas_landscape(canvas)


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


def block_rules(title, rules, story, styled=True, custom=False):
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
            add_paragraph(paragraph, story, custom=custom)

    return story


def list_of_parag_with_bullet(text, style=''):
    """
    Return correct string in order to be displayed as list
    """
    reg = re.compile(r'>(.*?)</(p|li)>')
    r = reg.findall(text.replace('r\\n\\', '<br><\\br>'))
    _list = []
    for t, v in r:
        if v == 'li':
            _list.append(Paragraph(
                "<para %s leftIndent=40>%s</para>" % (
                    style, t), styles['Bullet_1']))
        else:
            _list.append(Paragraph(
                "<para %s >%s</para>" % (
                    style, t), styles['Justify']))
    return _list


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


def add_simple_paragraph(story, rule, sp, ap):
    """
    print content of paragraph with Specific and additionnel values in state of
    standard values
    """

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
        text = ap.filter(rule_gen_id=rule.id).first().text_additional_paragraph
        style = "textColor=green"
        append_text(story, text, style)


def add_paragraph(e, story, sp=None, ap=None, styled=True, custom=False):

    t = [["", ""]]

    t.append([
        Paragraph("<para textColor=darkblue><b>%s</b></para>" % e.label,
                  styles['Normal']),
        Paragraph("<para align=right textColor=darkblue fontSize=8>\
                  ID %s</para>" % e.pk, styles['Normal'])
        if styled and not custom else ' '])

    paragraphs = ParagraphRules.objects.filter(Q(rule=e))
    for p in paragraphs:
        if p.is_in_use:
            txt = ''
            derog = _("Dérogation <br></br> possible") if \
                p.is_interaction else ''
            if p.is_interaction:
                if not custom:
                    txt = derog
                else:
                    txt = 'derogation(s) : %s ' % p.specific_involved.count()

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


def table_title_trainings_info(training, in_two_part=True, story=[]):
    """
    Create table title for training used in preview mecc and model A and others
    """
    # ############ USEFULL STUFF ################################
    # STYLES :
    main_style = [
        ('BOX', (0, 0), (-2, -1), 0.5, colors.black),
        ('SPAN', (-1, 0), (-1, -1)),
        ('SPAN', (0, 1), (-2, 1)),
        ('VALIGN', (0, 0), (-2, 0), 'MIDDLE'),
        ('VALIGN', (0, 1), (-2, 1), 'TOP'),
        ('BACKGROUND', (0, 0), (-2, 0), colors.steelblue),
        ('SIZE', (0, 0), (-2, 0), 11),
        ('FACE', (0, 0), (-3, 0), 'Helvetica-Bold'),

        ('TEXTCOLOR', (0, 0), (-2, 0), colors.white),
        ('BOX', (0, 0), (-2, 0), 0.5, colors.black),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)

    ]
    side_style = [
        ('BOX', (0, 0), (-1, -1), 0.5, colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.steelblue),
        ('FACE', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FACE', (0, 1), (-1, 1), 'Helvetica'),
        ('SIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
    ]
    # ############ TABLE STRUCTURE ################################

    line_2 = "<para><strong>%s : </strong>%s </para>" % (
        _('Responsable(s)'),
        ", ".join([e for e in training.get_respform_names]))
    date_cmp = training.date_val_cmp.strftime(
        "%d/%m/%Y") if training.date_val_cmp not in [None, ''] else _("Non")
    date_des = training.date_visa_des.strftime(
        "%d/%m/%Y") if training.date_visa_des not in [None, ''] else _("Non")
    date_cfvu = training.date_val_cfvu.strftime(
        "%d/%m/%Y") if training.date_val_cfvu not in [None, ''] else _("Non")
    secondary_table = Table([
        [_("Etat de saisie :")],
        ["%s : %s  %s : %s" % (
            _("Règles"), training.get_progress_rule_display().lower(),
            _("Tableau"), training.get_progress_table_display().lower())
         ],
        ["%s:%s" % (_("Validation Composante"), date_cmp)],
        ["%s:%s" % (_("Visa DES"), date_des)],
        ["%s:%s" % (_("Validation CFVU"), date_cfvu)],
    ], style=side_style
    )
    # Create here other secondary table display if needed
    table = [
        [training.label, "%s - %s" % (training.get_MECC_type_display(),
                                      training.get_session_type_display()),
         "%s : %s" % (_('Référence APOGEE'), training.ref_si_scol),
         secondary_table
         ],
        [Paragraph(line_2, styles['Normal']),
         "empty", "empty", ],
    ]

    final_table = Table(table, style=main_style, colWidths=[
                        9 * cm, 5 * cm, 6.5 * cm, 7 * cm])
    return final_table


def models_first_page(model, criteria, trainings, story):
    current_year = currentyear().code_year
    criteria_table = None
    # ### UPPER PART
    title = [
        "<font size=22>M</font size=22>odalités d'<font size=22>E</font size=22>valuation des <font size=22>C</font size=22>onnaissances et des <font size=22>C</font size=22>ompétences",
        "Année universitaire %s/%s" % (current_year, current_year + 1),
        trainings.first().institutes.filter(
            code=trainings.first().supply_cmp).first().label
    ]

    for e in title:
        story.append(Paragraph("<para align=center fontSize=16 spaceBefore=16 textColor=\
            steelblue>%s</para>" % e, styles['Normal']))
    story.append(Spacer(0, 24))

    story.append(Paragraph("<para align=center fontSize=16 spaceBefore=24 textColor=\
        steelblue>%s</para>" % "-" * 125, styles['Normal']))

    story.append(Spacer(0, 36))

    # ### TABLE STYLES
    style_criteria_table = [
        # ('GRID', (0, 0), (-1, -1), 1, colors.orange),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.steelblue),
        ('SIZE', (0, 0), (-1, 0), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 16),
    ]
    style_training_list = [
        # ('GRID', (0, 0), (-1, -1), 1, colors.pink),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('SIZE', (0, 0), (-1, -1), 8),



    ]
    style_table = [
        # ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    style_trainings = [
        # ('GRID', (0, 0), (-1, -1), 1, colors.green),
        ('VALIGN', (0, 0), (-1, 0), 'BOTTOM'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.steelblue),
        ('LINEBELOW', (-1, 0), (-1, 0), 1, colors.steelblue),
        ('ALIGN', (-1, 0), (-1, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 1), (-1, 1), 15),
        ('SIZE', (0, 0), (-1, -1), 9),
        ('SIZE', (0, 0), (0, 0), 16),
        ('SIZE', (-1, 0), (-1, 0), 12),
    ]

    # ### MAIN PART

    # ### Edition criteria published or not
    if criteria[_("Objectif")] != _('Publication'):
        criteria_list = [["Critères d'édition"]] + \
            [["%s: %s" % (k, criteria[k])] for k in criteria]
        criteria_table = Table(
            criteria_list, style=style_criteria_table, colWidths=[6 * cm])

    training_list = [
        [e.label, Table([
            ["Conseil de composante : %s" %
                (e.date_val_cmp.strftime(
                    "%d/%m/%Y") if e.date_val_cmp else "Non"), "CFVU : %s " % (e.date_val_cfvu.strftime(
                        "%d/%m/%Y") if e.date_val_cfvu else "Non")]
        ],
            style=style_training_list, colWidths=[5 * cm, 3 * cm])] for e in trainings
    ]

    trainings_table = [["Formation", "Dates de validation"]]
    trainings_table.extend(training_list)

    trainings_table = Table(
        trainings_table, style=style_trainings, colWidths=[6.5 * cm, 8 * cm])
    # ### BUILDING TABLE

    if criteria_table:
        table = [[criteria_table, trainings_table]]

        story.append(Table(table, style=style_table,
                           colWidths=[8.5 * cm, 15.5 * cm]))
    else:
        table = [[trainings_table]]
        story.append(Table(table, style=style_table,
                           colWidths=[15.5 * cm]))

    return story


def doc_gen_title(year, cmp_label, date, goal, custom_date=None, title="Modalités d'évaluation des connaissances et des compétences", story=[]):
    """
    Nice blue title with logo and stuff
    """
    style_table = [
        ('VALIGN', (0, 0), (-1, -1), "MIDDLE"),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.steelblue),
        ('SIZE', (0, 0), (-1, -1), 13),
        ('FACE', (0, 0), (-1, 0), 'Helvetica-Bold'),

    ]
    style_middle = [
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.steelblue),
        ('SIZE', (0, 0), (-1, -1), 12),
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.steelblue),

    ]
    style_last = [
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.steelblue),
        ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.steelblue),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('SIZE', (0, 0), (-1, -1), 9),

    ]
    if goal in ['Relecture', 'Publication']:
        goal_text = goal.upper()
    else:
        goal_text = "<u>%s</u><br></br>Du %s" % (goal, custom_date)
    table = [
        [logo_uds_small, title, Table([
            ["%s %s/%s" % (_("Année universitaire"), year, year + 1)],
            [Paragraph("<para textColor=steelblue fontSize=12 >%s</para> \
            " % cmp_label, styles['Normal'])]
        ], style=style_middle), Table([
            ["%s %s" % (_("Edition du "), date)], [
                Paragraph("<para fontsize=9 textColor=steelblue align=right><strong>%s\
                </strong></para> " % goal_text, styles['Normal'])]
        ], style=style_last)]
    ]
    story.append(Table(table, style=style_table, colWidths=[
                 3.25 * cm, 15 * cm, 6.5 * cm, 4.5 * cm]))
    return story


def gen_model_story(trainings, model, date, target, standard, ref, gen_type, user, story=[]):
    """
    Story for model
    """
    ordered_trainings = trainings.order_by('degree_type')
    i = datetime.datetime.now()
    year = currentyear().code_year

    if 'review' in target:
        goal = _("Relecture")
    elif 'publish' in target:
        goal = _("Publication")
    elif target == 'prepare_cfvu':
        goal = _('CFVU')
    elif 'prepare_cc' in target:
        goal = _('Conseil de composante')
    else:
        # TODO: should not be raised debug for now
        goal = target

    criteria = [

        (_("Utilisateur"), "%s %s" % (user.first_name, user.last_name)),
        (_("Objectif"), goal),
        (_("Modèle"), model.upper()),
        (_("Date"), "%s/%s/%s" % (i.day, i.month, i.year)),
        (_("Règle standard"), _("Avec") if standard else _("Sans")),
        (_("Références"), _("Sans") if ref == "without" else _(
            "ROF") if ref == "with_rof" else _("SI Scolarité"))

    ]

    criteria = collections.OrderedDict(criteria)
    additionals = AdditionalParagraph.objects.filter(
        training__in=ordered_trainings)
    specifics = SpecificParagraph.objects.filter(
        training__in=ordered_trainings)
    derog_gen_id = [e.rule_gen_id for e in specifics]
    addit_gen_id = [e.rule_gen_id for e in additionals]
    train = trainings.last()
    all_rules = Rule.objects.filter(
        degree_type__in=[e.degree_type for e in trainings],
        code_year=train.code_year)
    rules = all_rules.filter(id__in=derog_gen_id + addit_gen_id)
    models_first_page(
        model, criteria, ordered_trainings, story)
    story.append(PageBreak())
    doc_gen_title(
        train.code_year,
        train.institutes.filter(code=train.supply_cmp).first().label,
        "%s/%s/%s" % (i.day, i.month, i.year),
        goal,
        story=story,
        custom_date=date
    )

    if model == 'a':
        degree_type = []
        for d in ordered_trainings:
            if d.degree_type not in degree_type and standard:
                if degree_type:
                    story.append(PageBreak())
                title_degree_type(d.degree_type, story)
                trainings = {e.MECC_type for e in ordered_trainings.filter(
                    degree_type=d.degree_type)}
                story += degree_type_rules(None, d.degree_type,
                                           year, filter_type=trainings,
                                           custom=True)
            degree_type.append(d.degree_type)
            # if len(degree_type) > 1:
            story.append(PageBreak())
            preview_mecctable_story(
                d, story, False, ref=ref, model=model, additionals=additionals,
                specifics=specifics, edited_rules=rules)

    if model == 'b':
        pass
    
    return story


def derog_and_additional(training, derogs, additionals, edited_rules, story=[]):
    """
    Adding derog and additional for specific training
    """
    # #### STYLES
    main_table_style = [
        ('VALIGN', (1, 0), (-1, -1), "TOP"),
        ('VALIGN', (0, 0), (0, -1), "MIDDLE"),
        ('LEFTPADDING', (-1, 0), (-1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
    ]
    main_table_size = [1 * cm, 12.5 * cm, 10.5 * cm]
    additional_style = [
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.steelblue),
        ('FACE', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SIZE', (0, 0), (-1, 0), 12),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
    ]
    derog_style = additional_style + [
        ('LINEAFTER', (-1, -1), (-1, -1), 0.5, colors.red),
    ]
    motiv_style = [

    ]
    # #### TABLES
    table = []
    if additionals:
        for e in additionals:
            table.append([
                Paragraph("<para textColor=green>(A)</para>",
                          styles['Normal']),
                Table([
                    [edited_rules.filter(id=e.rule_gen_id).first().label],
                    [list_of_parag_with_bullet(e.text_additional_paragraph)]
                ], style=additional_style, ),
                ""
            ])
    if derogs:
        for e in derogs:
            table.append([
                Paragraph("<para textColor=blue>(D)</para>", styles['Normal']),
                Table([
                    [edited_rules.filter(id=e.rule_gen_id).first().label],
                    [list_of_parag_with_bullet(e.text_specific_paragraph)]
                ], style=derog_style),
                Table([
                    [' '],
                    [Paragraph("<para textColor=red><u>%s</u> : %s </para>" % (
                        _('Motif de la dérogation'), e.text_motiv), styles['Normal'])]
                ], style=motiv_style)
            ])

    if table:
        story.append(Table(table, style=main_table_style,
                           colWidths=main_table_size))

    return story

# derog_and_additional(training, specifics.filter(
#             training=training), additionals.filter(training=training),
#             edited_rules, story)


def preview_mecctable_story(training, story=[], preview=True, ref="both", model=None,
                            additionals=None, specifics=None, edited_rules=None):
    """
    Story for previewing mecctable
    """
    import itertools

    # ############ USEFULL STUFF ################################
    training_is_ccct = True if training.MECC_type == 'C' else False
    current_year = currentyear().code_year
    current_structures = StructureObject.objects.filter(code_year=current_year)
    current_links = ObjectsLink.objects.filter(code_year=current_year)
    current_exams = Exam.objects.filter(code_year=current_year)
    root_link = current_links.filter(
        id_parent='0', id_training=training.id).order_by(
        'order_in_child').distinct()

    links = get_mecc_table_order([e for e in root_link], [],
                                 current_structures, current_links,
                                 current_exams, all_exam=True)
    references = '<para textColor=steelblue><strong>%s</strong></para>' % ("Référence ROF \
<br></br><br></br> Référence APOGEE" if ref == "both" else "Référence\
 ROF" if "with_rof" == ref else 'Référence APOGEE' if "with_si" == ref else '')

    # ############ TITLE STUFF ################################
    if preview:
        story.append(Paragraph("<para align=center fontSize=14 spaceAfter=14 textColor=\
            red><strong>%s</strong></para>" % _("PREVISUALISATION du TABLEAU"), styles['Normal']))

    title_training_table = table_title_trainings_info(training)

    story.append(title_training_table)
    if model == 'a':
        story.append(Paragraph("<para fontSize=12 lindent=0 spaceAfter=14 \
        spaceBefore=14 textColor=darkblue><strong>%s</strong></para>" % _(
            "Dérogation et alinéas additionnels"), styles['Normal']))
        if specifics.filter(training=training) or additionals.filter(training=training):
            derog_and_additional(training, specifics.filter(
                training=training), additionals.filter(training=training),
                edited_rules, story)
        else:
            story.append(Paragraph("<para>%s</para>" %
                                   _("Aucun"), styles['Normal']))

    story.append(Paragraph("<para fontSize=12 lindent=0 spaceAfter=14 spaceBefore=14 textColor=\
        darkblue><strong>%s</strong></para>" % _("Tableau MECC"), styles['Normal']))
    story.append(Spacer(0, 12))

    # ############ TABLE STRUCUTURE ################################
    col_width = [6 * cm, 2.25 * cm, 1.8 * cm, .6 * cm, .6 * cm, .6 * cm]
    widht_exam_1 = [0.85 * cm, 4 * cm, .6 *
                    cm, 1.1 * cm, .6 * cm, .7 * cm, .7 * cm, ]
    widht_exam_2 = [0.85 * cm, 4 * cm, .6 * cm, 1.1 * cm, .7 * cm]
    widht_exams = widht_exam_1
    widht_exams.extend(widht_exam_2)
    col_width.extend(widht_exam_1)
    col_width.extend(widht_exam_2)

    # - Ugly but tables are almost always ugly
    big_table = [['OBJETS', '', '', '', '', '', 'EPREUVES'],
                 ['Intitulé', 'Responsable', Paragraph(
                     references,
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
                  verticalText(
                      'Convocation' if not training_is_ccct else 'CC/CT'),
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
                    [Paragraph(ex_1.label if ex_1 else '', styles[
                        'SmallNormal']), Paragraph("<para textColor=grey\
                        >" + ex_1.additionnal_info if ex_1 and ex_1.additionnal_info else "" + "</para\>",
                                                   styles['SmallNormal'])],
                    ex_1.type_exam if ex_1 is not None else '',
                    ex_1.text_duration if ex_1 is not None else '',
                    '' if ex_1 is None else ex_1.convocation if not training_is_ccct else ex_1.get_type_ccct_display(),
                    ex_1.eliminatory_grade if ex_1 is not None else '',
                    ex_1.threshold_session_2 if ex_1 is not None else '',
                ]

                ex_2_table = [
                    str('{0:.2f}'.format(ex_2.coefficient)
                        ) if ex_2 is not None else '',
                    [Paragraph(ex_2.label if ex_2 is not None else '', styles[
                        'SmallNormal']), Paragraph("<para textColor=grey\
                        >" + ex_2.additionnal_info + "</para\
                        >" if ex_2.additionnal_info is not None else "",
                                                   styles['SmallNormal'])],
                    ex_2.type_exam if ex_2 is not None else '',
                    ex_2.text_duration if ex_2 is not None else '',
                    ex_2.eliminatory_grade if ex_2 is not None else '',
                ] if ex_2 is not None else ['', '', '', '', '']
                ex_1_table.extend(ex_2_table)
                exam_table.append(ex_1_table)
            exam_table = exam_table if len(exam_table) > 0 else exams_empty
            if exam_table == exams_empty:
                # TODO: calculate empty space to set rowHeights in order to
                # avoid blank in table
                pass
            inner_table = Table(
                exam_table, colWidths=widht_exams, rowHeights=None)
            inner_table.setStyle(TableStyle(
                [('INNERGRID', (0, 0), (-1, -1), 0.1, colors.black),
                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                 ('FONTSIZE', (0, 0), (-1, -1), 8),
                 ]))
            return inner_table

        ref_data = (Paragraph(struct.ROF_ref, styles['CenterSmall']), Paragraph(
            struct.ref_si_scol, styles['CenterSmall'])) if ref == 'both' else Paragraph(
                struct.ROF_ref, styles['CenterSmall']) if ref == 'with_rof' else Paragraph(
            struct.ref_si_scol, styles['CenterSmall']) if ref == 'with_si' else Paragraph(
            '', styles['CenterSmall'])
        big_table.append([
            "%s%s " % ("    " * what.get('rank'), struct.label),
            Paragraph(
                struct.get_respens_name_small,
                styles['CenterSmall'] if not struct.external_name else styles['CenterSmallItalic']),
            [ref_data],
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
        ('FONTSIZE', (0, 1), (-1, -1), 8),

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
        a = add if e.id in id_ap else None
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


def title_degree_type(degree_type, story):
    story.append(Table([[degree_type]], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.steelblue),
        ('SIZE', (0, 0), (-1, -1), 12),
        ('FACE', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
    ], colWidths=[27 * cm]))
    return story


def degree_type_rules(title, degreetype, year, custom=False, filter_type=None):
    degree_type = degreetype.short_label.upper()

    cr = rules_degree_for_year(degreetype.id, year)

    story = []

# ############ TITLE ################################

    # No title means whole rules !
    if title:
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
        # No title means whole rules so no need to warn
        if title:
            story.append(Spacer(0, 24))
            story.append(Paragraph(_("Aucune règle."), styles['Normal']))
        return story

# ############ ECI/CCT ################################

    block_rules(
        _("RÈGLES APPLICABLES à tous les diplômes de type \
        %s" % degree_type),
        cr.filter(Q(is_eci=True, is_ccct=True)),
        story,
        custom=custom
    )

# ############ ECI ################################

    if not filter_type or 'E' in filter_type:
        block_rules(
            _("RÈGLES APPLICABLES aux diplômes de type %s en  \
            évaluation continue intégrale" % degree_type),
            cr.filter(Q(is_eci=True, is_ccct=False)),
            story,
            custom=custom
        )

# ############ CCCT ################################
    if not filter_type or 'C' in filter_type:
        block_rules(
            _("RÈGLES APPLICABLES aux diplômes de type %s en contrôle terminal, \
            combiné ou non avec un contrôle continu" % degree_type),
            cr.filter(Q(is_eci=False, is_ccct=True)),
            story,
            custom=custom
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
