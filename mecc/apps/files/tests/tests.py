from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from mecc.apps.files.models import FileUpload
from mecc.apps.files import utils
from mecc.apps.institute.models import AcademicField, Institute

import os
import shutil


class FileUploadTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="test")
        self.client.login(username='test', password='test')
        self.academicField = AcademicField.objects.create(name='test_academic_field')
        self.obj = Institute.objects.create(code='1', label='test_institute', field=self.academicField)
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

    def test_views(self):
        # test get not allowed
        response = self.client.get(reverse('files:upload_file', kwargs={'app_name': 'test', 'model_name' : 'Test', 'object_pk': 1, }))
        self.assertEqual(response.status_code, 405)
        upload_file = SimpleUploadedFile('test.txt', 'test'.encode('utf-8'), content_type='text/plain')
        #upload_file = SimpleUploadedFile(self.fileFullPath, "file_content", content_type="application/pdf")
        response = self.client.post(reverse("files:upload_file", { 'file': upload_file}, kwargs={'app_name': 'institute', 'model_name' : 'Institute', 'object_pk': self.obj.pk}))
        self.assertEqual(response.status_code, 405)
