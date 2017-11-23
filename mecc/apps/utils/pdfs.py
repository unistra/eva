import re

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from reportlab.platypus import Paragraph, Spacer, Image, SimpleDocTemplate, \
    Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from mecc.apps.institute.models import Institute
from mecc.apps.rules.models import Rule, Paragraph as ParagraphRules
from mecc.apps.training.models import Training, SpecificParagraph
from mecc.apps.utils.queries import rules_degree_for_year
from mecc.apps.years.models import UniversityYear


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='Bullet_1', bulletIndent=25, bulletText="•"))
styles.add(ParagraphStyle(name='CenterBalek', alignment=TA_CENTER))
logo_uds = Image('mecc/static/img/signature_uds_02.png', 160, 60)


def setting_up_pdf(title, margin=72):
    """
    Create the HttpResponse object with the appropriate PDF headers.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ('filename="%s.pdf"' % title)

    doc = SimpleDocTemplate(response, rightMargin=margin, leftMargin=margin,
                            topMargin=margin, bottomMargin=18)
    return response, doc


def watermark_do_not_distribute(canvas, doc):
    """
    Add a watermark
    """
    canvas.saveState()
    canvas.setFont("Helvetica", 45)
    canvas.setFillGray(0.80)
    canvas.rotate(45)
    canvas.drawCentredString(550, 100, "NE PAS DIFFUSER")
    canvas.restoreState()


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

    def draw_page_number(self, page_count):
        """
        drow page number with custom format and position
        """
        if page_count > 0:
            self.setFillGray(0.2)
            self.setFont("Helvetica", 8.5)
            self.drawRightString(
                205 * mm, 5 * mm, "Page %d/%d" %
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
        # comment usefull to visualize border and grid
        # ('BOX', (0, 1), (-1, 1), 1, colors.black),
        # ('BACKGROUND', (1, 0), (1, -1), colors.grey),
        ('VALIGN', (0, 0), (0, -1), 'TOP'),
        ('VALIGN', (1, 1), (1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 2), (-1, -1), 0.75, colors.lightgrey),
    ])
    story.append(table)
    return story


def complete_rule(year, title, training, rules, specific, add):
    """
    Story to get all rule for a slected training
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
            darkblue><strong>%s</strong></para>" % e, styles['Normal']))

    t = [[logo_uds, ttle]]

    table = Table(t, colWidths=(145, 405))

    story.append(table)

    story.append(Spacer(0, 12))
    degrees = str([e.short_label for e in rule.degree_type.all()])[1:-1]
    applies = _("RÈGLE APPLICABLE aux diplômes de type : <br> \
        %s" % degrees)
    if rule.is_eci and rule.is_ccct:
        applies = _("RÈGLE APPLICABLE à tous les diplômes de type : <br> \
        %s" % degrees)
    if rule.is_eci and not rule.is_ccct:
        applies = _("RÈGLE APPLICABLE aux diplômes de type : <br> %s <br> en  \
        évaluation continue intégrale" % degrees)
    if not rule.is_eci and rule.is_ccct:
        applies = _("RÈGLE APPLICABLE aux diplômes de type : <br>%s<br> en contrôle \
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

    # ############ DATAS ################################
    uy = UniversityYear.objects.get(is_target_year=True)
    institutes = Institute.objects.filter(
        training__code_year=uy.code_year).distinct()

    t = Training.objects.filter(code_year=uy.code_year)

    for training in t:
        if training.supply_cmp in institutes.values_list('code', flat=True):
            supply_filter.append(training.supply_cmp)

    derogations = SpecificParagraph.objects.filter(code_year=uy.code_year)

    toptend = derogations.values('rule_gen_id').annotate(nb_derog=Count('rule_gen_id'), nb_cmp=Count(
        'training__supply_cmp', distinct=True)).order_by('-nb_derog').exclude(nb_cmp__isnull=True)

    for d in toptend:
        d['rule'] = Rule.objects.get(id=d['rule_gen_id'])
        d['supply_cmps'] = derogations.filter(rule_gen_id=d['rule_gen_id']).values_list(
            'training__supply_cmp', flat=True).distinct()
        d['cmps'] = institutes.filter(
            code__in=d['supply_cmps']).values_list('label', flat=True)
        d['is_eci'] = d['rule'].is_eci
        d['is_ccct'] = d['rule'].is_ccct

        if d['rule'].is_eci and d['rule'].is_ccct:
            derog_eci_ccct.append(d)
        elif d['rule'].is_eci:
            derog_eci.append(d)
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
    block_derogations(
        _("Régime ECI et CC/CT"),
        derog_eci_ccct,
        story
    )

    # ############ CCCT ##########{{}}######################
    block_derogations(
        _("Régime ECI"),
        derog_eci,
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
