import json
import mimetypes
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps

from django.core.servers.basehttp import FileWrapper
from django.http import (HttpResponse, HttpResponseNotFound,
                         HttpResponseBadRequest, StreamingHttpResponse)
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from django_cas.decorators import login_required

from .models import FileUpload
from .utils import upload_files


@login_required
@require_http_methods(["POST"])
def upload_file(request, app_name, model_name, object_pk):
    """Upload a file"""
    try:
        m = apps.get_model(app_name, model_name)

    except LookupError:
        message = _('Model does not exist.')
        return HttpResponseBadRequest(
            json.dumps({'status': 'error', 'message': message}))

    # Then look up the object by pk
    try:
        obj = m.objects.get(pk=object_pk)
    except ObjectDoesNotExist:
        message = _('Object does not exist.')
        return HttpResponseNotFound(
            json.dumps({'status': 'error', 'message': message}))

    files = upload_files(request, obj)
    if files is not None:
        return HttpResponse(
            json.dumps({'status': 'success', 'files': files}))

    message = _('Invalid or no file received.')
    return HttpResponseBadRequest(
        json.dumps({'status': 'error', 'message': message}))


@login_required
@require_http_methods(["POST"])
def delete_file(request, file_id):
    """Delete a file given its object id. TODO:permissions to delete files """
    try:
        res = FileUpload.objects.get(pk=file_id)
    except FileUpload.DoesNotExist:
        message = _('The requested file could not be found.')
        return HttpResponseNotFound(
            json.dumps({'status': 'error', 'message': message}))
    res.file.delete()
    res.delete()

    return HttpResponse(json.dumps({'status': 'success'}))


@login_required
def serve_file(request, path, document_root=None, show_indexes=False):
    """Serve static files """
    try:
        _file = os.path.join(settings.MEDIA_ROOT, path)
        _file_type = mimetypes.guess_type(_file)[0]

        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(_file, 'rb'),
                                                     chunk_size),
                                         content_type=_file_type)
        response['Content-Length'] = os.path.getsize(_file)

    except:
        return HttpResponseNotFound()

    return response
