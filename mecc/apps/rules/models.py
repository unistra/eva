from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from mecc.apps.years.models import UniversityYear


class Rule(models.Model):
    """
    Rule model
    """
    EDITED_CHOICES = (
        ('O', _('Oui')),
        ('N', _('Non')),
        ('X', _('Nouvelle')),
    )
    display_order = models.IntegerField(
        _('Numéro ordre affichage'), unique=False, default=0)
    code_year = models.IntegerField(_("Code année"))
    label = models.CharField(_("Libellé"), max_length=75)
    is_in_use = models.BooleanField(_('En service'), default=True)
    is_edited = models.CharField(_('Modifiée'), max_length=4,
                                 choices=EDITED_CHOICES, default='X')
    is_eci = models.BooleanField(_('ECI'), default=False)
    is_ccct = models.BooleanField(_('CC/CT'), default=False)
    degree_type = models.ManyToManyField('degree.DegreeType')
    n_rule = models.IntegerField(_('Numéro de règle'), unique=False)

    @property
    def is_empty(self):
        """
        Return true if the rule contains any paragraph
        """
        return True if len(Paragraph.objects.filter(rule=self)) is 0 else False

    @property
    def has_parag_with_derog(self):
        """
        Return true if there is at least one derogation in paragraphs concerned
        by the rule
        """
        return True if True in [e.is_interaction for e in Paragraph.objects.filter(
            rule=self)] else False

    @property
    def has_current_exceptions(self):
        """
        Return two values :
            - bool if there is additionals and/or derogations
            - list of additionals and derogations
        """
        # get_model in order to avoid cyclic import
        additional_paragraph = apps.get_model('training', 'AdditionalParagraph')
        additionals = [e for e in additional_paragraph.objects.filter(
            code_year=self.code_year,
            rule_gen_id=self.n_rule)]
        specific_paragraph = apps.get_model('training', 'SpecificParagraph')
        s_p = [e for e in specific_paragraph.objects.filter(
            code_year=self.code_year,
            rule_gen_id=self.n_rule)]
        give = {
            'additionals': additionals,
            'specifics': s_p}
        return True if len(s_p + additionals) > 0 else False, give

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        """
        Return absolute url
        """
        return reverse('rules:list')

    def clean_fields(self, exclude=None):
        self.code_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0).code_year
        if self.display_order < 0:
            raise ValidationError({'display_order': [
                _('L\'ordre d\'affichage doit être positif.'),
            ]})
        if self.n_rule in ['', ' ', 0, None]:
            try:
                self.n_rule = Rule.objects.all().latest('id').id + 1
            except ObjectDoesNotExist:
                self.n_rule = 1

    class Meta:
        ordering = ['display_order']
        unique_together = (("n_rule", "code_year"),)


class Paragraph(models.Model):
    """
    Paragraph model
    """
    code_year = models.IntegerField(_("Code année"), unique=False)
    rule = models.ManyToManyField(Rule)
    text_standard = models.TextField(_("Texte de l'alinéa standard"))
    is_in_use = models.BooleanField(_('En service'), default=True)
    display_order = models.IntegerField(
        _('Numéro ordre affichage'), unique=False)
    # is_cmp = models.BooleanField(_('Alinéa de composante'))
    is_interaction = models.BooleanField(_('Dérogation'))
    text_derog = models.TextField(_("Texte de consigne pour la saisie de \
        l'alinéa dérogatoire"), blank=True)
    text_motiv = models.TextField(_("Texte de consigne pour la saisie des \
        motivations"), blank=True)

    def __str__(self):
        return "Alinéa n° %s" % self.pk

    @property
    def specific_involved(self):
        SpecificParagraph = apps.get_model('training', 'SpecificParagraph')
        return SpecificParagraph.objects.filter(
            paragraph_gen_id=self.id, code_year=self.code_year)

    def get_absolute_url(self):
        return reverse('rules:rule_edit', id=Rule.object.all()[0].id)

    class Meta:
        ordering = ['display_order']
