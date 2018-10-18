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
from pydiploy.require.system import is_systemd


def celery_service_name():
    return 'celery-%s' % env.root_package_name

def celerybeat_service_name():
    return 'celerybeat-%s' % env.root_package_name

@do_verbose
def install_celery():
    if all([e in env.keys() for e in ('celery_version',)]):
        # Firstly we check if the system uses sytemd
        if is_systemd():
            worker_filename = 'celery-%s' % env.application_name
            beat_filename = 'celerybeat-%s' % env.application_name
            tmpfiles_filename = worker_filename + ".conf"

            # Create celery log folder
            fabtools.require.files.directory(
                path=join(sep, "var", "log", "celery"),
                use_sudo=True,
                owner=env.remote_owner,
                group=env.remote_group,
                mode='775'
            )

            # Create celery run folder
            fabtools.require.files.directory(
                path=join(sep, "var", "run", "celery"),
                use_sudo=True,
                owner=env.remote_owner,
                group=env.remote_group,
                mode='775'
            )

            #Configure the celery worker and beat service file in /etc/systemd/system
            systemd_path = join(sep, "etc", "systemd", "system")
            worker_filepath = join(systemd_path, worker_filename + ".service")
            beat_filepath = join(systemd_path, beat_filename + ".service")

            with fabric.api.cd(systemd_path):
                # Worker service file
                fabtools.files.upload_template(
                    'celery-mecc.service.tpl',
                    worker_filepath,
                    context=env,
                    template_dir=join(dirname(__file__), 'templates'),
                    use_jinja=True,
                    # use_sudo=True,
                    user='root',
                    chown=True,
                    mode='755'
                )
                # Beat service file
                fabtools.files.upload_template(
                    'celerybeat-mecc.service.tpl',
                    beat_filepath,
                    context=env,
                    template_dir=join(dirname(__file__), 'templates'),
                    use_jinja=True,
                    # use_sudo=True,
                    user='root',
                    chown=True,
                    mode='755'
                )

            # Configure the tmpfiles conf file in /etc/tmpfiles.d
            tmpfiles_path = join(sep, "etc", "tmpfiles.d")
            tmpfiles_filepath = join(tmpfiles_path, tmpfiles_filename)

            with fabric.api.cd(tmpfiles_path):
                fabtools.files.upload_template(
                    'celery-mecc.conf.tpl',
                    tmpfiles_filepath,
                    context=env,
                    template_dir=join(dirname(__file__), 'templates'),
                    use_jinja=True,
                    # use_sudo=True,
                    user='root',
                    chown=True,
                    mode='755'
                )
            fabric.api.sudo('systemctl daemon-reload')
        # if the system doesn't use systemd, we assume that it uses initd
        else:
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

        # Configure the celery conf file in /etc/default
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
        if is_systemd():
            fabtools.systemd.start(celery_service_name())
        else:
            fabtools.service.start(celery_service_name())
    else:
        fabric.api.puts("Celery is already started")

@do_verbose
def celerybeat_start():
    """ Starts celerybeat """
    if not celerybeat_started():
        if is_systemd():
            fabtools.systemd.start(celerybeat_service_name)
        else:
            fabtools.service.start(celerybeat_service_name())
    else:
        fabric.api.puts("Celerybeat is already started")

@do_verbose
def celery_restart():
    """ Starts/Restarts celery """
    if not celery_started():
        fabric.api.puts("celery-mecc not started")
        fabric.api.execute(celery_start)
    else:
        fabric.api.puts("celery-mecc started")
        if is_systemd():
            fabtools.systemd.restart(celery_service_name())
        else:
            fabtools.service.restart(celery_service_name())

@do_verbose
def celerybeat_restart():
    """ Starts/Restarts celerybeat """
    if not celerybeat_started():
        fabric.api.execute(celerybeat_start)
    else:
        if is_systemd():
            fabtools.systemd.stop(celerybeat_service_name())
            fabtools.systemd.start(celerybeat_service_name())
        else:
            fabtools.service.restart(celerybeat_service_name())

@do_verbose
def celery_started():
    """
    Returns true/false depending on whether the celery service is started or not
    """
    if is_systemd():
        running = 'active' in fabric.api.sudo('systemctl is-active %s' % celery_service_name())
        return running

    return fabtools.service.is_running(celery_service_name())

@do_verbose
def celerybeat_started():
    """
    Returns true/false depending on whether the celerybeat service is started or not
    """
    if is_systemd():
        running = 'active' in fabric.api.sudo('systemctl is-active %s' % celerybeat_service_name())
        return running

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

@do_verbose
def deploy_celery_file():
    """ Uploads wsgi.py template on remote """
    fabtools.files.upload_template(
        'celery.py',
        join(env.remote_base_package_dir,'celery.py'),
        template_dir=env.local_tmp_root_app_package,
        context=env,
        use_sudo=True,
        user=env.remote_owner,
        chown=True,
        mode='644',
        use_jinja=True
    )
