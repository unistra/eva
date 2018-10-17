[Unit]
Description={{ application_name }} celery beat service
After=network.target systemd-tmpfiles-setup.service

[Service]
Type=forking
User={{ remote_owner }}
Group={{ remote_group }}
EnvironmentFile=-/etc/default/celeryd-{{ application_name }}
WorkingDirectory={{ remote_current_path }}
ExecStart=/bin/sh -c '${CELERY_BIN} beat -A ${CELERY_APP} --pidfile=${CELERYBEAT_PID_FILE} --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} --schedule=${CELERYBEAT_SCHEDULE}'
ExecStop=/bin/kill $MAINPID

[Install]
WantedBy=multi-user.target
