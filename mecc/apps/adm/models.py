from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from django.utils.translation import ugettext as _


class Profile(models.Model):
    """
    Model for profile with year and cmp
    """
    code = models.CharField(_('Code du profil'), max_length=10)
    label = models.CharField(_('Libellé du profil'), max_length=100)
    year = models.IntegerField(_('Année'), blank=True, null=True)
    cmp = models.CharField(_('Composante'), max_length=3)

    def __str__(self):
        return self.label

    @property
    def give_user_id(self):
        return [e.id for e in MeccUser.objects.filter(Q(profile=self))]

    class Meta:
        permissions = (
            ('DES1', _('Donne accès à un large panel de fonctionnalité')),
            ('DES2', _('Donne accès à un panel restreint')),
            ('DES3', _('Peut usurper l\'identité des utilisateurs')),
        )


class MeccUser(models.Model):
    """
    Model for custom user
    """
    STATUS_CHOICES = (
        ('STU', _('Étudiant')),
        ('ADM', _('Administratif')),
        ('PROF', _('Enseignant')),
    )
    django_user = get_user_model()
    user = models.OneToOneField(django_user, on_delete=models.CASCADE, related_name="mecc")
    cmp = models.CharField(_('Composante'), max_length=5, blank=True)
    status = models.CharField(
        _('Statut'), max_length=4, choices=STATUS_CHOICES, blank=True)
    profile = models.ManyToManyField(Profile)
    is_ref_app = models.BooleanField(_("Référent application"), default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _('Utilisateur')
