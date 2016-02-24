from django.apps import AppConfig


class AppConfig(AppConfig):

    name = 'mecc'
    verbose_name = 'Modalités d’évaluation des connaissances et compétences'

    def ready(self):

        # import signal handlers
        import mecc.apps.utils.signals
