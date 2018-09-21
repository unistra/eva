import tempfile
from io import BytesIO

import boto3
from django.conf import settings


class Ceph:
    """"
    Simple interface to store files in Ceph, generate a public URL for it
    and delete it
    """

    def __init__(self, filename):
        self.ceph = boto3.client(
            's3',
            aws_access_key_id=settings.CEPH_STORAGE_KEY_ID,
            aws_secret_access_key=settings.CEPH_STORAGE_SECRET_KEY,
            endpoint_url=settings.CEPH_STORAGE_ENDPOINT_URL
        )
        self.bucket = settings.CEPH_STORAGE_BUCKET
        self.filename = filename

    def save(self, data):
        if not isinstance(data, BytesIO):
            raise TypeError('binary_data must be an instance of io.BytesIO')
        file = self.get_pdf_as_file(data)
        self.ceph.upload_file(file.name, self.bucket, self.filename)

    def get_url(self, seconds_before_expires):
        if not isinstance(seconds_before_expires, int):
            raise ValueError('seconds_before_expires must be an integer value')
        url = self.ceph.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': self.filename,
            },
            ExpiresIn=seconds_before_expires)
        return url

    def get_file(self):
        data = BytesIO()
        self.ceph.download_fileobj(self.bucket, self.filename, data)
        return data

    def delete(self):
        self.ceph.delete_object(Bucket=self.bucket, Key=self.filename)

    def get_pdf_as_file(self, data):
        tf = tempfile.NamedTemporaryFile(mode='wb')
        tf.write(data.getvalue())
        return tf
