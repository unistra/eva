from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import pdf as celery_pdf

__all__ = ['celery_pdf']

# In order to make signals work
default_app_config = 'mecc.apps.utils.apps.AppConfig'

