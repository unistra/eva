from django import template
import os
from mecc.apps.files.models import FileUpload


register = template.Library()


@register.filter
def filename(value):
    try:
        return os.path.basename(value.file.name)
    except (OSError, ValueError, AttributeError):
        pass
    return None
