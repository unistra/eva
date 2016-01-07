from django.db import models
from django.utils.translation import ugettext_lazy as _


class ECICommissionMember(models.Model):
    """
    ECI Commission Member model
    """
    member_type_choice = (
        ('commission', _('Commission ECI')), ('tenured', _('Etudiant CFVU titulaire')),
        ('supply', _('Etudiant CFVU suppléant')),
    )
    id_member = models.CharField(_('ID Membre'), max_length=35, unique=True)
    name = models.CharField(_('Nom'), max_length=35)
    firstname = models.CharField(_('Prénom'), max_length=35)
    member_type = models.CharField(_('Type'), blank=False,
                                   choices=member_type_choice, max_length=20)
    mail = models.CharField(_('Mail'), max_length=256)

    def __str__(self):
        return '%s %s' % (self.name, self.firstname)

    class Meta:
        permissions = (
            ('can_view_eci_commission_member', _('Peut voir les membres de la commission ECI')),
        )
