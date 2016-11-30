from django import template

from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter
def redify(value,redvalue):
    return '<span class="red">%s</span>' % value if value == _(redvalue) else value
