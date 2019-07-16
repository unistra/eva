import itertools
from io import BytesIO
from math import modf

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Paragraph, Table, TableStyle, Frame
from reportlab.platypus.flowables import Flowable

from mecc.apps.institute.models import Institute
from mecc.apps.mecctable.models import ObjectsLink, StructureObject, Exam
from mecc.apps.training.models import Training
from mecc.apps.utils.documents_generator.utils.pdf import filter_content
from mecc.apps.utils.queries import get_mecc_table_order
from ..document import Document


class PreviewMeccTable(Document):

    def __init__(self, trainings, reference='both'):
        if trainings is not None:
            self.training = Training.objects.get(id=trainings)
        self.reference = reference
        self.respforms = True
        self.mecc_state = True
        self.title_header = "Prévisualisation du tableau"
        self.mecctable_header_line_1 = ["OBJETS", '', '', '', '', '', "ÉPREUVES"]

        self.make_watermark_attributes()
        self.doc_setup()
        self.make_styles()

        self.story = []

    def doc_setup(self):
        self.set_doc_title()
        self.set_response()
        self.set_doc_margins()

        self.buffer = BytesIO()

        self.document = BaseDocTemplate(
            filename=self.buffer,
            pagesize=landscape(A4),
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            title=self.title,
            author="Université de Strasbourg",
            showBoundary=0,
        )

        self.add_page_templates()

    def add_page_templates(self):
        frame_landscape = Frame(
            x1=self.left_margin,
            y1=self.bottom_margin,
            width=self.document.width,
            height=self.document.height,
            id='landscape_frame',
            showBoundary=0
        )

        landscape_pagetemplate = PageTemplate(
            id='landscape_pagetemplate',
            frames=[frame_landscape],
            onPage=self.footer_watermark
        )


        self.document.addPageTemplates([landscape_pagetemplate])

    def set_doc_title(self):
        self.title = "Prévisualisation du tableau"

    def set_response(self):
        self.response = HttpResponse(content_type='application/pdf')
        self.response['Content-Disposition'] = ('filename="%s.pdf"' % self.title)

    def set_doc_margins(self):
        self.left_margin = self.right_margin = self.top_margin = self.bottom_margin = 10*mm

    def make_styles(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CenterSmall',
            alignment=TA_CENTER,
            fontSize=8
        ))
        self.styles.add(ParagraphStyle(
            name='CenterSmallItalic',
            alignment=TA_CENTER,
            fontSize=8,
            fontName="Times-Italic"
        ))
        self.styles.add(ParagraphStyle(
            name='SmallNormal',
            fontSize=8
        ))
        self.styles.add(ParagraphStyle(
            name='SmallBold',
            fontSize=8,
            fontName="Helvetica-Bold"
        ))
        self.styles.add(ParagraphStyle(
            name='InversedBigBold',
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        ))

    def make_watermark_attributes(self, string='Prévisualisation', x=500, y=-75, rotation=40):
        self.watermark_string = string
        self.watermark_position_x = x
        self.watermark_position_y = y
        self.watermark_rotation = rotation

    def build_doc(self):
        self.write_preview_header()
        self.write_landscape_training_infos()
        self.write_table_title()
        self.write_mecctable()
        self.document.build(
            self.story,
            canvasmaker=LandscapeLeftNumberedCanvas
        )

        pdf = self.buffer.getvalue()
        self.buffer.close()
        self.response.write(pdf)

        return self.response

    def write_preview_header(self):
        self.story.append(
            Paragraph(
                "<para align=center fontSize=14 spaceAfter=14 textColor=red>\
                <strong>%s</strong></para>" % filter_content(self.title_header),
                self.styles['Normal']
            )
        )

    def write_landscape_training_infos(self):

        # ############ STYLES ################################
        main_style = [
            ('SPAN', (0, 1), (2, 1)),
            ('SPAN', (3, 0), (3, 1)),
            ('VALIGN', (0, 0), (2, 1), 'MIDDLE'),
            ('FACE', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('SIZE', (0, 0), (2, 0), 11),
            ('TEXTCOLOR', (0, 0), (2, 1), colors.white),
            ('BACKGROUND', (0, 0), (-2, -2), colors.steelblue),
            ('BOX', (0, 0), (-2, -1), 1, colors.black),
            ('LINEABOVE', (0, -1), (-2, -1), 1, colors.black),
            # ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            # ('GRID', (0, 0), (-1, -1), 1, colors.green)
        ]

        side_style = [
            ('BOX', (0, 0), (-1, -1), 0.5, colors.steelblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.steelblue),
            ('FACE', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FACE', (0, 1), (-1, 1), 'Helvetica'),
            ('SIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 1, colors.red)
        ]

        # ############ TABLE ################################
        date_cmp = self.training.date_val_cmp.strftime(
            "%d/%m/%Y") if self.training.date_val_cmp not in [None, ''] else "Non"
        date_des = self.training.date_visa_des.strftime(
            "%d/%m/%Y") if self.training.date_visa_des not in [None, ''] else "Non"
        date_cfvu = self.training.date_val_cfvu.strftime(
            "%d/%m/%Y") if self.training.date_val_cfvu not in [None, ''] else "Non"

        mecc_state_table = [
            ["Etat de saisie :"],
            ["%s : %s  %s : %s" % (
                "Règles", self.training.get_progress_rule_display().lower(),
                "Tableau", self.training.get_progress_table_display().lower())
            ],
            ["%s : %s" % ("Validation Composante", date_cmp)],
            ["%s : %s" % ("Visa DES", date_des)],
            ["%s : %s" % ("Validation CFVU", date_cfvu)],
        ]

        if self.reference == 'without':
            ref_label = ''
        elif self.reference == 'with_rof':
            ref_label = "Référence ROF : %s" % self.training.ref_cpa_rof \
                if self.training.ref_cpa_rof is not None else ''
        elif self.reference == 'both':
            ref_label = "Référence ROF : %s\n\nRéférence APOGEE : %s" % (
                self.training.ref_cpa_rof if self.training.ref_cpa_rof is not None \
                    else '',
                self.training.ref_si_scol if self.training.ref_si_scol is not None \
                    else ''
            )
        else:
            ref_label = "Référence APOGEE : %s" % self.training.ref_si_scol

        table = [
            [
                Paragraph("%s" % filter_content(self.training.label), self.styles['InversedBigBold']),
                "%s - %s" % (
                    self.training.get_MECC_type_display(),
                    self.training.get_session_type_display()
                ),
                ref_label,
                Table(
                    mecc_state_table,
                    style=side_style
                ) if self.mecc_state else ''
            ],
            [
                Paragraph(
                    "<para fontSize=11><strong>Responsable(s) : \
                    </strong>%s</para>" % ", ".join(
                        [e for e in self.training.get_respform_names]
                    ),
                    self.styles['Normal']
                ),
                '',
                '',
                ''
            ]
        ]

        final_table = Table(
            table,
            style=main_style,
            colWidths=[
                9*cm if self.mecc_state else 12*cm,
                5*cm if self.mecc_state else 7.15*cm,
                6.5*cm if self.mecc_state else 8.5*cm,
                7.15*cm if self.mecc_state else 0*cm
            ],
            spaceBefore = 10,
        )

        self.story.append(final_table)

    def write_table_title(self):
        table_title_style = [
            ('FACE', (-1, -1), (-1, -1), 'Helvetica'),
            ('FACE', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.steelblue),
            ('SIZE', (0, 0), (0, 0), 12),
            ('SIZE', (-1, -1), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
            # ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 1, colors.green)
        ]
        table_title = Table(
            [
                ["Tableau MECC", "(E = Écrit, O = Oral, A = Autre)"]
            ],
            style=table_title_style,
            colWidths=[
                '50%',
                '50%'
            ],
            spaceAfter=8,
            spaceBefore=5
        )

        self.story.append(table_title)

    def write_mecctable(self):

        current_structures = StructureObject.objects.filter(
            code_year=self.training.code_year
        )
        current_links = ObjectsLink.objects.filter(
            code_year=self.training.code_year
        )
        # Ne pas inclure les objets dont le témoin is_existing_rof = False
        # si composante en appui ROF ou formation de type Catalogue NS cf #131
        supply_cmp = Institute.objects.get(code=self.training.supply_cmp)
        if supply_cmp.ROF_support or self.training.degree_type.ROF_code == 'EA':
            current_links = current_links.exclude(is_existing_rof=False)
        current_exams = Exam.objects.filter(
            code_year=self.training.code_year
        )

        training_is_ccct = True if self.training.MECC_type == 'C' else False

        root_link = current_links.filter(
            id_parent='0',
            id_training=self.training.id).order_by(
                'order_in_child').distinct()
        links = get_mecc_table_order(
            [e for e in root_link],
            [],
            current_structures, current_links,
            current_exams, self.training, all_exam=True
        )

        col_width, width_exams, mecc_table_style, big_table = \
            self.make_mecctable_header(training_is_ccct)

        global count_row
        count_row = 2
        background_blue = []

        # ############ POPULATING TABLE ################################

        def write_the_table(what):
            """
            Recursively add data in strucuture
            """
            global count_row
            count_row += 1

            if what.get('rank') == 0:
                background_blue.append(count_row)

            struct = what.get('structure')
            link = what.get('link')
            exams_1 = what.get('exams_1')
            exams_2 = what.get('exams_2')
            exams_empty = [['', '', '', '', '', '', '', '', '', '', '', '']] \
                if self.training.session_type != '1' else \
                [['', '', '', '', '', '']]

            def formated(number):
                """
                Remove trailing 0
                """
                frac, whole = modf(number)
                if frac == 0:
                    return int(whole)
                return str(number).rstrip('0')

            def write_exams(list_1, list_2):
                exam_table = []
                for ex_1, ex_2 in itertools.zip_longest(list_1, list_2):
                    ex_1_table = [
                        formated(ex_1.coefficient) if ex_1 is not None else '',
                        [
                            Paragraph(filter_content(ex_1).label if ex_1 else '',
                                      self.styles['SmallNormal']),
                            Paragraph(
                                "<para textColor=grey>" + filter_content(ex_1.additionnal_info) \
                                if ex_1 and ex_1.additionnal_info \
                                else "" + "</para\>",
                                self.styles['SmallNormal'])
                        ],
                        ex_1.type_exam if ex_1 is not None else '',
                        ex_1.text_duration if ex_1 is not None else '',
                        '' if ex_1 is None \
                            else ex_1.convocation if not training_is_ccct \
                            else ex_1.get_type_ccct_display(),
                        ex_1.eliminatory_grade if ex_1 is not None else '',
                        ex_1.threshold_session_2 if ex_1 is not None else '',
                    ]

                    ex_2_table = [
                        formated(ex_2.coefficient) if ex_2 is not None else '',
                        [Paragraph(filter_content(ex_2.label) if ex_2 is not None else '', self.styles[
                            'SmallNormal']), Paragraph("<para textColor=grey\
                            >" + ex_2.additionnal_info + "</para\
                            >" if ex_2.additionnal_info is not None else "",
                                                       self.styles['SmallNormal'])],
                        ex_2.type_exam if ex_2 is not None else '',
                        ex_2.text_duration if ex_2 is not None else '',
                        ex_2.eliminatory_grade if ex_2 is not None else '',
                    ] if ex_2 is not None else ['', '', '', '', '']
                    if self.training.session_type != '1':
                        ex_1_table.extend(ex_2_table)
                    else:
                        ex_1_table.pop()
                    exam_table.append(ex_1_table)
                exam_table = exam_table if len(exam_table) > 0 else exams_empty
                if exam_table == exams_empty:
                    # TODO: calculate empty space to set rowHeights in order to
                    # avoid blank in table
                    pass
                inner_table = Table(
                    exam_table, colWidths=width_exams, rowHeights=None)
                inner_table.setStyle(TableStyle(
                    [('INNERGRID', (0, 0), (-1, -1), 0.1, colors.black),
                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                     ('FONTSIZE', (0, 0), (-1, -1), 8),
                     # ('LEFTPADDING', (0, 0), (-1, -1), 0),
                     # ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                     ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                     ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ]))
                return inner_table

            ref_scol = struct.ref_si_scol if struct.ref_si_scol else ""  # FIX bug with rof data
            ref_data = (
                Paragraph(struct.ROF_ref, self.styles['CenterSmall']),
                Paragraph(ref_scol, self.styles['CenterSmall'])
            ) if self.reference == 'both' \
                else Paragraph(struct.ROF_ref, self.styles['CenterSmall']) if self.reference == 'with_rof' \
                else Paragraph(ref_scol, self.styles['CenterSmall']) if self.reference == 'with_si' \
                else Paragraph('', self.styles['CenterSmall'])

            object_line = [
                Paragraph(
                    "<para leftIndent=%s>%s</para> " % (what.get('rank')*10, filter_content(struct.label)),
                    self.styles['SmallBold'] if what.get('rank') == 0 \
                        or what.get('structure').nature == 'UE' \
                        else self.styles['SmallNormal']
                ),
                Paragraph(
                    struct.get_respens_name if not struct.external_name \
                        else struct.external_name,
                    self.styles['CenterSmall'] if not struct.external_name else \
                        self.styles['CenterSmallItalic']
                ),
                [ref_data],
                '30' if self.training.degree_type.ROF_code in self.training_types_for_which_to_display_30_ects\
                    and struct.nature == 'SE'\
                    else struct.ECTS_credit if struct.ECTS_credit else '-',
                formated(link.coefficient) if link.coefficient else '',
                link.eliminatory_grade,
                write_exams(exams_1, exams_2)
            ]
            if self.respforms:
                if self.reference == 'without':
                    object_line.pop(2)
            else:
                object_line.pop(1)
                if self.reference == 'without':
                    object_line.pop(1)

            big_table.append(object_line)

            for e in what.get('children'):
                write_the_table(e)

        for e in links:
            write_the_table(e)

        for e in range(3, len(big_table)):
            if self.respforms:
                if self.reference == 'without':
                    mecc_table_style.append(('SPAN', (5, e), (-1, e)))
                else:
                    mecc_table_style.append(('SPAN', (6, e), (-1, e)))
            else:
                if self.reference == 'without':
                    mecc_table_style.append(('SPAN', (4, e), (-1, e)))
                else:
                    mecc_table_style.append(('SPAN', (5, e), (-1, e)))

        for e in background_blue:
            mecc_table_style.append(
                ('BACKGROUND', (0, e), (-1, e), colors.lightsteelblue)
            )

        col_width.extend(width_exams)

        mecc_table = Table(
            big_table,
            style=mecc_table_style,
            colWidths=col_width,
            repeatRows=3
        )

        self.story.append(mecc_table)

    def make_mecctable_header(self, training_is_ccct):

        references = '<para textColor=steelblue><strong>%s</strong></para>' % (
            "Référence ROF <br></br><br></br> Référence APOGEE" \
                if self.reference == "both" \
                else "Référence ROF" if self.reference == "with_rof" \
                else 'Référence APOGEE' if self.reference == "with_si" \
                else ''
        )

        # ############ TABLE STRUCUTURE ################################

        mecc_table_style = [
            # POLICE
            ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FACE', (0, 1), (-1, 1), 'Helvetica-Bold'),
            # FUSION DE CELLULES
            ('SPAN', (0, 1), (0, 2)),
            ('SPAN', (1, 1), (1, 2)),
            ('SPAN', (2, 1), (2, 2)),
            ('SPAN', (3, 1), (3, 2)),
            ('SPAN', (4, 1), (4, 2)),
            # MARGES INTERIEURES DES CELLULES
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            # QUADRILLAGE
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]

        # - Ugly but tables are almost always ugly
        mecctable_header_line_2 = [
            'Intitulé',
            'Responsable',
            Paragraph(
                references,
                self.styles['CenterSmall']
            ),
            VerticalText('Crédit ECTS'),
            VerticalText('Coefficient'),
            VerticalText('Seuil compens.'),
            'Session principale' if self.training.session_type != '1' \
                else 'Session unique',
            '', '', '', '', '', '',
            'Session de rattrapage'
        ]

        mecctable_header_line_3 = [
            '', '', '', '', '', '',
            VerticalText('Coefficient'),
            'Intitulé',
            VerticalText('Type'),
            VerticalText('Durée'),
            VerticalText(
                'Convocation' if not training_is_ccct else 'CC/CT'),
            VerticalText('Seuil compens.'),
            VerticalText(' Report session 2 '),
            VerticalText('Coefficient'),
            'Intitulé',
            VerticalText('Type'),
            VerticalText('Durée'),
            VerticalText('Seuil compens.')
        ]

        if self.respforms:
            if self.reference == 'without':
                mecctable_header_line_2.pop(2)
                mecctable_header_line_3.pop(2)

                mecc_table_style.extend([
                    ('FACE', (0, 0), (4, 2), 'Helvetica-Bold'),
                    ('FACE', (5, 0), (-1, 0), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (5, 0), (-1, 0), colors.white),
                    ('SPAN', (0, 0), (4, 0)),
                    ('SPAN', (5, 0), (-1, 0)),
                    ('BACKGROUND', (5, 0), (-1, 0), colors.steelblue)
                ])

                big_table = [
                    self.mecctable_header_line_1,
                ]


                if self.training.session_type == '1':
                    big_table.extend([
                        mecctable_header_line_2[:6],
                        mecctable_header_line_3[:11]
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (5, 1), (-1, 1)),
                        ('BACKGROUND', (5, 1), (-1, 1), colors.lightgrey),
                        ('BACKGROUND', (5, 2), (-1, 2), colors.lightgrey)
                    ])

                    col_width = [9.25*cm, 3.5*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 9.25*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm]

                else:
                    big_table.extend([
                        mecctable_header_line_2,
                        mecctable_header_line_3
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (5, 1), (11, 1)),
                        ('SPAN', (12, 1), (-1, 1)),
                        ('BACKGROUND', (5, 1), (11, 1), colors.lightgrey),
                        ('BACKGROUND', (5, 2), (11, 2), colors.lightgrey),
                        ('BACKGROUND', (12, 1), (-1, 1), colors.grey),
                        ('BACKGROUND', (12, 2), (-1, 2), colors.grey)
                    ])

                    col_width = [6.6*cm, 2.25*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 4.6*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm, 0.7*cm,
                                   0.85*cm, 4.6*cm, 0.6*cm, 1.1*cm, 0.7*cm]
            else:
                mecc_table_style.extend([
                    ('FACE', (0, 0), (5, 2), 'Helvetica-Bold'),
                    ('FACE', (6, 0), (-1, 0), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (6, 0), (-1, 0), colors.white),
                    ('SPAN', (5, 1), (5, 2)),
                    ('SPAN', (0, 0), (5, 0)),
                    ('SPAN', (6, 0), (-1, 0)),
                    ('BACKGROUND', (6, 0), (-1, 0), colors.steelblue)
                ])

                big_table = [
                    self.mecctable_header_line_1,
                ]

                if self.training.session_type == '1':
                    big_table.extend([
                        mecctable_header_line_2[:7],
                        mecctable_header_line_3[:12]
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (6, 1), (-1, 1)),
                        ('BACKGROUND', (6, 1), (-1, 1), colors.lightgrey),
                        ('BACKGROUND', (6, 2), (-1, 2), colors.lightgrey)
                    ])

                    col_width = [8.65*cm, 2.9*cm, 1.8*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 8.65*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm]
                else:
                    big_table.extend([
                        mecctable_header_line_2,
                        mecctable_header_line_3
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (6, 1), (12, 1)),
                        ('SPAN', (13, 1), (-1, 1)),
                        ('BACKGROUND', (6, 1), (12, 1), colors.lightgrey),
                        ('BACKGROUND', (6, 2), (12, 2), colors.lightgrey),
                        ('BACKGROUND', (13, 1), (-1, 1), colors.grey),
                        ('BACKGROUND', (13, 2), (-1, 2), colors.grey)
                    ])

                    col_width = [6*cm, 2.25*cm, 1.8*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 4*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm, 0.7*cm,
                                   0.85*cm, 4*cm, 0.6*cm, 1.1*cm, 0.7*cm]
        else:
            mecctable_header_line_2.pop(1)
            mecctable_header_line_3.pop(1)
            if self.reference == 'without':
                mecctable_header_line_2.pop(1)
                mecctable_header_line_3.pop(1)

                mecc_table_style.extend([
                    ('FACE', (0, 0), (3, 2), 'Helvetica-Bold'),
                    ('FACE', (4, 0), (-1, 0), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (4, 0), (-1, 0), colors.white),
                    ('SPAN', (0, 0), (3, 0)),
                    ('SPAN', (4, 0), (-1, 0)),
                    ('BACKGROUND', (4, 0), (-1, 0), colors.steelblue)
                ])

                big_table = [
                    self.mecctable_header_line_1,
                ]

                if self.training.session_type == '1':
                    big_table.extend([
                        mecctable_header_line_2[:5],
                        mecctable_header_line_3[:10]
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (4, 1), (-1, 1)),
                        ('BACKGROUND', (4, 1), (-1, 1), colors.lightgrey),
                        ('BACKGROUND', (4, 2), (-1, 2), colors.lightgrey)
                    ])

                    col_width = [11*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 11*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm]

                else:
                    big_table.extend([
                        mecctable_header_line_2,
                        mecctable_header_line_3
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (4, 1), (10, 1)),
                        ('SPAN', (11, 1), (-1, 1)),
                        ('BACKGROUND', (4, 1), (10, 1), colors.lightgrey),
                        ('BACKGROUND', (4, 2), (10, 2), colors.lightgrey),
                        ('BACKGROUND', (11, 1), (-1, 1), colors.grey),
                        ('BACKGROUND', (11, 2), (-1, 2), colors.grey)
                    ])

                    col_width = [7.35*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 5.35*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm, 0.7*cm,
                                   0.85*cm, 5.35*cm, 0.6*cm, 1.1*cm, 0.7*cm]
            else:
                mecc_table_style.extend([
                    ('FACE', (0, 0), (4, 2), 'Helvetica-Bold'),
                    ('FACE', (6, 0), (-1, 0), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (5, 0), (-1, 0), colors.white),
                    ('SPAN', (4, 1), (4, 2)),
                    ('SPAN', (0, 0), (4, 0)),
                    ('SPAN', (5, 0), (-1, 0)),
                    ('BACKGROUND', (5, 0), (-1, 0), colors.steelblue)
                ])

                big_table = [
                    self.mecctable_header_line_1,
                ]

                if self.training.session_type == '1':
                    big_table.extend([
                        mecctable_header_line_2[:7],
                        mecctable_header_line_3[:12]
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (5, 1), (-1, 1)),
                        ('BACKGROUND', (5, 1), (-1, 1), colors.lightgrey),
                        ('BACKGROUND', (5, 2), (-1, 2), colors.lightgrey)
                    ])

                    col_width = [10.1*cm, 1.8*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 10.1*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm]
                else:
                    big_table.extend([
                        mecctable_header_line_2,
                        mecctable_header_line_3
                    ])

                    mecc_table_style.extend([
                        ('SPAN', (5, 1), (11, 1)),
                        ('SPAN', (12, 1), (-1, 1)),
                        ('BACKGROUND', (5, 1), (11, 1), colors.lightgrey),
                        ('BACKGROUND', (5, 2), (11, 2), colors.lightgrey),
                        ('BACKGROUND', (12, 1), (-1, 1), colors.grey),
                        ('BACKGROUND', (12, 2), (-1, 2), colors.grey)
                    ])

                    col_width = [6.75*cm, 1.8*cm, 0.6*cm, 0.6*cm, 0.6*cm]
                    width_exams = [0.85*cm, 4.75*cm, 0.6*cm, 1.1*cm, 0.6*cm, 0.7*cm, 0.7*cm,
                                   0.85*cm, 4.75*cm, 0.6*cm, 1.1*cm, 0.7*cm]

        return col_width, width_exams, mecc_table_style, big_table

    def footer_watermark(self, canvas, doc):
        self.custom_watermark(canvas, doc)

    def custom_watermark(self, canvas, doc):
        """
        Add a custom watermark
        """
        canvas.saveState()
        canvas.setFont('Helvetica', 45)
        canvas.setFillGray(0.80)
        canvas.rotate(self.watermark_rotation)
        canvas.drawCentredString(
            self.watermark_position_x,
            self.watermark_position_y,
            self.watermark_string
        )
        canvas.restoreState()


class VerticalText(Flowable):
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


class LandscapeLeftNumberedCanvas(canvas.Canvas):
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
        draw page number with custom format and position
        """
        if page_count > 0:
            self.setFillGray(0.2)
            self.setFont("Helvetica", 8)
            self.drawRightString(
                position_x * mm, position_y * mm, "Page %d/%d" %
                (self._pageNumber, page_count))
