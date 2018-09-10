from django.core.management import BaseCommand

from mecc.apps.training.models import Training
from mecc.apps.utils.published_mecc_pdf import PublishedMeccPdf


class Command(BaseCommand):

    def handle(self, *args, **options):
        training = Training.objects.get(pk=5)
        pdf = PublishedMeccPdf(training).build_doc()
