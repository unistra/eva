import logging
import os
import shutil

from django.conf import settings
from django_celery_results.models import TaskResult
from celery import shared_task
from celery.signals import task_prerun, task_postrun, task_success, task_failure

from mecc.apps.utils.documents_generator import Document

################################################################################
################################### MODEL A ####################################
################################################################################

logger = logging.getLogger(__name__)

@shared_task(bind=True) # utile pour les "reusable apps"
def task_generate_pdf_model_a(
        self,
        user,
        trainings,
        reference,
        standard,
        target,
        date):
    """ generate pdf model A files """

    task_result, created = TaskResult.objects.get_or_create(task_id=self.request.id)

    filename = Document.generate(
        gen_type='pdf',
        model='a',
        user=user,
        trainings=trainings,
        reference=reference,
        standard=standard,
        target=target,
        date=date,
        year=None,
        task_id=task_result.id
    )

    return '%s - %s.pdf' % (task_result.id, filename)

@task_prerun.connect(sender=task_generate_pdf_model_a)
def start_task_generate_pdf_model_a(sender=None, *args, **kwargs):
    logger.info("Starting : {sender}".format(sender=sender))
    tmp_dir_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(tmp_dir_path, exist_ok=True)

@task_success.connect(sender=task_generate_pdf_model_a)
def success_task_generate_pdf_model_a(sender=None, *args, **kwargs):
    logger.info("Success : {sender}".format(sender=sender))

@task_postrun.connect(sender=task_generate_pdf_model_a)
def stop_task_generate_pdf_model_a(sender=None, *args, **kwargs):
    logger.info("Stopping : {sender}".format(sender=sender))

@task_failure.connect(sender=task_generate_pdf_model_a)
def failure_task_generate_pdf_model_a(sender=None, *args, **kwargs):
    logger.info("Fail : {sender}".format(sender=sender))

################################################################################
################################### MODEL B ####################################
################################################################################

@shared_task(bind=True) # utile pour les "reusable apps"
def task_generate_pdf_model_b(
        self,
        user,
        trainings,
        reference,
        standard,
        target,
        date):
    """ generate pdf model B files """

    task_result, created = TaskResult.objects.get_or_create(task_id=self.request.id)

    filename = Document.generate(
        gen_type='pdf',
        model='b',
        user=user,
        trainings=trainings,
        reference=reference,
        standard=standard,
        target=target,
        date=date,
        year=None,
        task_id=task_result.id
    )

    return '%s - %s.pdf' % (task_result.id, filename)

@task_prerun.connect(sender=task_generate_pdf_model_b)
def start_task_generate_pdf_model_b(sender=None, *args, **kwargs):
    logger.info("Starting : {sender}".format(sender=sender))
    tmp_dir_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(tmp_dir_path, exist_ok=True)

@task_success.connect(sender=task_generate_pdf_model_b)
def success_task_generate_pdf_model_b(sender=None, *args, **kwargs):
    logger.info("Success : {sender}".format(sender=sender))

@task_postrun.connect(sender=task_generate_pdf_model_b)
def stop_task_generate_pdf_model_b(sender=None, *args, **kwargs):
    logger.info("Stopping : {sender}".format(sender=sender))

@task_failure.connect(sender=task_generate_pdf_model_b)
def failure_task_generate_pdf_model_b(sender=None, *args, **kwargs):
    logger.info("Fail : {sender}".format(sender=sender))

################################################################################
################################### MODEL C ####################################
################################################################################

@shared_task(bind=True) # utile pour les "reusable apps"
def task_generate_pdf_model_c(self, user, trainings, date):
    """ generate pdf model C files """

    task_result, created = TaskResult.objects.get_or_create(task_id=self.request.id)

    filename = Document.generate(
        gen_type='pdf',
        model='a',
        user=user,
        trainings=trainings,
        reference='without',
        standard='yes',
        target='review_eci',
        date=date,
        year=None,
        task_id=task_result.id
    )

    return '%s - %s.pdf' % (task_result.id, filename)

@task_prerun.connect(sender=task_generate_pdf_model_c)
def start_task_generate_pdf_model_c(sender=None, *args, **kwargs):
    logger.info("Starting : {sender}".format(sender=sender))
    tmp_dir_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(tmp_dir_path, exist_ok=True)

@task_success.connect(sender=task_generate_pdf_model_c)
def success_task_generate_pdf_model_c(sender=None, *args, **kwargs):
    logger.info("Success : {sender}".format(sender=sender))

@task_postrun.connect(sender=task_generate_pdf_model_c)
def stop_task_generate_pdf_model_c(sender=None, *args, **kwargs):
    logger.info("Stopping : {sender}".format(sender=sender))

@task_failure.connect(sender=task_generate_pdf_model_c)
def failure_task_generate_pdf_model_c(sender=None, *args, **kwargs):
    logger.info("Fail : {sender}".format(sender=sender))

################################################################################
################################### MODEL D ####################################
################################################################################

@shared_task(bind=True) # utile pour les "reusable apps"
def task_generate_pdf_model_d(self, user, trainings, target, date, year):
    """ generate pdf model D files """

    task_result, created = TaskResult.objects.get_or_create(task_id=self.request.id)

    filename = Document.generate(
        gen_type='pdf',
        model='a',
        user=user,
        trainings=trainings,
        reference='both',
        standard='yes',
        target=target,
        date=date,
        year=year,
        task_id=task_result.id
    )

    return '%s - %s.pdf' % (task_result.id, filename)

@task_prerun.connect(sender=task_generate_pdf_model_d)
def start_task_generate_pdf_model_d(sender=None, *args, **kwargs):
    logger.info("Starting : {sender}".format(sender=sender))
    tmp_dir_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(tmp_dir_path, exist_ok=True)

@task_success.connect(sender=task_generate_pdf_model_d)
def success_task_generate_pdf_model_d(sender=None, *args, **kwargs):
    logger.info("Success : {sender}".format(sender=sender))

@task_postrun.connect(sender=task_generate_pdf_model_d)
def stop_task_generate_pdf_model_d(sender=None, *args, **kwargs):
    logger.info("Stopping : {sender}".format(sender=sender))

@task_failure.connect(sender=task_generate_pdf_model_d)
def failure_task_generate_pdf_model_d(sender=None, *args, **kwargs):
    logger.info("Fail : {sender}".format(sender=sender))

################################################################################
############################ TMP DIRECTORY CLEANER #############################
################################################################################

@shared_task(bind=True, ignore_result=True)
def task_clean_tmp_directory(self):
    """
    Remove generated pdfs in the /media/tmp directory on a daily basis
    The task deletes the tmp directory and recreates it
    """
    tmp_dir_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    shutil.rmtree(
        path=tmp_dir_path,
        ignore_errors=True
    )
    os.makedirs(tmp_dir_path, exist_ok=True)


@task_prerun.connect(sender=task_clean_tmp_directory)
def start_task_clean_tmp_directory(sender=None, *args, **kwargs):
    logger.info("Starting : {sender}".format(sender=sender))

@task_success.connect(sender=task_clean_tmp_directory)
def success_task_clean_tmp_directory(sender=None, *args, **kwargs):
    logger.info("Success : {sender}".format(sender=sender))

@task_postrun.connect(sender=task_clean_tmp_directory)
def stop_task_tmp_directory(sender=None, *args, **kwargs):
    logger.info("Stopping : {sender}".format(sender=sender))

@task_failure.connect(sender=task_clean_tmp_directory)
def failure_task_clean_tmp_directory(sender=None, *args, **kwargs):
    logger.info("Fail : {sender}".format(sender=sender))
