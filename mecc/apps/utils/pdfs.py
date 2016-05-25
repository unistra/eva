from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, \
    ListFlowable, ListItem, Table, PageBreak, CondPageBreak, TableStyle
from reportlab.pdfgen import canvas
from django.db.models import Q
from reportlab.lib.units import mm
from reportlab.lib import colors

from .querries import rules_for_current_year
from reportlab.lib.styles import getSampleStyleSheet
from mecc.apps.years.models import UniversityYear
from mecc.apps.rules.models import Paragraph as ParagraphRules

styles = getSampleStyleSheet()


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


def degree_type_rules_for_current_year(title, degreetype):
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0).code_year
    cr = rules_for_current_year(degreetype.id)
    if cr is None:
        return None
    cr1 = cr.filter(Q(is_eci=True, is_ccct=True))
    cr2 = cr.filter(Q(is_eci=True, is_ccct=False))
    cr3 = cr.filter(Q(is_eci=False, is_ccct=True))
    story = []

    def lf_paragraph(e, data):
        data.append([Paragraph(e.label, styles['Normal']), ""])
        paragraphs = ParagraphRules.objects.filter((Q(rule=e)))
        for p in paragraphs:

            data.append([Paragraph(p.text_standard, styles['Normal']), ""])

        return data

# ############ TITLE ################################

    header = [
        "Modalilté d'évaluation des connaissances et compétences",
        "Règles générales - %s" % degreetype.short_label,
        "Année universitaire %s/%s" % (current_year, current_year + 1)
    ]

    for e in header:
        story.append(Paragraph(e, styles["Normal"]))

    story.append(Spacer(0, 12))
# ############ ECI/CCT ################################
    if len(cr1) > 0:
        data = [
            [Paragraph("REGLES APPLICABLES à tous les diplômes \
                de type %s" % degreetype.short_label, styles["Normal"]), '']
        ]

        for e in cr1:
            lf_paragraph(e, data)

        t = Table(data, style=[
            ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ])
        story.append(t)
# ############ ECI ################################
    if len(cr2) > 0:
        story.append(Spacer(0, 50))

        data = [
            [Paragraph("REGLES APPLICABLES aux diplômes de type %s en  \
             évaluation continue intégrale" %
             degreetype.short_label, styles["Normal"]), '']
        ]

        for e in cr2:
            lf_paragraph(e, data)

        t = Table(data, style=[
            ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ])
        story.append(t)

# ############ CCCT ################################
    if len(cr3) > 0:

        story.append(Spacer(0, 50))

        data = [
            [Paragraph("REGLES APPLICABLES aux diplômes \
            de type %s en contrôle terminal, combiné ou non avec un contrôle \
            continu" % degreetype.short_label, styles["Normal"]), '']
        ]

        for e in cr3:
            lf_paragraph(e, data)

        t = Table(data, style=[
            ('LINEABOVE', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ])
        story.append(t)

    return story
