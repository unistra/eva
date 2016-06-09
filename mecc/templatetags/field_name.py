from django import template
import os


register = template.Library()


@register.filter
def filename(value):
    try:
        return os.path.basename(value.file.name)
    except (OSError, ValueError):
        pass
    return None
