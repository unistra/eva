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
        elif subcommand == 'unpublish':
            self.unpublish()

    def publish(self):
        trainings = self.select_trainings_to_publish()
        for training in trainings:
            filename = self.make_filename(training)
            pdf = BytesIO()
            PublishedMeccPdf(training, pdf).build_doc()
            url = self.save_to_ceph(training, pdf)
            training.published_mecc_url = url
            training.save(update_fields=['published_mecc_url'])
            self.stdout.write('{ts} - Training {id} ({label})\n\tsaved {filename} as {url}'.format(
                ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                id=training.id,
                label=training.label,
                filename=filename,
                url=url
            ))

    def unpublish(self):
        trainings = self.select_trainings_to_unpublish()
        for training in trainings:
            filename = self.make_filename(training)
            self.delete_from_ceph(training)
            training.published_mecc_url = None
            training.save(update_fields=['published_mecc_url'])
            self.stdout.write('{ts} - Training {id} ({label})\n\t{filename} removed'.format(
                ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                id=training.id,
                label=training.label,
                filename=filename
            ))

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

    def select_trainings_to_unpublish(self):
        year = currentyear()
        trainings = Training.objects.filter(
            code_year=year.code_year,
            is_used=True,
            date_val_cfvu__isnull=True,
            published_mecc_url__isnull=False,
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

    def delete_from_ceph(self, training):
        ceph = Ceph(self.make_filename(training))
        ceph.delete()
