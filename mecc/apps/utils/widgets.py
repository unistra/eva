from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext as _


class CustomFileInput(ClearableFileInput):
    template_with_initial = (
        '<a href="%(initial_url)s">%(initial)s</a> </br>'
        '%(clear_template)s<br/>'
    )

    def render(self, name, value, attrs=None):

        substitutions = {
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(
            name, value, attrs)
        if self.is_initial(value):
            template = self.template_with_initial
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                substitutions['clear_template'] = self.template_with_clear % \
                    substitutions
        else:
            template = (
                '%(input)s</br> '
                '%(add_pdf)s'
            )
            substitutions['add_pdf'] = '<button type="submit" id="add_pdf" class="pull-right btn btn-primary btn-xs" \
            name="add_pdf">%s</button></br>' % _('Ajouter le document')
        return (template % substitutions)

    template_with_clear = (
        '<a id="delete_pdf" class="pull-right btn btn-danger btn-xs" \
        onclick="return delete_pdf(event)">%s</a>' % _('Supprimer le document')

    )
