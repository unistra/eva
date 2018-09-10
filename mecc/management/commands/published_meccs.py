from datetime import datetime
from io import BytesIO

from django.core.management.base import BaseCommand
from django.db.models import Q

from mecc.apps.training.models import Training
from mecc.apps.utils.published_mecc_pdf import PublishedMeccPdf
from mecc.apps.utils.queries import currentyear
from mecc.apps.utils.storage.ceph import Ceph


class Command(BaseCommand):
    help = 'Générer les fichiers PDF des MECC validées et les stocker dans Ceph'

    def add_arguments(self, parser):
        parser.add_argument('subcommand', type=str)

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand == 'publish':
            self.publish()

    def publish(self):
        trainings = self.select_trainings_to_publish()
        for training in trainings:
            filename = self.make_filename(training)
            pdf = BytesIO()
            PublishedMeccPdf(training, pdf).build_doc()
            url = self.save_to_ceph(training, pdf)
            training.published_mecc_url = url
            training.save()
            self.stdout.write('{} - Training {}: saved {} as {} ({})'.format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                training.id,
                filename,
                url,
                training.label))

    def select_trainings_to_publish(self):
        year = currentyear()
        trainings = Training.objects.filter(
            code_year=year.code_year,
            is_used=True,
            date_val_cfvu__isnull=False,
        ).filter(
            Q(published_mecc_url__isnull=True) | Q(published_mecc_url='')
        ).exclude(
            Q(ref_cpa_rof__isnull=True) | Q(ref_cpa_rof='')
        )
        return trainings

    def make_filename(self, training):
        filename = 'eva/{year}/{id}-{ref_rof}.pdf'.format(
            year=training.code_year,
            id=training.id,
            ref_rof=training.ref_cpa_rof
        )
        return filename

    def save_to_ceph(self, training, pdf):
        ceph = Ceph(self.make_filename(training))
        ceph.save(pdf)
        url = ceph.get_url(86400 * 365 * 2)
        return url
