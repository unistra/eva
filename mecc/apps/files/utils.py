from django.core.files import File
from django.core.urlresolvers import reverse

from .forms import FileUploadForm
from .models import FileUpload


def create_file(up_file, obj, user, additional_type=None, comment=None):
    res = FileUpload(content_object=obj, creator=user,
                     additional_type=additional_type, comment=comment)
    file_ = File(up_file)
    res.file.save(up_file.name, file_, save=False)
    res.save()

    return res


def upload_files(request, obj):
    form = FileUploadForm(request.POST, request.FILES)
    if request.method == 'POST' and form.is_valid():
        files = []
        for name in request.FILES:
            upload_file = request.FILES[name]
            res = create_file(upload_file, obj, request.user,
                              request.POST['additional_type'],
                              request.POST['comment'])
            delete_url = reverse('files:delete_file',
                                 kwargs={'file_id': res.id})
            files.append({'name': upload_file.name, 'url': res.file.url,
                          'delete_url': delete_url})
        return files
    return None


# def file_directory_path(instance, filename):
#    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#    return 'user_{0}/{1}'.format(instance.user.id, filename)
