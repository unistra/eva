from django.db import models
from django.utils.translation import ugettext as _


class Travail(models.Model):
    """
    Model in order to create table to make ROF synchro
    """
    trav_annee_eva = models.IntegerField(
        _('EVA année'), blank=True, null=True),
    trav_idform_eva = models.IntegerField(
        _('EVA ID Form'), blank=True, null=True),
    trav_cmpform_eva = models.CharField(
        _('Composante'), max_length=256, blank=True),
    trav_regime_eva = models.CharField(
        _('Composante'), max_length=256, blank=True),
    trav_sessions_eva = models.CharField(
        _('Composante'), max_length=256, blank=True),
    trav_prog_rof = models.CharField(
        _('Composante'), max_length=256, blank=True),
    trav_pere_rof = models.CharField(
        _('Composante'), max_length=256, blank=True),
    trav_fils_rof = models.CharField(
        _('Composante'), max_length=256, blank=True),
    trav_ordre_rof = models.IntegerField(_('ROF ordre'), blank=True, null=True)
