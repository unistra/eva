import datetime

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import BaseDocTemplate, Paragraph, Table, PageBreak, Image, \
    NextPageTemplate, Frame, PageTemplate, FrameBreak, Spacer
from reportlab.platypus.doctemplate import _doNothing
from reportlab.lib.units import cm

from mecc.apps.mecctable.models import ObjectsLink, StructureObject
from mecc.apps.training.models import Training, SpecificParagraph
from mecc.apps.rules.models import Rule, Paragraph as ParagraphRules
from mecc.apps.utils.queries import currentyear

from .preview_mecc import PreviewMecc
from .preview_mecctable import LandscapeLeftNumberedCanvas


class ModelA(PreviewMecc):
    def __init__(
            self,
            user,
            trainings,
            reference,
            standard,
            target,
            date,
            year,
            task_id):
        self.user = user
        self.trainings = Training.objects\
            .filter(id__in=trainings)\
            .order_by('degree_type', 'MECC_type', 'label')
        self.degree_types = list(set(
            [training.degree_type for training in self.trainings]
        ))
        self.reference = reference
        self.standard = standard
        self.target = target
        self.date = date
        self.task_id = task_id
        if year is not None:
            self.year = int(year)
        else:
            self.year = currentyear().code_year
        self.mecc_state = True if \
            'publish' not in self.target and \
            'eci' not in self.target and \
            'history' not in self. target \
            else False
        print(self.trainings)
        self.cmp = self.trainings.first().supply_cmp_label
        self.today = datetime.date.today().strftime('%d/%m/%Y')
        self.logo = Image('mecc/static/img/signature_uds_02.png', 80, 30)

        print(self.trainings.first().id)
        super().__init__(
            reference=self.reference
        )
        self.model = 'a'
        self.respforms = True if 'eci' not in self.target else False

        self.make_watermark_attributes(
            string='Document intermédiaire' if 'publish' not in self.target \
                and 'history' not in self.target else ''
        )

    def set_doc_title(self):
        if 'publish' in self.target:
            self.goal = 'PUBLICATION'
            self.warning = "Ces MECC sont définitives et ne peuvent pas être modifiées en cours d'année universitaire"
        if 'review' in self.target:
            self.goal_criteria = self.goal = "Relecture"
        if 'eci' in self.target:
            self.goal = "Commission MECC"
        if 'cc' in self.target:
            self.goal_criteria = "Conseil de composante"
            self.goal = self.goal_criteria + " du %s" % self.date
        if self.target == "prepare_cfvu":
            self.goal_criteria = "CFVU"
            self.goal = self.goal_criteria + " du %s" % self.date
        if self.target == "history":
            self.goal = "MECC validées"

        self.title = "MECC - %s/%s - %s - %s" % (
            self.year, self.year+1,
            self.cmp,
            self.goal.upper()
        )
        self.filename = "MECC - %s-%s - %s - %s" % (
            self.year, self.year+1,
            self.cmp,
            self.goal.upper()
        )

    def doc_setup(self):
        self.set_doc_title()
        # self.set_response()
        self.set_doc_margins()

        # self.buffer = BytesIO()

        self.document = BaseDocTemplate(
            filename=settings.MEDIA_ROOT+'/tmp/%s - %s.pdf' % (self.task_id, self.filename),
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
        # ########## FIRST PAGE ##########
        frame_title = Frame(
            x1=self.left_margin,
            y1=14*cm,
            width=self.document.width,
            height=5*cm,
            showBoundary=0,
        )
        if 'publish' not in self.target and \
                'eci' not in self.target and \
                'history' not in self.target:
            frame_criteria = Frame(
                x1=self.left_margin,
                y1=self.bottom_margin,
                width=self.document.width/4,
                height=13*cm,
                showBoundary=0,
            )
        frame_trainings = Frame(
            x1=self.left_margin+self.document.width/4 if \
                'publish' not in self.target and \
                'eci' not in self.target and \
                'history' not in self.target else self.left_margin,
            y1=self.bottom_margin,
            width=(self.document.width*0.75) if \
                'publish' not in self.target and \
                'eci' not in self.target and\
                'history' not in self.target else self.document.width,
            height=13*cm,
            showBoundary=0,
        )

        first_page = PageTemplate(
            id='first_page',
            frames=[frame_title, frame_criteria, frame_trainings] if \
                'publish' not in self.target and \
                'eci' not in self.target and \
                'history' not in self.target else [frame_title, frame_trainings],
            onPage=_doNothing if 'publish' not in self.target else self.publish_footer
        )

        # ########## SECOND PAGE ##########
        frame_trainings_second_page = Frame(
            x1=self.left_margin+self.document.width/4 if \
                'publish' not in self.target and \
                'eci' not in self.target and \
                'history' not in self.target else self.left_margin,
            y1=self.bottom_margin,
            width=(self.document.width*0.75) if \
                'publish' not in self.target and \
                'eci' not in self.target and \
                'history' not in self.target else self.document.width,
            height=self.document.height,
            showBoundary=0,
        )

        second_page = PageTemplate(
            id='second_page',
            frames=[frame_trainings_second_page],
            onPage=_doNothing if 'publish' not in self.target else self.publish_footer
        )

        # ########## HEADER TEMPLATE ###########
        frame_landscape_header = Frame(
            x1=self.left_margin,
            y1=self.bottom_margin,
            width=self.document.width,
            height=self.document.height,
            id='landscape_frame_header',
            showBoundary=0
        )

        landscape_pagetemplate_header = PageTemplate(
            id='landscape_header_pagetemplate',
            frames=[frame_landscape_header],
            onPage=self.header_footer_watermark
        )

        # ########## BASE PAGE TEMPLATE ##########
        frame_landscape = Frame(
            x1=self.left_margin,
            y1=self.bottom_margin,
            width=self.document.width,
            height=self.document.height+0.7*cm,
            id='landscape_frame',
            showBoundary=0
        )

        landscape_pagetemplate = PageTemplate(
            id='landscape_pagetemplate',
            frames=[frame_landscape],
            onPage=self.footer_watermark
        )

        self.document.addPageTemplates([
            first_page,
            second_page,
            landscape_pagetemplate_header,
            landscape_pagetemplate
        ])

    def set_doc_margins(self):
        self.top_margin = 1.7 * cm
        self.bottom_margin = self.left_margin = self.right_margin = cm

    def make_styles(self):
        super().make_styles()
        self.styles.add(ParagraphStyle(
            name='InversedH1',
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=colors.white,
            spaceBefore=5,
            spaceAfter=5,
        ))
        self.styles.add(ParagraphStyle(
            name='CenteredH1',
            fontSize=12,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            textColor=colors.steelblue,
            spaceBefore=5,
            spaceAfter=5,
        ))
        self.styles.add(ParagraphStyle(
            name='CenteredH2',
            fontSize=11,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            textColor=colors.steelblue,
            spaceBefore=5,
            spaceAfter=5,
        ))

        self.styles.add(ParagraphStyle(
            name='CenteredNormal',
            fontName="Helvetica",
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='RightSmall',
            alignment=TA_RIGHT,
            fontSize=8
        ))
        self.styles.add(ParagraphStyle(
            name='CenteredSmall',
            alignment=TA_CENTER,
            fontSize=8
        ))
        self.styles.add(ParagraphStyle(
            name='Big',
            fontSize=12
        ))

    def build_doc(self):
        self.write_toc()
        self.story.append(NextPageTemplate('landscape_header_pagetemplate'))
        self.story.append(PageBreak())
        self.story.append(NextPageTemplate('landscape_pagetemplate'))

        for degree_type in self.degree_types:
            self.write_degree_type_title(degree_type=degree_type)

            if self.standard == 'yes':
                self.write_rules(degree_type=degree_type)
                self.story.append(PageBreak())

            for self.training in self.trainings.filter(degree_type=degree_type):
                self.write_landscape_training_infos()
                self.write_derogs_and_adds(
                    motivations=True if \
                        'publish' not in self.target and \
                        'history' not in self.target \
                        else False
                )
                self.write_table_title()
                self.write_mecctable()
                self.story.append(PageBreak())

        self.document.build(
            self.story,
            canvasmaker=LandscapeLeftNumberedCanvas
        )

        return self.filename

        # pdf = self.buffer.getvalue()
        # self.buffer.close()
        # self.response.write(pdf)
        #
        # return self.response

    def write_toc(self):
        self.story.append(NextPageTemplate('second_page'))

        title = [
            "<font size=22>M</font size=22>odalités d'<font size=22>E</font size=22>valuation des <font size=22>C</font size=22>onnaissances et des <font size=22>C</font size=22>ompétences",
            "Année universitaire %s/%s" % (self.year, self.year+1),
            self.cmp
        ]

        for line in title:
            self.story.append(Paragraph("<para align=center fontSize=16 spaceBefore=16 textColor=\
                steelblue>%s</para>" % line, self.styles['Normal']))
        self.story.append(Spacer(0, 24))

        self.story.append(Paragraph("<para align=center fontSize=16 spaceBefore=24 textColor=\
            steelblue>%s</para>" % "-" * 125, self.styles['Normal']))

        if 'publish' not in self.target and \
                'eci' not in self.target and \
                'history' not in self.target:
            self.story.append(FrameBreak())

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

            criteria_table = Table(
                [
                    ["Critères d'édition"],
                    ["Utilisateur : %s %s" % (self.user[0], self.user[1])],
                    ["Objectif : %s" % self.goal_criteria],
                    ["Modèle : %s" % self.model.upper()],
                    ["Date : %s" % self.today],
                    ["Règles standards : %s" % 'Avec' if self.standard == 'yes' else 'Sans'],
                    ["Références : %s" % 'Sans' if self.reference == 'without' else 'Avec']
                ],
                style=style_criteria_table,
                colWidths=[6*cm]
            )

            self.story.append(criteria_table)

        self.story.append(FrameBreak())

        style_training_list = [
            # ('GRID', (0, 0), (-1, -1), 1, colors.pink),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('SIZE', (0, 0), (-1, -1), 8),

        ]
        style_trainings = [
            # ('GRID', (0, 0), (-1, -1), 1, colors.green),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
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

        training_list = [
            [
                Paragraph(
                    "<para fontSize=9>%s</para>" % training.label,
                    self.styles['Normal']
                ),
                Table(
                    [
                        [
                            "Conseil de composante : %s" % (training.date_val_cmp.strftime(
                                "%d/%m/%Y") if training.date_val_cmp else "Non"),
                            "CFVU : %s " % (training.date_val_cfvu.strftime(
                                "%d/%m/%Y") if training.date_val_cfvu else "Non")
                        ]
                    ],
                    style=style_training_list,
                    colWidths=[5 * cm, 3 * cm]
                )
            ] for training in self.trainings
        ]

        trainings_table = [["Formation", "Dates de validation"]]
        trainings_table.extend(training_list)

        trainings_table = Table(
            trainings_table,
            style=style_trainings,
            colWidths=[6.5 * cm, 8 * cm]
        )
        self.story.append(trainings_table)

    def write_degree_type_title(self, degree_type):
        degree_type_title_style = [
            ('BACKGROUND', (0, 0), (-1, -1), colors.steelblue),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]
        degree_type_title = Table(
            [[Paragraph(
                "%s" % degree_type.short_label.upper(),
                style=self.styles['InversedH1']
            )]],
            style=degree_type_title_style,
            colWidths=[27.65*cm,],
            # spaceAfter=5
        )

        self.story.append(degree_type_title)

    def write_rules(self, degree_type):
        rules = Rule.objects.filter(
            code_year=self.year,
            degree_type=degree_type,
            is_in_use=True
        ).order_by('display_order')

        paragraphs = ParagraphRules.objects.filter(
            code_year=self.year,
            is_in_use=True
        ).order_by('display_order')

        trainings_mecc_types = list(set(
            [training.MECC_type for training in self.trainings.filter(degree_type=degree_type)]
        ))

        self.write_mecc_type_title(
            "all",
            degree_type.short_label
        )
        self.write_rules_table(
            rules.filter(degree_type=degree_type, is_eci=True, is_ccct=True),
            paragraphs,
            degree_type,
        )

        if 'C' in trainings_mecc_types:
            self.write_mecc_type_title(
                "CC/CT",
                degree_type.short_label
            )
            self.write_rules_table(
                rules.filter(degree_type=degree_type, is_eci=False, is_ccct=True),
                paragraphs,
                degree_type,
            )

        if 'E' in trainings_mecc_types:
            self.write_mecc_type_title(
                "ECI",
                degree_type.short_label
            )
            self.write_rules_table(
                rules.filter(degree_type=degree_type, is_eci=True, is_ccct=False),
                paragraphs,
                degree_type,
            )

    def write_mecc_type_title(self, mecc_type, degree_type):
        if mecc_type == "all":
            title = "à tous les diplômes %s selectionnés " % degree_type.upper()
        else:
            title = "aux diplômes %s en régime %s" % (degree_type.upper(), mecc_type)

        self.story.append(Paragraph(
            "<u>Règles applicables "+title+"</u>",
            self.styles['CenteredH1']
        ))

    def write_rules_table(self, rules, paragraphs, degree_type):
        rules_table_style = [
            ('VALIGN', (2, 0), (2, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.green),
        ]
        paragraph_table_style = [
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
        ]
        rules_table = []
        count_lines = -1
        for rule in rules:
            count_lines += 1
            bool_as_exception, exceptions = rule.has_current_exceptions
            adds = [
                add for add in exceptions.get('additionals') if \
                    add.training in self.trainings.filter(degree_type=degree_type) and \
                    add.training.degree_type == degree_type
            ]
            rules_table.append([
                Paragraph(
                    rule.label,
                    style=self.styles['H2']
                ),
                '',
                Paragraph(
                    "<para textColor=green>Additionnels : %s</para>" % len(adds),
                    style=self.styles['RightSmall']
                ) if len(adds) > 0 and 'publish' not in self.target else ''
            ])
            rules_table_style.extend([
                ('SPAN', (0, count_lines), (1, count_lines)),
                ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 0),
                ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
                # ('LINEBELOW', (0, count_lines), (2, count_lines), 1, colors.steelblue)
            ])
            for paragraph in paragraphs.filter(rule=rule):
                count_lines += 1
                derogs = [
                    derog for derog in paragraph.specific_involved if \
                        derog.training in self.trainings.filter(degree_type=degree_type)
                ]
                rules_table.append([
                    "",
                    Table(
                        [[self.clean_up(paragraph.text_standard)]],
                        style=paragraph_table_style
                    ),
                    Paragraph(
                        "Dérogations : %s" % len(derogs),
                        style=self.styles['CenteredSmall']
                    ) if paragraph.is_interaction and 'publish' not in self.target else ''
                ])
                rules_table_style.extend([
                    ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 3),
                    ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
                    ('RIGHTPADDING', (1, count_lines), (1, count_lines), 10),
                    ('LINEBELOW', (1, count_lines), (2, count_lines), 0.75, colors.lightgrey)
                ])
                # if paragraph.is_interaction and 'publish' not in self.target:
                #     rules_table_style.append(
                #         ('LINEBEFORE', (2, count_lines), (2, count_lines), 0.75, colors.grey)
                #     )

        self.story.append(
            Table(
                rules_table,
                style=rules_table_style,
                colWidths=[1*cm, 18.65*cm, 8*cm],
                spaceBefore=0
            ))

    def footer_watermark(self, canvas, doc):
        super().footer_watermark(canvas, doc)
        self.set_footer(canvas, doc)

    def header_footer_watermark(self, canvas, doc):
        self.set_header(canvas, doc)
        self.footer_watermark(canvas, doc)

    def set_header(self, canvas, doc):
        canvas.saveState()

        header_table_style = [
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            # ('BOTTOMPADDING', (0, 0), (0, 0), 2),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.lightgrey),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.green),
        ]
        header_subtable_style = [
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.orange),
        ]
        header_table = [
            [
                self.logo,
                Paragraph(
                    "Modalités d'évaluation des connaissances et des compétences",
                    self.styles['CenteredH2']
                ),
                Table(
                    [
                        [Paragraph(
                            "<para textColor=steelblue>Année universitaire %s/%s</para>" % \
                                (self.year, self.year+1),
                            self.styles['CenteredSmall']
                        )],
                        [Paragraph(
                            "<para textColor=steelblue>%s</para>" % self.cmp,
                            self.styles['CenteredSmall']
                        )]
                    ],
                    style=header_subtable_style
                ),
                Table(
                    [
                        [Paragraph(
                            "<para textColor=steelblue>Edition du %s</para>" % \
                                self.today if 'history' not in self.target \
                                else "<para textColor=steelblue><b>HISTORIQUE</b></para>",
                            self.styles['RightSmall']
                        )],
                        [Paragraph(
                            "<para textColor=steelblue><b>%s</b></para>" % (
                                self.goal.upper() if 'prepare' not in self.target \
                                else self.goal
                            ),
                            self.styles['RightSmall']
                        )]
                    ],
                    style=header_subtable_style
                )
            ]
        ]

        header = Table(
            header_table,
            style=header_table_style,
            colWidths=[3*cm, 15.40*cm, 5*cm, 4.25*cm]
        )
        page_width, page_height = canvas._pagesize
        width, height = header.wrapOn(canvas, page_width, page_height)
        header.drawOn(canvas, self.left_margin, page_height-self.top_margin)

        canvas.restoreState()

    def set_footer(self, canvas, doc):
        canvas.saveState()

        footer = "%s - %s/%s - %s%s" % (
            "MECC" if 'history' not in self.target else "MECC définitives",
            self.year, self.year+1,
            self.cmp,
            " - Edition du %s - %s" % (
                self.today,
                self.goal
            ) if 'eci' not in self.target and 'history' not in self.target else ''
        ) if 'publish' not in self.target else self.warning

        canvas.setFillGray(0.2)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(cm, 0.5*cm, footer)
        
        canvas.restoreState()

    def publish_footer(self, canvas, doc):
        canvas.saveState()

        footer = self.warning
        canvas.setFillColor(colors.steelblue)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(7*cm, 0.5*cm, footer)

        canvas.restoreState()
