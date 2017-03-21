import os

from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
# from django.urls import reverse
# from django.utils.html import format_html


class FileUpload(models.Model):
    """ Manage uploads"""
    file = models.FileField(upload_to=settings.FILES_UPLOAD_PATH)
    creator = models.ForeignKey(User, related_name='file_uploads')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    additional_type = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return self.file.name

    def filename(self):
        return os.path.basename(self.file.name)

    # def protected_file(self,):
    #     url = reverse('file_serve', args=[os.path.basename(self.file.file.name)])
    #     return format_html('<a href="'+url+'">File</a>')
    #     protected_file.short_description = 'Upload'
