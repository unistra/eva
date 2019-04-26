import re

from django.db.models import Q

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table, CondPageBreak

from mecc.apps.rules.models import Rule
from mecc.apps.training.models import SpecificParagraph, AdditionalParagraph
from .preview_mecctable import PreviewMeccTable, LandscapeLeftNumberedCanvas


class PreviewMecc(PreviewMeccTable):
    def __init__(self, trainings=None, reference='both'):
        super().__init__(trainings, reference)
        self.title_header = "Prévisualisation des MECC"

    def set_doc_title(self):
        self.title = "Previsualisation des MECC"

    def make_styles(self):
        super().make_styles()
        self.styles.add(ParagraphStyle(
            name='H1',
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=colors.steelblue,
            spaceBefore=5,
            spaceAfter=5,
        ))
        self.styles.add(ParagraphStyle(
            name='H2',
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=colors.steelblue,
            spaceBefore=3,
            spaceAfter=3,
        ))
        self.styles.add(ParagraphStyle(
            name='IndentedText',
            leftIndent=20
        ))
        self.styles.add(ParagraphStyle(
            name='CenterNormal',
            fontSize=10,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='Justify',
            alignment=TA_JUSTIFY
        ))
        self.styles.add(ParagraphStyle(
            name='Bullet_1',
            bulletIndent=25,
            bulletText="•"
        ))

    def build_doc(self):
        self.write_preview_header()
        self.write_landscape_training_infos()
        self.write_derogs_and_adds()
        self.story.append(CondPageBreak(8*cm))
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

    def write_derogs_and_adds(self, motivations=True):

        derogs = SpecificParagraph.objects.\
            filter(training_id=self.training).\
            order_by('paragraph_gen_id')
        adds = AdditionalParagraph.objects.filter(training_id=self.training)
        rules = Rule.objects.\
            filter(code_year=self.training.code_year).\
            filter(
                Q(id__in=[derog.rule_gen_id for derog in derogs]) \
                | \
                Q(id__in=[add.rule_gen_id for add in adds])
            )

        shared_adds = adds.filter(rule_gen_id__in=[derog.rule_gen_id for derog in derogs])
        table_derogs = []
        table_derogs_style = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.green),
        ]
        subtable_style = [
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.red),
        ]
        count_lines = -1
        self.story.append(
            Paragraph(
                "<para>Dérogations et alinéas additionnels</para>",
                self.styles['H1']
            )
        )
        if rules:
            if derogs:
                for rule in rules.filter(id__in=[derog.rule_gen_id for derog in derogs]):
                    count_lines += 1
                    table_derogs.append(
                        [Paragraph(
                            rule.label,
                            style=self.styles['H2']
                        )]
                    )
                    table_derogs_style.extend([
                        ('SPAN', (0, count_lines), (-1, count_lines)),
                        ('TOPPADDING', (0, count_lines), (-1, count_lines), 0),
                        ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 0),
                    ])
                    for derog in derogs.filter(rule_gen_id=rule.id):
                        count_lines += 1
                        table_derogs.append(
                            [
                                Paragraph(
                                    "<para textColor=steelblue><b>(D)</b></para>",
                                    style=self.styles['CenterNormal']
                                ),
                                Table(
                                    [[self.clean_up(derog.text_specific_paragraph)]],
                                    style=subtable_style,
                                ),
                                Paragraph(
                                    "<para textColor=red><u>Motif de la dérogation</u> : %s" \
                                        % derog.text_motiv,
                                    style=self.styles['Normal']
                                ) if motivations else ''
                            ]
                        )
                        table_derogs_style.extend([
                            ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
                            ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 3),
                            ('RIGHTPADDING', (1, count_lines), (1, count_lines), 3),
                            ('LEFTPADDING', (2, count_lines), (2, count_lines), 3),
                        ])
                        if motivations:
                            table_derogs_style.append(
                                ('LINEAFTER', (1, count_lines), (1, count_lines), 0.5, colors.red),
                            )

                    if shared_adds and rule.id in [add.rule_gen_id for add in shared_adds]:
                        add = shared_adds.get(rule_gen_id=derog.rule_gen_id).text_additional_paragraph
                        count_lines += 1
                        table_derogs.append([
                            Paragraph(
                                "<para textColor=green><b>(A)</b></para>",
                                self.styles['CenterNormal']
                            ),
                            Table(
                                [[self.clean_up(add)]],
                                style=subtable_style,
                            ),
                            ""
                        ])
                        table_derogs_style.extend([
                            ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 3),
                            ('RIGHTPADDING', (1, count_lines), (1, count_lines), 3),
                        ])
            if adds:
                if shared_adds:
                    adds = adds.exclude(id__in=[add.id for add in shared_adds])
                for rule in rules.filter(id__in=[add.rule_gen_id for add in adds]):
                    count_lines += 1
                    table_derogs.append(
                        [Paragraph(
                            rule.label,
                            style=self.styles['H2']
                        )]
                    )
                    table_derogs_style.extend([
                        ('SPAN', (0, count_lines), (-1, count_lines)),
                        ('TOPPADDING', (0, count_lines), (-1, count_lines), 0),
                        ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 0),
                    ])
                    for add in adds.filter(rule_gen_id=rule.id):
                        count_lines += 1
                        table_derogs.append(
                            [
                                Paragraph(
                                    "<para textColor=green><b>(A)</b></para>",
                                    style=self.styles['CenterNormal']
                                ),
                                Table(
                                    [[self.clean_up(add.text_additional_paragraph)]],
                                    style=subtable_style,
                                ),
                                ""
                            ]
                        )
                        table_derogs_style.extend([
                            ('TOPPADDING', (0, count_lines), (-1, count_lines), 3),
                            ('BOTTOMPADDING', (0, count_lines), (-1, count_lines), 3),
                        ])
            self.story.append(
                Table(
                    table_derogs,
                    style=table_derogs_style,
                    colWidths=[1*cm, 16.30*cm, 8.35*cm]
                )
            )
        else:
            self.story.append(
                Paragraph(
                    "Néant",
                    self.styles['IndentedText']
                )
            )

    def clean_up(self, text, style=''):
        """
        Return correct string in order to be displayed as list
        """
        text = text.replace('<br>', '<br/>')
        text = text.replace('\\r\\n', '<br/>')
        reg = re.compile(r'>(.*?)</(p|li)>')
        r = reg.findall(text.replace('r\\n\\', '<br><\\br>'))
        _list = []
        for t, v in r:
            if v == 'li':
                _list.append(Paragraph(
                    "<para %s leftIndent=40>%s</para>" % (
                        style, t), self.styles['Bullet_1']))
            else:
                _list.append(Paragraph(
                    "<para %s >%s</para>" % (
                        style, t), self.styles['Justify']))
        return _list
