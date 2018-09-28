from mecc.apps.rules.models import Rule, Paragraph
from mecc.apps.training.models import SpecificParagraph, AdditionalParagraph

from .model_a_docx import ModelADocx

class ModelBDocx(ModelADocx):

    def build_doc(self):

        # ########## Template clean up : we only want the title section
        doc_paragraphs = self.doc.paragraphs[2:]
        for paragraph in doc_paragraphs:
            self.delete_paragraph(paragraph)
        self.add_lines(2)

        self.write_doc_subtitle()

        degree_types = list(set([training.degree_type for training in self.trainings]))

        for degree_type in degree_types:
            rules = Rule.objects.filter(
                code_year=self.code_year,
                degree_type=degree_type
            ).order_by('display_order')
            self.write_degree_label(degree_type.short_label)

            for training in self.trainings:
                self.write_training_header(training)
                self.add_lines()
                self.doc.add_paragraph(
                    "Règles applicables à la formation",
                    style=self.style_title2
                )
                self.add_lines()
                if training.MECC_type == 'C':
                    training_rules = rules.exclude(is_eci=0)
                if training.MECC_type == 'E':
                    training_rules = rules.exclude(is_ccct=0)
                training_specifics = SpecificParagraph.objects.filter(training=training)
                training_additionals = AdditionalParagraph.objects.filter(training=training)

                for rule in training_rules:
                    self.doc.add_paragraph(rule.label, style=self.style_title3)
                    paragraphs = Paragraph.objects.filter(rule=rule).order_by('display_order')
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
            self.doc.add_page_break()

        self.doc.save(self.response)

        return self.response
