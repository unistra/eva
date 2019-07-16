from io import BytesIO

from bs4 import BeautifulSoup as bs
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, BaseDocTemplate, Paragraph, Table, \
    TableStyle, NextPageTemplate, PageTemplate, Frame
from reportlab.platypus.flowables import HRFlowable, PageBreak

from mecc.apps.institute.models import Institute
from mecc.apps.rules.models import Rule, Paragraph as RuleParagraph
from mecc.apps.training.models import Training, SpecificParagraph, \
    AdditionalParagraph
from mecc.apps.utils.documents_generator.utils.pdf import filter_content
from mecc.apps.years.models import UniversityYear
from .preview_mecctable import PreviewMeccTable

logo_uds_small = Image(
    'mecc/static/img/signature_uds_02.png',
    80,
    30,
    hAlign='LEFT'
)


class ModelE(PreviewMeccTable):
    COLOR_DARKBLUE = '#4682B3'
    COLOR_LIGHTBLUE = '#AFC3DD'
    COLOR_LIGHTGREY = '#D3D3D3'
    COLOR_DARKGREY = '#808080'
    COLOR_TEXT = '#000000'
    COLOR_TEXT_INVERSED = '#FFFFFF'

    def __init__(self, training):
        self.training = training
        self.reference = 'without'
        self.institute = Institute.objects.get(code__exact=training.supply_cmp)
        self.year = UniversityYear.objects.get(code_year=training.code_year)
        self.doc_setup()
        self.make_styles()
        self.p_width, self.p_height = portrait(A4)
        self.p_page_width = (self.p_width - self.left_margin * 2)
        self.p_page_height = (self.p_height - self.top_margin * 2)
        self.mecctable_header_line_1 = ['Enseignements'.upper(), '', '', '', '', '', 'Épreuves'.upper()]
        self.story = []
        self.respforms = True

    def build_doc(self):
        self.write_training_header()
        self.write_rules()
        self.story.append(NextPageTemplate('landscape'))
        self.story.append(PageBreak())
        self.write_table_title()
        self.write_mecctable()
        # self.write_mecc_table()
        self.document.build(self.story)

        return self.response

    def write_training_header(self):
        """
        Entête du PDF : Année, nom de la formation, Faculté, Responsable(s)
        """
        respforms = ', '.join([e for e in self.training.get_respform_names])
        training_header_style = TableStyle()
        training_header_style.add(
            'BACKGROUND',
            (0, 0),
            (0, 0),
            self.COLOR_DARKBLUE
        )
        training_header_style.add('BACKGROUND', (1, 0), (1, 0), self.COLOR_TEXT)
        training_header_style.add('BOX', (0, 0), (-1, -1), 1, self.COLOR_TEXT)
        self.story.append(
            Table(
                [
                    [
                        logo_uds_small,
                        Paragraph(
                            "{}<br/><b>Modalités d'évaluation des connaissances \
                                et des compétences</b><br/>{}".format(
                                    self.year.label_year,
                                    filter_content(self.institute.label)
                                ),
                            self.styles['HeaderTitle']
                        )
                    ]
                ],
                colWidths=[30 * mm, self.p_page_width - 30 * mm]
            )
        )
        self.story.append(
            Paragraph(
                "Ces modalités sont définitives et ne peuvent pas être modifiées \
                en cours d'année universitaire",
                self.styles['NormalCentered']
            )
        )
        self.story.append(
            Table(
                [
                    [
                        Paragraph(
                            "<b>{}</b>".format(filter_content(self.training.label)),
                            self.styles['NormalInversed']
                        )
                    ],
                    [
                        Paragraph(
                            "<b>Responsable(s) :</b> {}".format(filter_content(respforms)),
                            self.styles['NormalCentered']
                        )
                    ]
                ],
                style=training_header_style
            )
        )

    # def mecctable_story(self):
    #     import itertools
    #     training_is_ccct = True if self.training.MECC_type == 'C' else False
    #     current_structures = StructureObject.objects.filter(
    #         code_year=self.year.code_year
    #     )
    #     current_links = ObjectsLink.objects.filter(
    #         code_year=self.year.code_year
    #     )
    #     current_exams = Exam.objects.filter(code_year=self.year.code_year)
    #     root_link = current_links.filter(
    #         id_parent='0',
    #         id_training=self.training.id).order_by('order_in_child').distinct()
    #     links = get_mecc_table_order(
    #         [e for e in root_link],
    #         [],
    #         current_structures,
    #         current_links,
    #         current_exams,
    #         all_exam=True
    #     )
    #
    #     col_width = [6 * cm, 2.25 * cm, 1.8 * cm, .6 * cm, .6 * cm, .6 * cm]
    #     width_exam_1 = [0.85 * cm, 4 * cm, .6 *
    #                     cm, 1.1 * cm, .6 * cm, .7 * cm, .7 * cm, ]
    #     width_exam_2 = [0.85 * cm, 4 * cm, .6 * cm, 1.1 * cm, .7 * cm]
    #     width_exams = width_exam_1
    #     width_exams.extend(width_exam_2)
    #     col_width.extend(width_exam_1)
    #     col_width.extend(width_exam_2)
    #
    #     def make_big_table_headers():
    #         if self.training.session_type == '2':
    #             headers = [
    #                 ['Enseignements'.upper(), '', '', '', '', '', 'Épreuves'.upper()],
    #                 ['Intitulé', 'Responsable', '',
    #                  verticalText('Crédit ECTS'), verticalText('Coefficient'),
    #                  verticalText('Seuil de compensation'), 'Session principale',
    #                  '', '', '', '', '', '', 'Session de rattrapage'],
    #                 ['Intitulé',
    #                  'Responsable',
    #                  'Référence APOGEE',
    #                  verticalText('Crédit ECTS'),
    #                  verticalText('Coefficient'),
    #                  verticalText('Seuil de compensation'),
    #                  verticalText('Coefficient'),
    #                  'Intitulé',
    #                  verticalText('Type'),
    #                  verticalText('Durée'),
    #                  verticalText('Convocation' if not training_is_ccct else 'CC/CT'),
    #                  verticalText('Seuil de compensation'),
    #                  verticalText('Report session 2'),
    #                  verticalText('Coefficient'),
    #                  'Intitulé',
    #                  verticalText('Type'),
    #                  verticalText('Durée'),
    #                  verticalText('Seuil de compensation')],
    #             ]
    #         else:
    #             headers = [
    #                 ['Enseignements'.upper(), '', '', '', '', '', 'Épreuves'.upper()],
    #                 ['Intitulé', 'Responsable', '',
    #                  verticalText('Crédit ECTS'), verticalText('Coefficient'),
    #                  verticalText('Seuil de compensation'), 'Session unique',
    #                  '', '', '', '', '', '', ''],
    #                 ['Intitulé',
    #                  'Responsable',
    #                  'Référence APOGEE',
    #                  verticalText('Crédit ECTS'),
    #                  verticalText('Coefficient'),
    #                  verticalText('Seuil de compensation'),
    #                  verticalText('Coefficient'),
    #                  'Intitulé',
    #                  verticalText('Type'),
    #                  verticalText('Durée'),
    #                  verticalText('Convocation' if not training_is_ccct else 'CC/CT'),
    #                  verticalText('Seuil de compensation'),
    #                  verticalText('Report session 2'),
    #                  '', '', '', '', '', ],
    #             ]
    #
    #         return headers
    #
    #     big_table = make_big_table_headers()
    #
    #     col_width = [6.8 * cm, 3.25 * cm, 0, .6 * cm, .6 * cm, .6 * cm]
    #     width_exam_1 = [0.85 * cm, 4 * cm, .6 *
    #                     cm, 1.1 * cm, .6 * cm, .7 * cm, .7 * cm, ]
    #     width_exam_2 = [0.85 * cm, 4 * cm, .6 * cm, 1.1 * cm, .7 * cm]
    #     widht_exams = width_exam_1
    #     widht_exams.extend(width_exam_2)
    #     col_width.extend(width_exam_1)
    #     col_width.extend(width_exam_2)
    #
    #     title_length = len(big_table)
    #     global count_row
    #     count_row = 2
    #     background_blue = []
    #     bold_text = []
    #
    #     def write_the_table(what):
    #         global count_row
    #         count_row += 1
    #
    #         if what.get('rank') == 0:
    #             background_blue.append(count_row)
    #         if what.get('rank') == 1:
    #             bold_text.append(count_row)
    #
    #         struct = what.get('structure')
    #         link = what.get('link')
    #         exams_1 = what.get('exams_1')
    #         exams_2 = what.get('exams_2')
    #         exams_empty = [['', '', '', '', '', '', '', '', '', '', '', '']]
    #
    #         def formated(number):
    #             frac, whole = modf(number)
    #             if frac == 0:
    #                 return int(whole)
    #             else:
    #                 return str(number).rstrip('0')
    #
    #         def write_exams(list_1, list_2):
    #             exam_table = []
    #             for ex_1, ex_2 in itertools.zip_longest(list_1, list_2):
    #                 ex_1_table = [
    #                     formated(ex_1.coefficient) if ex_1 is not None else '',
    #                     [
    #                         Paragraph(
    #                             ex_1.label if ex_1 else '',
    #                             self.styles['SmallNormal']
    #                         ),
    #                         Paragraph(
    #                             "<para textColor=grey>" + \
    #                             ex_1.additionnal_info if \
    #                                 ex_1 and ex_1.additionnal_info else "" + \
    #                                                                     "</para\>",
    #                             self.styles['SmallNormal']
    #                         )
    #                     ],
    #                     ex_1.type_exam if ex_1 is not None else '',
    #                     ex_1.text_duration if ex_1 is not None else '',
    #                     '' if ex_1 is None \
    #                         else ex_1.convocation if not training_is_ccct \
    #                         else ex_1.get_type_ccct_display(),
    #                     ex_1.eliminatory_grade if ex_1 is not None else '',
    #                     ex_1.threshold_session_2 if ex_1 is not None else '',
    #                 ]
    #                 ex_2_table = [
    #                     formated(ex_2.coefficient) if ex_2 is not None else '',
    #                     [
    #                         Paragraph(
    #                             ex_2.label if ex_2 is not None else '',
    #                             self.styles['SmallNormal']
    #                         ),
    #                         Paragraph(
    #                             "<para textColor=grey>" + \
    #                             ex_2.additionnal_info + \
    #                             "</para>" if ex_2.additionnal_info is not None \
    #                                 else "",
    #                             self.styles['SmallNormal']
    #                         )
    #                     ],
    #                     ex_2.type_exam if ex_2 is not None else '',
    #                     ex_2.text_duration if ex_2 is not None else '',
    #                     ex_2.eliminatory_grade if ex_2 is not None else '',
    #                 ] if ex_2 is not None else ['', '', '', '', '']
    #                 ex_1_table.extend(ex_2_table)
    #                 exam_table.append(ex_1_table)
    #             exam_table = exam_table if len(exam_table) > 0 else exams_empty
    #             if exam_table == exams_empty:
    #                 pass
    #             inner_table = Table(
    #                 exam_table, colWidths=widht_exams, rowHeights=None)
    #             inner_table.setStyle(TableStyle(
    #                 [('INNERGRID', (0, 0), (-1, -1), 0.1, self.COLOR_TEXT),
    #                  ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #                  ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #                  ('FONTSIZE', (0, 0), (-1, -1), 8),
    #                  ]))
    #             return inner_table
    #
    #         ref_data = Paragraph('', self.styles['CenterSmall'])
    #         big_table.append([
    #             Paragraph(
    #                 "<para leftIndent=%s>%s</para> " % (
    #                     what.get('rank') * 10,
    #                     '<b>' + struct.label + '</b>' if struct.nature == 'UE' else struct.label),
    #                 self.styles['Normal']
    #             ),
    #             Paragraph(
    #                 struct.get_respens_name if not struct.external_name \
    #                     else struct.external_name,
    #                 self.styles['CenterSmall'] if not struct.external_name \
    #                     else self.styles['CenterSmallItalic']
    #             ),
    #             [ref_data],
    #             struct.ECTS_credit if struct.ECTS_credit else '-',
    #             formated(link.coefficient) if link.coefficient else '',
    #             link.eliminatory_grade,
    #             write_exams(exams_1, exams_2)
    #         ])
    #         for e in what.get('children'):
    #             write_the_table(e)
    #
    #     for e in links:
    #         write_the_table(e)
    #
    #     style_table = [
    #         # BASIC
    #         ('INNERGRID', (0, 0), (-1, -1), 0.25, self.COLOR_TEXT),
    #         ('BOX', (0, 0), (-1, -1), 0.25, self.COLOR_TEXT),
    #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #         ('ALIGN', (0, 0), (-1, 2), 'CENTER'),
    #         ('ALIGN', (3, 3), (-1, -1), 'CENTER'),
    #         ('FONTSIZE', (0, 1), (-1, -1), 8),
    #
    #         # SPAN
    #         ('SPAN', (0, 0), (5, 0)),
    #         ('SPAN', (6, 0), (-1, 0)),
    #         ('SPAN', (0, 1), (5, 1)),
    #         ('SPAN', (6, 1), (12, 1)),
    #         ('SPAN', (13, 1), (-1, 1)),
    #         ('SPAN', (0, 2), (0, 1)),
    #         ('SPAN', (1, 2), (1, 1)),
    #         ('SPAN', (2, 2), (2, 1)),
    #         ('SPAN', (3, 2), (3, 1)),
    #         ('SPAN', (4, 2), (4, 1)),
    #         ('SPAN', (5, 2), (5, 1)),
    #         # BACKGROUND
    #         ('BACKGROUND', (6, 0), (-1, 0), self.COLOR_DARKBLUE),
    #         ('BACKGROUND', (6, 1), (12, 2), self.COLOR_LIGHTGREY),
    #         ('BACKGROUND', (13, 1), (-1, 2), self.COLOR_DARKGREY),
    #         # PADDING
    #         ('LEFTPADDING', (0, 0), (-1, -1), 0),
    #         ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    #         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    #         ('TOPPADDING', (0, 0), (-1, -1), 0),
    #         # BOLD
    #         ('FACE', (0, 0), (5, 2), 'Helvetica-Bold'),
    #         ('FACE', (6, 0), (-1, 1), 'Helvetica-Bold'),
    #         # TEXT COLOR
    #         ('TEXTCOLOR', (6, 0), (-1, 0), self.COLOR_TEXT_INVERSED),
    #     ]
    #     # Dynamic style
    #     for e in range(title_length, len(big_table)):
    #         style_table.append(('SPAN', (6, e), (-1, e)))
    #
    #     for e in background_blue:
    #         style_table.append(
    #             ('BACKGROUND', (0, e), (-1, e), self.COLOR_LIGHTBLUE))
    #         style_table.append(('FACE', (0, e), (0, e), 'Helvetica-Bold'))
    #
    #     for e in bold_text:
    #         style_table.append(('FACE', (0, e), (0, e), 'Helvetica-Bold'))
    #
    #     # ############ CREATE TABLE ################################
    #     final_table = Table(big_table, colWidths=col_width,
    #                         style=style_table, repeatRows=3)
    #     self.story.append(final_table)
    #
    # def write_mecc_table(self):
    #     table_style = TableStyle()
    #     table_style.add('BOX', (0, 0), (-1, -1), 1, self.COLOR_TEXT)
    #     table_style.add('BACKGROUND', (1, 0), (1, 0), self.COLOR_DARKBLUE)
    #     table_style.add('ALIGN', (0, 0), (-1, -1), 'CENTER')
    #     self.story.append(
    #         Table(
    #             [
    #                 [
    #                     Paragraph(
    #                         '<b>Épreuves</b>',
    #                         self.styles['TextHeader']
    #                     ),
    #                     Paragraph(
    #                         '(E = Écrit, O = Oral, A = Autre)',
    #                         self.styles['NormalRight']
    #                     )
    #                 ]
    #             ],
    #             colWidths=['50%', '50%']
    #         )
    #     )
    #     self.story.append(Spacer(0, 12))
    #     self.mecctable_story()

    def write_rules(self):
        self.story.append(
            Paragraph(
                "<b>Règles applicables à la formation</b>",
                self.styles['TextHeader']
            )
        )

        rules = Rule.objects.filter(
            code_year=self.year.code_year,
            degree_type=self.training.degree_type
        ).order_by('display_order')
        if self.training.MECC_type == 'C':  # cc/ct
            rules = rules.filter(is_ccct=1)
        if self.training.MECC_type == 'E':  # eci
            rules = rules.filter(is_eci=1)
        training_specifics = SpecificParagraph.objects.filter(
            training=self.training
        )
        training_additionals = AdditionalParagraph.objects.filter(
            training=self.training
        )

        for rule in rules:
            self.story.append(
                Paragraph(
                    "<b>{}</b>".format(filter_content(rule.label)),
                    self.styles['TextSubHeader']
                )
            )
            self.story.append(
                HRFlowable(
                    width="100%",
                    thickness=1,
                    lineCap='round',
                    color=self.COLOR_DARKBLUE,
                    spaceBefore=1,
                    spaceAfter=1,
                    hAlign='LEFT',
                    vAlign='BOTTOM',
                    dash=None
                )
            )
            paragraphs = RuleParagraph.objects.filter(
                rule=rule
            ).order_by('display_order')
            to_write = []
            for paragraph in paragraphs:
                if paragraph.id in [specific.paragraph_gen_id for specific in training_specifics]:
                    to_write.append(training_specifics.get(
                        paragraph_gen_id=paragraph.id
                    ))
                else:
                    to_write.append(paragraph)
            self.write_rules_paragraphs(to_write)
            if rule.id in [additional.rule_gen_id for additional in training_additionals]:
                to_write = training_additionals.filter(
                    rule_gen_id=rule.id
                )
                self.write_rules_paragraphs(to_write)

    def write_rules_paragraphs(self, paragraphs):
        for paragraph in paragraphs:
            if isinstance(paragraph, RuleParagraph):
                to_write = paragraph.text_standard
            elif isinstance(paragraph, SpecificParagraph):
                to_write = paragraph.text_specific_paragraph
            else:
                to_write = paragraph.text_additional_paragraph
            to_write = self.clean_up(to_write)
            for element in to_write:
                tag, content = element
                if tag == 'p':
                    self.story.append(
                        Paragraph(
                            content,
                            self.styles['RuleText']
                        )
                    )
                elif tag == 'li':
                    self.story.append(
                        Paragraph(
                            content,
                            self.styles['RuleTextBullet']
                        )
                    )

    def clean_up(self, text):
        """
        Paragraphs are stored as HTML paragraphs (with tags like <p></p>)
        This function parses paragraphs and returns a list that contains
        style elements and the text to write
        Only p/ul>li/ol>li elements are considered : em, strong, bold, i etc.
        are directly supported by reportlab
        Ex : [('p','some text to write'), ('li','some bullet')]
        """
        text = text.replace('\r\n', '').replace('\t', '')
        soup = bs(text, 'lxml')

        to_write = []
        paragraphs = soup.body.find_all(["p", "ul"], recursive=False)

        for paragraph in paragraphs:
            if paragraph.name == 'ul' or paragraph.name == 'ol':
                items = paragraph.find_all('li', recursive=False)
                for item in items:
                    if item.string is not None:
                        to_write.append((item.name, item.string))
            else:
                content = " ".join([str(e) for e in paragraph.contents])
                to_write.append((paragraph.name, content))

        return to_write

    def doc_setup(self):
        self.set_doc_title()
        self.set_response()
        self.set_doc_margins()
        self.document = BaseDocTemplate(
            filename=self.response,
            pagesize=A4,
            rightMargin=self.right_margin,
            leftMargin=self.left_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title=self.title,
            author="Université de Strasbourg",
            showBoundary=0
        )
        self.landscape_width, self.landscape_height = landscape(A4)

        self.add_page_templates()

    def set_doc_title(self):
        self.title = "MECC {} - {}".format(self.year, self.training.label)

    def set_response(self):
        self.response = BytesIO()

    def add_page_templates(self):
        # @see https://stackoverflow.com/questions/15349474/how-do-you-change-from-landscape-to-portrait-layout-in-python-reportlab
        frame_portrait = Frame(
            x1=self.left_margin,
            y1=self.bottom_margin,
            width=self.document.width,
            height=self.document.height,
            id='frame_portrait',
            showBoundary=0
        )
        frame_landscape = Frame(
            x1=self.left_margin,
            y1=self.bottom_margin,
            width=self.landscape_width - (self.left_margin * 2),
            height=self.landscape_height - (self.bottom_margin * 2),
            id='frame_landscape',
            showBoundary=0
        )
        portrait_template = PageTemplate(
            id='portrait',
            frames=[frame_portrait],
            onPage=self.make_portrait
        )
        landscape_template = PageTemplate(
            id='landscape',
            frames=[frame_landscape],
            onPage=self.make_landscape
        )
        self.document.addPageTemplates([portrait_template, landscape_template])

    def add_page_number(self, canvas, doc):
        """
        http://www.blog.pythonlibrary.org/2013/08/12/reportlab-how-to-add-page-numbers/
        """
        page_num = canvas.getPageNumber()
        text = "Page {}".format(page_num)

        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillGray(0.3)
        canvas.drawCentredString(
            (canvas._pagesize[0] / 2),
            self.left_margin / 2,
            text
        )
        canvas.restoreState()

    def make_portrait(self, canvas, doc):
        """
        https://stackoverflow.com/questions/15349474/how-do-you-change-from-landscape-to-portrait-layout-in-python-reportlab
        """
        canvas.saveState()
        canvas.setPageSize(A4)
        self.add_page_number(canvas, doc)
        canvas.restoreState()

    def make_landscape(self, canvas, doc):
        canvas.saveState()
        canvas.setPageSize(landscape(A4))
        self.add_page_number(canvas, doc)
        canvas.restoreState()

    def make_styles(self):
        super().make_styles()
        self.styles.add(
            ParagraphStyle(
                name="NormalInversed",
                alignment=TA_CENTER,
                textColor=self.COLOR_TEXT_INVERSED
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='HeaderTitle',
                alignment=TA_CENTER,
                fontSize=14,
                spaceAfter=55,
                textColor=self.COLOR_DARKBLUE
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="NormalCentered",
                alignment=TA_CENTER,
                spaceBefore=15,
                spaceAfter=15)
        )
        self.styles.add(
            ParagraphStyle(
                name="NormalRight",
                alignment=TA_RIGHT,
                spaceBefore=15,
                spaceAfter=15
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TextHeader",
                spaceBefore=10,
                fontSize=12,
                textColor=self.COLOR_DARKBLUE
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TextHeaderInversed",
                spaceBefore=10,
                fontSize=12,
                textColor=self.COLOR_TEXT_INVERSED
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TextSubHeader",
                spaceBefore=15,
                fontSize=11,
                textColor=self.COLOR_DARKBLUE
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="RuleText",
                alignment=TA_JUSTIFY,
                fontSize=10,
                spaceAfter=5,
                leftIndent=25,
                textColor=self.COLOR_TEXT
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='RuleTextBullet',
                alignment=TA_JUSTIFY,
                fontSize=10,
                spaceAfter=5,
                leftIndent=25,
                textColor=self.COLOR_TEXT,
                bulletIndent=25,
                bulletText='•'
            )
        )


if __name__ == '__main__':
    training = Training.objects.get(13)
    p = PublishedMeccPdf(13).build_doc()
