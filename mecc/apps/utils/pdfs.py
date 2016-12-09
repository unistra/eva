from django.http import HttpResponse
from reportlab.platypus import Paragraph, Spacer, Image, SimpleDocTemplate, \
    Table
from reportlab.pdfgen import canvas
from django.db.models import Q
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY

from .querries import rules_degree_for_year
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from mecc.apps.rules.models import Paragraph as ParagraphRules
from django.utils.translation import ugettext as _
from django.db.models import Q


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))


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


def add_simple_paragraph(story, rule, sp, ap):
    """
    print content of paragraph with Specific and additionnel values in state of
    standard values
    """

    def append_text(story, text, style, motiv, spacer=6):
        """
        print content of paragraph no matter what
        """
        if motiv:
            story.append(
                Paragraph(
                    "<para %s leftIndent=20><u>Motifs de la dérogation</u> : %s</para>" % (
                        style, text), styles["Justify"]))
        else:
            story.append(
                Paragraph("<para %s leftIndent=20>%s</para>" % (
                    style, text), styles["Justify"]))
        story.append(Spacer(0, spacer))

    story.append(Spacer(0, 6))
    story.append(Paragraph("<para fontSize=11><strong>%s</strong></para>" % rule.label, styles['Normal']))
    story.append(Spacer(0, 6))

    paragraphs = ParagraphRules.objects.filter(Q(rule=rule))
    for p in paragraphs:
        if p.is_in_use:
            motiv = False
            if p.id in [e.paragraph_gen_id for e in sp]:
                text = sp.get(paragraph_gen_id=p.id).text_specific_paragraph
                append_text(story, text, "textColor=blue", motiv, spacer=0)
                text = sp.get(paragraph_gen_id=p.id).text_motiv
                style = 'textColor=red'
                motiv = True
                append_text(story, text, style, motiv)
            else:
                text = p.text_standard
                style = ''
                append_text(story, text, style, motiv)

    if ap:
        text = ap.get(rule_gen_id=rule.id).text_additional_paragraph
        style = "textColor=green"
        append_text(story, text, style, motiv)


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
                    Paragraph(p.text_standard, styles["Justify"]),
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
        _("Récapitulatif des règles de la formation (avec spécificités)"),
    ]
    ttle = []
    for e in header:
        ttle.append(Paragraph("<para align=right fontSize=14 spaceAfter=14 textColor=\
            darkblue><strong>%s</strong></para>" % e, styles['Normal']))

    t = [[Image('mecc/static/img/logo_uds.png', 140, 60), ttle]]
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
            darkblue><strong>%s</strong></para>" % e, styles['Normal']))

    t = [[Image('mecc/static/img/logo_uds.png', 140, 60), ttle]]

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

    t = [[Image('mecc/static/img/logo_uds.png', 140, 60), ttle]]

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
