import itertools
from io import BytesIO
from math import modf

import xlsxwriter

from mecc.apps.mecctable.models import StructureObject, ObjectsLink, Exam
from mecc.apps.utils.queries import get_mecc_table_order


class MeccTable:
    COLOR_DARKBLUE = '#4682B3'
    COLOR_LIGHTBLUE = '#AFC3DD'
    COLOR_LIGHTGREY = '#D3D3D3'
    COLOR_DARKGREY = '#808080'
    COLOR_TEXT = '#000000'
    COLOR_TEXT_INVERSED = '#FFFFFF'

    def __init__(self):
        self.references = 'with_si_scol'
        self.formats = {}
        self.current_row = 0

    def get_mecc_tables(self, trainings, institute, year, references):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)

        self.references = references
        self.formats = self.define_formats(workbook)

        for training in trainings:
            worksheet = workbook.add_worksheet(training.label)
            training_is_ccct = True if training.MECC_type == 'C' else False

            self.write_worksheet_headers(institute, worksheet, training, year, references)
            self.write_training_headers(worksheet, training)

            current_structures = StructureObject.objects.filter(code_year=year)
            current_links = ObjectsLink.objects.filter(code_year=year)
            current_exams = Exam.objects.filter(code_year=year)
            root_link = current_links.filter(
                id_parent=0, id_training=training.id
            ).order_by(
                'order_in_child'
            ).distinct()
            links = get_mecc_table_order([e for e in root_link], [], current_structures,
                                         current_links, current_exams, all_exam=True)

            self.current_row = 8
            for link in links:
                self.write_training_data(link, worksheet, training_is_ccct)

        workbook.close()
        output.seek(0)

        return output

    def write_training_data(self, what, worksheet, training_is_ccct):
        self.current_row += 1

        struct = what.get('structure')
        link = what.get('link')
        exams_1 = what.get('exams_1')
        exams_2 = what.get('exams_2')

        def formatted(number):
            frac, whole = modf(number)
            if frac == 0:
                return int(whole)
            else:
                return str(number).rstrip('0')

        def write_exams(list_1, list_2, worksheet, cell_format):

            def write_session(session, start_column, worksheet, first_session=True):
                ccct = session.convocation if not training_is_ccct else session.get_type_ccct_display()
                label = session.label
                if session.additionnal_info is not None:
                    label += "\n" + session.additionnal_info

                worksheet.write(self.current_row, start_column, formatted(session.coefficient), cell_format)
                worksheet.write(self.current_row, start_column + 1, label, cell_format)
                worksheet.write(self.current_row, start_column + 2, session.type_exam, cell_format)
                worksheet.write(self.current_row, start_column + 3, session.text_duration, cell_format)
                if first_session:
                    worksheet.write(self.current_row, start_column + 4, ccct, cell_format)
                    worksheet.write(self.current_row, start_column + 5, session.eliminatory_grade, cell_format)
                    worksheet.write(self.current_row, start_column + 6, session.threshold_session_2, cell_format)
                else:
                    worksheet.write(self.current_row, start_column + 4, session.eliminatory_grade, cell_format)

            for ex_1, ex_2 in itertools.zip_longest(list_1, list_2):
                if ex_1 is not None:
                    write_session(ex_1, 6, worksheet, True)
                else:
                    worksheet.write(self.current_row, 6, '', cell_format)
                    worksheet.write(self.current_row, 7, '', cell_format)
                    worksheet.write(self.current_row, 8, '', cell_format)
                    worksheet.write(self.current_row, 9, '', cell_format)
                    worksheet.write(self.current_row, 10, '', cell_format)
                    worksheet.write(self.current_row, 11, '', cell_format)
                    worksheet.write(self.current_row, 12, '', cell_format)
                if ex_2 is not None:
                    write_session(ex_2, 13, worksheet, False)
                else:
                    worksheet.write(self.current_row, 13, '', cell_format)
                    worksheet.write(self.current_row, 14, '', cell_format)
                    worksheet.write(self.current_row, 15, '', cell_format)
                    worksheet.write(self.current_row, 16, '', cell_format)
                    worksheet.write(self.current_row, 17, '', cell_format)
                if len(list_1) > 1 and len(list_2) > 1:
                    self.current_row += 1

        ref_scol = struct.ref_si_scol if struct.ref_si_scol else ""
        if self.references == 'with_rof':
            ref = struct.ROF_ref
        elif self.references == 'without':
            ref = ''
        elif self.references == 'both':
            ref = ref_scol + "\n" + struct.ROF_ref
        else:
            ref = ref_scol

        if what.get('rank') == 0:
            cell_format = self.formats['header_top_element']
        else:
            cell_format = self.formats['default']
        worksheet.write(self.current_row, 0, '  ' * what.get('rank') + struct.label, cell_format)
        worksheet.write(self.current_row, 1,
                        struct.get_respens_name if not struct.external_name else struct.external_name, cell_format)
        worksheet.write(self.current_row, 2, ref, cell_format)
        worksheet.write(self.current_row, 3, struct.ECTS_credit if struct.ECTS_credit else '-', cell_format)
        worksheet.write(self.current_row, 4, formatted(link.coefficient) if link.coefficient else '', cell_format)
        worksheet.write(self.current_row, 5, link.eliminatory_grade, cell_format)
        write_exams(exams_1, exams_2, worksheet, cell_format)

        for e in what.get('children'):
            self.write_training_data(e, worksheet, training_is_ccct)

    def write_training_headers(self, worksheet, training):
        if training.MECC_type == 'E':
            mecc_type = 'Convocation'
        else:
            mecc_type = 'CC/CT'
        worksheet.merge_range('A7:F7', 'Objets', self.formats['header4'])
        worksheet.merge_range('G7:R7', 'Épreuves', self.formats['header5'])
        worksheet.merge_range('A8:F8', '', self.formats['default'])
        worksheet.merge_range('G8:M8', 'Session principale', self.formats['header6'])
        worksheet.merge_range('N8:R8', 'Session de rattrapage', self.formats['header7'])
        col = 0
        for header in ('Intitulé', 'Responsable', 'Réf', 'ECTS', 'Coefficient', 'Note seuil'):
            worksheet.write(8, col, header, self.formats['default'])
            col = col + 1
        col = 6
        for header in ('Coefficient', 'Intitulé', 'Type', 'Durée', mecc_type, 'Note seuil', 'Report session 2'):
            worksheet.write(8, col, header, self.formats['header8'])
            col = col + 1
        col = 13
        for header in ('Coefficient', 'Intitulé', 'Type', 'Durée', 'Note seuil'):
            worksheet.write(8, col, header, self.formats['header9'])
            col = col + 1

    def write_worksheet_headers(self, institute, worksheet, training, year, references):
        respforms = ', '.join([e for e in training.get_respform_names])
        mecc_type = training.get_MECC_type_display()
        session_type = training.get_session_type_display()
        if references == 'without':
            ref_label = ''
        elif references == 'with_rof':
            ref_label = "Réf. ROF : %s" % training.ref_cpa_rof
        elif references == 'both':
            ref_label = "Réf. ROF : %s\nRéf. APOGEE : %s" % (training.ref_cpa_rof, training.ref_si_scol)
        else:
            ref_label = "Réf. APOGEE : %s" % training.ref_si_scol
        worksheet.merge_range('A1:R1', "Modalités d'évaluation des connaissances et des compétences",
                              self.formats['header1'])
        worksheet.merge_range('A2:R2', "Année universitaire %s/%s" % (year, int(year) + 1), self.formats['header2'])
        worksheet.merge_range('A3:R3', institute.label, self.formats['header2'])
        worksheet.merge_range('A4:R4', '')
        worksheet.merge_range('A5:F5', training.label, self.formats['header3'])
        worksheet.merge_range('G5:L5', '%s - %s' % (mecc_type, session_type), self.formats['header3'])
        worksheet.merge_range('M5:R5', ref_label, self.formats['header3'])
        worksheet.set_row(4, 20)
        worksheet.merge_range('A6:R6', '', self.formats['default'])
        worksheet.write_rich_string('A6', self.formats['bold'], 'Responsables : ',
                                    self.formats['default'], respforms, self.formats['default'])

    def define_formats(self, workbook):
        formats = {
            'default': workbook.add_format({
                'font_size': 12, 'font_color': self.COLOR_TEXT,
                'align': 'left',
            }),
            'bold': workbook.add_format({
                'bold': True,
            }),
            'header1': workbook.add_format({
                'bold': True,
                'font_size': 12, 'font_color': self.COLOR_DARKBLUE,
                'align': 'center',
            }),
            'header2': workbook.add_format({
                'font_size': 12, 'font_color': self.COLOR_DARKBLUE,
                'align': 'center',
            }),
            'header3': workbook.add_format({
                'bold': True, 'bg_color': self.COLOR_DARKBLUE,
                'align': 'center',
                'font_size': 14, 'font_color': self.COLOR_TEXT_INVERSED,
            }),
            'header4': workbook.add_format({
                'font_color': self.COLOR_TEXT,
                'bold': True,
                'align': 'center',
            }),
            'header5': workbook.add_format({
                'bg_color': self.COLOR_DARKBLUE,
                'font_color': self.COLOR_TEXT_INVERSED, 'bold': True,
                'align': 'center',
            }),
            'header6': workbook.add_format({
                'bg_color': self.COLOR_LIGHTGREY, 'font_color': self.COLOR_TEXT,
                'bold': True,
                'align': 'center',
            }),
            'header7': workbook.add_format({
                'bg_color': self.COLOR_DARKGREY, 'font_color': self.COLOR_TEXT,
                'bold': True,
                'align': 'center',
            }),
            'header8': workbook.add_format({
                'bg_color': self.COLOR_LIGHTGREY, 'font_color': self.COLOR_TEXT,
            }),
            'header9': workbook.add_format({
                'bg_color': self.COLOR_DARKGREY, 'font_color': self.COLOR_TEXT,
            }),
            'header_top_element': workbook.add_format({
                'bg_color': self.COLOR_LIGHTBLUE, 'font_color': self.COLOR_TEXT_INVERSED,
            })
        }

        return formats
