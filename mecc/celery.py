from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mecc.settingsi{{ goal  }}')

from django.conf import settings

app = Celery(
    settings.CELERY_NAME,
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_RESULT_BACKEND
)

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

pdf_exchange = Exchange('pdf', type='topic', durable=False, delivery_mode=1)

app.conf.task_queues = (
    Queue('model_a', pdf_exchange, routing_key='pdf.model_a'),
    Queue('model_b', pdf_exchange, routing_key='pdf.model_b'),
    Queue('model_c', pdf_exchange, routing_key='pdf.model_c'),
    Queue('model_d', pdf_exchange, routing_key='pdf.model_d'),
)

app.conf.task_default_queue = 'model_a'
app.conf.task_default_exchange = 'pdf'
app.conf.task_default_routing_key = 'pdf.model_a'

app.conf.task_routes = [
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
