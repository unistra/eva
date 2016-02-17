from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..institute.models import Institute

class MeccUser(models.Model):
        STATUS_CHOICES = (
            ('STU', _('Étudiant')),
            ('ADM', _('Administratif')),
            ('PROF', _('Enseignant')),
        )

        PROFILE_CHOICES = (
            ('ADM', _('Administrateur')),
            ('DES1', _('Direction des études et de la scolarité 1')),
            ('DES2', _('Direction des études et de la scolarité 2')),
            ('ECI', _('Membre de la commission ECI')),
            ('DIRCOMP', _('Directeur de composante')),
            ('RAC', _('Responsable administratif')),
            ('REFSCOL', _('Responsable Formation Scolarité')),
            ('DIRETU', _('Directeur d\'études')),
            ('GESCOL', _('Gestionnaire de scolarité')),
            ('RESPFORM', _('Responsable de formation')),
        )

        user = models.OneToOneField(User, on_delete=models.CASCADE)

# Can be fill with Camelot
        # last_name = models.CharField(_('Nom'), max_length=35)
        # birth_name = models.CharField(_('Nom de naissance'), max_length=35, blank=True)
        # first_name = models.CharField(_('Prénom'), max_length=35, blank=True)
        status = models.CharField(
            _('Statut'), max_length=4, choices=STATUS_CHOICES, blank=True)
        # email = models.EmailField(_('email address'), blank=True)
        cmp = models.ForeignKey(Institute, blank=True, null=True, verbose_name=_('Composante'))
        birth_date = models.DateField(
            _('Date de naissance'), blank=True, null=True)

# To manually add depending on selected input
        profile = models.CharField(
            _("Profil"), max_length=10, choices=PROFILE_CHOICES, blank=False)

        
