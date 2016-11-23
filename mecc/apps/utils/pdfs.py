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


def block_rules(title, rules, story):
    if len(rules) > 0:
        t = [
            [""],
            [Paragraph(title, styles["Normal"])]
        ]

        table = Table(t, colWidths=(550), style=[
            ('BOX', (0, 1), (-1, 1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
        ])
        story.append(table)

        for paragraph in rules:
            add_paragraph(paragraph, story)

    return story


def add_paragraph(e, story):
    t = [["", ""]]

    t.append([
        Paragraph("<para textColor=darkblue><b>%s</b></para>" % e.label,
                  styles['Normal']),
        Paragraph("<para align=right textColor=darkblue fontSize=8>\
                  ID %s</para>" % e.pk, styles['Normal'])])

    paragraphs = ParagraphRules.objects.filter((Q(rule=e)))

    for p in paragraphs:
        if p.is_in_use:
            txt = ''
            # cmp = _("Alinéa de composante (facultatif)") if p.is_cmp else ''
            derog = _("Dérogation <br></br> possible") if \
                p.is_interaction else ''
            if p.is_interaction:
                txt = derog  # if not p.is_cmp else cmp

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
