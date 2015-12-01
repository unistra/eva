from django.db import models
from django.utils.translation import ugettext_lazy as _


class ECICommissionMember(models.Model):
    """
    ECI Commission model
    """
    member_type_choice = (
        ('commission', _('ECI Commission')), ('tenured', _('Tenured Student')),
        ('supply', _('Supply Student')),
    )
    id_member = models.CharField(_('Member ID'), max_length=35)
    name = models.CharField(_('Name'), max_length=35)
    firstname = models.CharField(_('First name'), max_length=35)
    member_type = models.CharField(_('Member type'), blank=False,
                                   choices=member_type_choice, max_length=20)

    def __str__(self):
        return '%s %s' % (self.name, self.firstname)

    class Meta:
        permissions = (
            ('can_view_eci_commission', _('Can view ECI Commission')),
        )


class Mail(models.Model):
    """
    Mail model
    """
    adress = models.EmailField(max_length=254)
    member = models.ForeignKey(ECICommissionMember)

    def __str__(self):
        return adress
