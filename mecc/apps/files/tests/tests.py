from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.test import TestCase
from mecc.apps.files.models import FileUpload
from mecc.apps.institute.models import AcademicField, Institute

import os
import shutil


class FileUploadTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")
        self.obj = Institute(code='1', label='test_institute', field=AcademicField(name='test_academic_field'))
        self.ct = ContentType.objects.get_for_model(self.obj)
        self.fileFullPath = 'mecc/apps/files/tests/media/testpdf.pdf'
        self.media_path = "/tmp/mecc_unittests"

    def tearDown(self):
        if os.path.exists(self.media_path):
            shutil.rmtree(self.media_path)

    def test_fileupload_upload(self):
        upload = FileUpload(content_object=self.obj, creator=self.user)
        with open(self.fileFullPath, 'rb') as f:
            up_file = File(f)
            upload.file.save(up_file.name, up_file, save=False)
        self.assertEqual('testpdf.pdf', os.path.basename(upload.file.name))
        self.assertEqual('testpdf.pdf', upload.filename())
        self.assertEqual(str(upload), upload.file.name)
