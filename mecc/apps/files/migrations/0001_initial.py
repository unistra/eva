# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('file', models.FileField(upload_to='uploads/docs/%Y')),
                ('object_id', models.PositiveIntegerField()),
                ('additional_type', models.CharField(max_length=255, blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True, default='')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('creator', models.ForeignKey(related_name='file_uploads', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
