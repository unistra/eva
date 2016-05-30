from django import template
import os


register = template.Library()


@register.simple_tag
def get_field_name(instance, field_name):
    """
    Returns field name.
    """
    return instance._meta.get_field(field_name).verbose_name.title()


@register.filter
def filename(value):
    try:
        return os.path.basename(value.file.name)
    except (OSError, ValueError):
        pass
    return None
