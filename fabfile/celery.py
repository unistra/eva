# -*- coding: utf-8 -*-

"""
celery
=====

Required functions for Celery

"""

from os.path import dirname, join, sep

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


def celery_service_name():
    return 'celery-%s' % env.root_package_name

def celerybeat_service_name():
    return 'celerybeat-%s' % env.root_package_name

@do_verbose
def install_celery():
    if all([e in env.keys() for e in ('celery_version',)]):
        # Configure the celery file in /etc/init.d
        initd_path = join(sep, 'etc', 'init.d')
        with fabric.api.cd(initd_path):
            fabric.api.sudo(
                'wget -c https://raw.githubusercontent.com/celery/celery/%s/extra/generic-init.d/celeryd -O %s'\
                    % (env.celery_version, celery_service_name())
            )
            fabric.api.sudo(
                'wget -c https://raw.githubusercontent.com/celery/celery/%s/extra/generic-init.d/celerybeat -O %s'\
                    % (env.celery_version, celerybeat_service_name())
            )
            fabric.api.sudo('chmod 755 %s' % celery_service_name())
            fabric.api.sudo('chmod 755 %s' % celerybeat_service_name())
        # Configure the celery file in /etc/default
        celeryd_path = join(sep, 'etc', 'default')
        celeryd_filepath = join(celeryd_path, celery_service_name())

        with fabric.api.cd(celeryd_path):
            fabtools.files.upload_template(
                'celeryd.tpl',
                celeryd_filepath,
                context=env,
                template_dir=join(dirname(__file__), 'templates'),
                use_jinja=True,
                use_sudo=True,
                user='root',
                chown=True,
                mode='644'
            )
    else:
        fabric.api.abort('Please provide parameters for Celery installation !')

@do_verbose
def celery_start():
    """ Starts celery """
    if not celery_started():
        fabtools.service.start(celery_service_name())
    else:
        fabric.api.puts("Celery is already started")

@do_verbose
def celerybeat_start():
    """ Starts celerybeat """
    if not celerybeat_started():
        fabtools.service.start(celerybeat_service_name())
    else:
        fabric.api.puts("Celerybeat is already started")

@do_verbose
def celery_restart():
    """ Starts/Restarts celery """
    if not celery_started():
        fabric.api.execute(celery_start)
    else:
        fabtools.service.restart(celery_service_name())

@do_verbose
def celerybeat_restart():
    """ Starts/Restarts celerybeat """
    if not celerybeat_started():
        fabric.api.execute(celerybeat_start)
    else:
        fabtools.service.restart(celerybeat_service_name())

def celery_started():
    """
    Returns true/false depending on whether the celery service is started or not
    """
    return fabtools.service.is_running(celery_service_name())

def celery_beat_started():
    """
    Returns true/false depending on whether the celerybeat service is started or not
    """
    return fabtools.service.is_running(celerybeat_service_name())

@do_verbose
def deploy_celery_file():
    """ Uploads celery.py template on remote """
    fabtools.files.upload_template(
        'celery.py',
        join(env.remote_base_package_dir, 'celery.py'),
        template_dir=env.local_tmp_root_app_package,
        context=env,
        use_sudo=True,
        user=env.remote_owner,
        chown=True,
        mode='644',
        use_jinja=True
    )
