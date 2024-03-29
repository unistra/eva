from django import template
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from mecc.apps.mecctable.models import Exam

register = template.Library()


@register.filter
def redify(value, redvalue):
    return '<span class="red">%s</span>' % value if value == _(redvalue) else value


@register.filter
def redorgreenify(value, redvalue):
    color = "green" if value == _(redvalue) else "red"
    return '<span class="%s">%s</span>' % (color, value)


@register.assignment_tag
def get_bootstrap_alert_msg_css_name(tags):
    # in bootstrap the class danger is for error !!!
    return 'danger' if tags == 'error' else tags


@register.assignment_tag
def settings_get(name):
    try:
        return str(settings.__getattr__(name))
    except:
        return ""

@register.filter(name="has_exams")
def has_exams(structure_id):
    return True if structure_id in [exam.id_attached for exam in Exam.objects.all()] else False
