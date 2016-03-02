from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _


class Profile(models.Model):
    code = models.CharField(_('Code du profil'), max_length=10)
    label = models.CharField(_('Libellé du profil'), max_length=30)

    def __str__(self):
        return self.label

    class Meta:
        permissions = (
            ('DES1', _('Donne accès à un large pannel de fonctionnalité')),
            ('DES2', _('Donne accès à un pannel restreint')),
            ('DES3', _('Peut usurper l\'identité des utilisateurs')),
        )


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

        profile = models.ManyToManyField(Profile)

        def __str__(self):
            return self.user.username


class ScolManager(MeccUser):
    is_ref_app = models.BooleanField(_("Référent application"))
