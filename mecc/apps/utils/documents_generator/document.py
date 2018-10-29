from abc import ABCMeta, abstractmethod


class Document(metaclass=ABCMeta):

    training_types_for_which_to_display_30_ects = [
        'DE', 'DT', 'UF', 'GE', 'IE', 'XA',
        'DP', 'XB', 'DS', 'DF', 'PS', 'PA'
    ]

    @staticmethod
    def generate(gen_type='pdf', model='a', **kwargs):
        if gen_type == 'doc':
            if model == 'a':
                from .models import ModelADocx
                return ModelADocx(**kwargs).build_doc()
            if model == 'b':
                from .models import ModelBDocx
                return ModelBDocx(**kwargs).build_doc()
        if gen_type == 'excel':
            from .models import MeccTableExcel
            return MeccTableExcel(**kwargs).build_doc()
        if gen_type == 'pdf':
            if model == 'preview_mecctable':
                from .models import PreviewMeccTable
                return PreviewMeccTable(**kwargs).build_doc()
            if model == 'preview_mecc':
                from .models import PreviewMecc
                return PreviewMecc(**kwargs).build_doc()
            if model == 'a':
                from .models import ModelA
                return ModelA(**kwargs).build_doc()
            if model == 'b':
                from .models import ModelB
                return ModelB(**kwargs).build_doc()
            if model == 'e':
                from .models import ModelE
                return ModelE(**kwargs).build_doc()

    @abstractmethod
    def build_doc(self):
        pass
