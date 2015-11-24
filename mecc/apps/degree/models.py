# from django.db import models
# from django.utils.translation import ugettext_lazy as _
# from mecc.apps.institute.models import Institute
#
#
# class Degree(models.Model):
#     """
#     Degree model
#     """
#     degree_type = models.ForeignKey('DegreeType')
#     label_type = models.CharField(_('Label type'), max_length=25)
#     mention = models.CharField(_('Mention'), max_length=25)
#     speciality = models.CharField(_('Speciality'), max_length=25)
#     course = models.CharField(_('Course'), max_length=25)
#     title = models.CharField(_('Title')),
#     in_use = models.BooleanField(_('In use'))
#     start = models.IntegerField(_('Start'))
#     end = models.IntegerField(_('End'))
#     ref_formation = models.CharField(_('REF SI Formation'), max_length=25)
#     ref_scol = models.CharField(_('REF SI Scol'), max_length=25)
#     # institutes = models.ManyToManyField(Institute)
#
#     def __str__(self):
#         return '%s %s' % (self.label_type, self.mention)
#
#     class Meta:
#         ordering = ['label_type', 'mention']
#         permissions = (('can_view_degree', 'Can view degree'),)
#
#
# class DegreeType(models.Model):
#     """
#     Degree Type model
#     """
#     display_order = models.IntegerField(_('Display order'))
#     short_label = models.CharField(_('Short label'), max_length=25)
#     long_label = models.CharField(_('Long label', max_length=25))
#     in_use = models.BooleanField(_('In use'))
#     mecc_category = models.CharField(_('MECC Category'), max_length=25)
#
#     def __str__(self):
#         return self.short_label
#
#     class Meta:
#         ordering = ['display_order']
#         permissions = (('can_view_degree_type', _('Can view degree type')),)
