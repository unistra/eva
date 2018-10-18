from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, NextPageTemplate, PageBreak, Table

from mecc.apps.mecctable.models import ObjectsLink, StructureObject, Exam
from mecc.apps.training.models import SpecificParagraph, AdditionalParagraph
from mecc.apps.rules.models import Rule, Paragraph as ParagraphRules

from .model_a import ModelA, LandscapeLeftNumberedCanvas

class ModelB(ModelA):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'b'
        self.mecc_state = True if 'publish' not in self.target else False

    def build_doc(self):


        self.write_toc()

        self.story.append(NextPageTemplate('landscape_header_pagetemplate'))
        self.story.append(PageBreak())
        self.story.append(NextPageTemplate('landscape_pagetemplate'))
        for self.training in self.trainings:


            if self.standard == 'yes':
                self.write_landscape_training_infos()
                self.write_rules()
                self.story.append(PageBreak())

            self.write_landscape_training_infos()
            if self.standard == 'no':
                self.write_derogs_and_adds(
                    motivations=True
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

    def write_rules(self):
        rules = Rule.objects.filter(
            code_year=self.year,
            degree_type=self.training.degree_type,
            is_in_use=True
        ).only('id', 'label').order_by('display_order')

        self.story.append(Paragraph(
            "<u>Règles applicables à la formation</u>",
            style=self.styles['CenteredH1']
        ))

        if self.training.MECC_type == 'E':
            rules = rules.exclude(is_eci=False)
        if self.training.MECC_type == 'C':
            rules.exclude(is_ccct=False)

        training_specifics = SpecificParagraph.objects.filter(
            training=self.training
        ).only('paragraph_gen_id', 'text_specific_paragraph', 'text_motiv')
        training_additionals = AdditionalParagraph.objects.filter(
            training=self.training
        ).only('rule_gen_id', 'text_additional_paragraph')

        rules_table_style = [
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 1, colors.green)
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
            rules_table.append(
                [
                    Paragraph(
                        "%s" % rule.label,
                        style=self.styles['H2']
                    ),
                    '',
                    ''
                ]
            )
            rules_table_style.extend([
                ('SPAN', (0, count_lines), (-1, count_lines)),
                ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 0),
                ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
            ])
            paragraphs = ParagraphRules.objects.filter(rule=rule.id).only('id', 'text_standard')
            for paragraph in paragraphs:
                count_lines += 1
                d = ''
                text_motiv = ''
                if paragraph.id in [specific.paragraph_gen_id for specific in training_specifics]:
                    specific = training_specifics.get(
                        paragraph_gen_id=paragraph.id
                    )
                    text_paragraph = specific.text_specific_paragraph
                    if 'publish' not in self.target:
                        d = Paragraph(
                            "<para textColor=steelblue><b>(D)</b></para>",
                            style=self.styles['CenterNormal']
                        )
                        text_motiv = specific.text_motiv
                        rules_table_style.append(
                            ('VALIGN', (0, count_lines), (0, count_lines), 'MIDDLE')
                        )
                else:
                    text_paragraph = paragraph.text_standard
                rules_table.append([
                    d,
                    Table(
                        [[self.clean_up(text_paragraph)]],
                        style=paragraph_table_style
                    ),
                    ""
                ])
                if 'publish' not in self.target and text_motiv not in ["", '', None]:
                    count_lines += 1
                    rules_table.append([
                        '',
                        Paragraph(
                            "<para textColor=red><u>Motif de la dérogation</u> : %s</para>" % text_motiv,
                            style=self.styles['Normal']
                        ),
                        ''
                    ])
                rules_table_style.extend([
                    ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 3),
                    ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
                    ('RIGHTPADDING', (1, count_lines), (1, count_lines), 10),
                    # ('LINEBELOW', (1, count_lines), (2, count_lines), 0.75, colors.lightgrey)
                ])
            if rule.id in [additional.rule_gen_id for additional in training_additionals]:
                count_lines += 1
                text_additional = training_additionals.get(
                    rule_gen_id=rule.id
                ).text_additional_paragraph
                rules_table.append([
                    Paragraph(
                        "<para textColor=green><b>(A)</b></para>",
                        style=self.styles['CenterNormal']
                    ) if 'publish' not in self.target else '',
                    Table(
                        [[self.clean_up(text_additional)]],
                        style=paragraph_table_style
                    ),
                    ''
                ])
                rules_table_style.extend([
                    ('VALIGN', (0, count_lines), (0, count_lines), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 3),
                    ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
                    ('RIGHTPADDING', (1, count_lines), (1, count_lines), 10),
                    # ('LINEBELOW', (1, count_lines), (2, count_lines), 0.75, colors.lightgrey)
                ])
        self.story.append(Table(
            rules_table,
            style=rules_table_style,
            colWidths=[1*cm, 18.65*cm, 8*cm]
        ))
