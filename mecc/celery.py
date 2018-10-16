from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mecc.settings.{{ goal }}')

from django.conf import settings

pdf = Celery(
    settings.CELERY_NAME,
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_RESULT_BACKEND
)

pdf.config_from_object('django.conf:settings')
pdf.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

pdf_exchange = Exchange('pdf', type='topic', durable=False, delivery_mode=1)
clean_exchange = Exchange('clean_tmp_dir', type='topic', durable=False, delivery_mode=1)

pdf.conf.task_queues = (
    Queue('model_a', pdf_exchange, routing_key='pdf.model_a'),
    Queue('model_b', pdf_exchange, routing_key='pdf.model_b'),
    Queue('model_c', pdf_exchange, routing_key='pdf.model_c'),
    Queue('model_d', pdf_exchange, routing_key='pdf.model_d'),
    Queue('clean_tmp_dir', clean_exchange, routing_key='clean.tmp_dir')
)

pdf.conf.task_default_queue = 'model_a'
pdf.conf.task_default_exchange = 'pdf'
pdf.conf.task_default_routing_key = 'pdf.model_a'

pdf.conf.task_routes = [
    {
        'mecc.apps.doc_gen.tasks.task_generate_pdf_model_a': {
            'queue': 'model_a',
            'routing_key': 'pdf.model_a',
        },
        'mecc.apps.doc_gen.tasks.task_generate_pdf_model_b': {
            'queue': 'model_b',
            'routing_key': 'pdf.model_b',
        },
        'mecc.apps.doc_gen.tasks.task_generate_pdf_model_c': {
            'queue': 'model_c',
            'routing_key': 'pdf.model_c',
        },
        'mecc.apps.doc_gen.tasks.task_generate_pdf_model_d': {
            'queue': 'model_d',
            'routing_key': 'pdf.model_d',
        },
    },

]

pdf.conf.beat_schedule = {
    'task_clean_tmp_directory': {
        'task': 'mecc.apps.doc_gen.tasks.task_clean_tmp_directory',
        'schedule': crontab(hour=3),
        'options': {
            'queue': 'clean_tmp_dir',
            'routing_key': 'clean.tmp_dir',
        }
    }
}
