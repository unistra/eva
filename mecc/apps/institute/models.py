# from django.db import models
# from django.utils.translation import ugettext_lazy as _
#
#
# class Person(models.Model):
#     """"
#     Person model used as parent and directly as Institute Director & \
#     Administrative Manager
#     """
#     id_person = models.CharField(_('ID'))
#     name = models.CharField(_('Name'))
#     firstname = models.CharField(_('Firstname'))
#
#     def __str__(self):
#         return '%s %s' % (self.name, self.firstname)
#
#
# class TuitonManager(Person):  # ## Gestionnaire de scolarité
#     """
#     Tuition Manager model
#     """
#     is_registrar = models.BooleanField(_('Is registrar'))
#
#
# class Yearly(models.Model):
#     """
#     Yearly model, contains code institute and the needed
#     staff for a specific year
#     """
#     code_institute = models.CharField(_('Code Institute'), max_length=5)
#
#     code_year = models.IntegerField(_('Code year'),)
#     label_year = models.CharField(_('Label year'), max_length=15)
#     current_year = models.BooleanField(_('Current year'), default=False)
#     initialisation_done = models.BooleanField(_('Initalisation done'), default=False)
#     pdf_uploaded = models.BooleanField(_('Pdf uploaded'))  # ## May be deleted
#     date_CFVU_framework = models.DateField(_('Date CFVU framework'))
#     date_CFVU_estimated = models.DateField(_('Estimated CFVU date'))
#     date_last_notification = models.DateField(_('Last notification date'))
#     institute_director = models.ForeignKey(Person)  # ## Dir de composante
#     administrative_manager = models.ForeignKey(Person)  # ## Responsable admin
#
#     studies_director = models.ManyToManyField(Person)  # ## Directeur(s) d'étude
#     tuition_manager = models.ManyToManyField(TuitonManager)  # ## Gestionnaire(s) de scolarité
#
#     class Meta:
#         unique_together = (('code_institute', 'code_year'),)  # ## Django cannot handle multi primary key so we'll use unique_together
#
#
# class Institute(models.Model):
#     """
#     Institute model
#     """
#
#     code = models.CharField(_('Code'), max_length=4)
#     label = models.CharField(_('Label'), max_length=25)
#     in_use = models.BooleanField(_('In use'))
#     field = models.CharField(_('Field'), max_length=25)
#     years = models.ManyToManyField(Yearly)
