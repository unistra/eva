from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from mecc.apps.utils.querries import rules_degree_for_year, rules_since_ever
from mecc.apps.institute.models import Institute
from mecc.apps.utils.querries import currentyear


class DegreeType(models.Model):
    """
    Degree Type model
    """
    display_order = models.IntegerField(
        _('Numéro ordre affichage'), unique=False)
    is_in_use = models.BooleanField(_('En service'))
    short_label = models.CharField(_('Libellé court'), max_length=40)
    long_label = models.CharField(_('Libellé long'), max_length=70)
    ROF_code = models.CharField(
        _('Correspondance ROF'), max_length=2, blank=True, null=True)

    def __str__(self):
        return self.short_label

    class Meta:
        ordering = ['display_order', 'short_label']
        permissions = (
            ('can_view_degree_type',
             _('Peut voir les types de diplôme')),
        )

    def get_absolute_url(self):
        return reverse('degree:type')

    def clean_fields(self, exclude=None):
        if self.display_order is None or self.display_order < 0:
            raise ValidationError({'display_order': [
                _('L\'ordre d\'affichage doit être positif.'),
            ]})
        if not self.is_in_use:
            c = currentyear()
            rules = rules_degree_for_year(
                self.pk, c.code_year) if self.pk is not None else None
            if rules is None:
                return
            else:
                raise ValidationError(_('La mise hors service ne peut s\'effectuer \
                    que si aucune règle n\'y est rattachée pour l\'année \
                    universitaire \n %s' % [e.label for e in rules]))

    def delete(self):
        rules = rules_since_ever(self.pk) if self.pk is not None else None
        if rules is None:
            super(DegreeType, self).delete()
        else:
            raise ValidationError(_("Vous ne pouvez pas supprimer un type \
                de diplôme qui contient des règles"))


class Degree(models.Model):
    """
    Degree model
    """
    label = models.TextField(_("Libellé réglementaire"))
    degree_type = models.ForeignKey(
        DegreeType, verbose_name=_("Type de diplôme"))
    degree_type_label = models.CharField(
        _('Libellé du type de diplôme'), max_length=120)
    is_used = models.BooleanField(_('En service'), default=True)
    start_year = models.IntegerField(_('Code année de début de validité'))
    end_year = models.IntegerField(_('Code année de fin de validité'))
    ROF_code = models.CharField(_("Référence Programme ROF"), max_length=20)
    APOGEE_code = models.CharField(
        _("Référence dans le SI Scolarité (APOGEE)"), max_length=40)
    institutes = models.ManyToManyField(Institute)

    @property
    def get_id_type(self):
        return self.degree_type.id

    @property
    def get_short_label_type(self):
        return self.degree_type.short_label

    class Meta:
        ordering = ['degree_type_label', 'label']
