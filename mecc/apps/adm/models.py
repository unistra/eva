from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class MeccUser(models.Model):
        STATUS_CHOICES = (
            ('STU', _('Étudiant')),
            ('ADM', _('Administratif')),
            ('PROF', _('Enseignant')),
        )

        PROFILE_CHOICES = (
            ('ECI', _('Membre de la commission ECI')),
            ('DIRCOMP', _('Directeur de composante')),
            ('RAC', _('Responsable administratif')),
            ('REFSCOL', _('Responsable Formation Scolarité')),
            ('DIRETU', _('Directeur d\'études')),
            ('GESCOL', _('Gestionnaire de scolarité')),
            ('RESPFORM', _('Responsable de formation')),
        )

        user = models.OneToOneField(User, on_delete=models.CASCADE)

        cmp = models.CharField(_('Composante'), max_length=5, blank=True)
        status = models.CharField(
            _('Statut'), max_length=4, choices=STATUS_CHOICES, blank=True)

        profile = models.CharField(
            _("Profil"), max_length=10, choices=PROFILE_CHOICES, blank=True)


class ScolManager(MeccUser):
    is_ref_app = models.BooleanField(_("Référent application"))
