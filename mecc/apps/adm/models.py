from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib import auth


class MeccUserManager(BaseUserManager):

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class MeccUser(AbstractBaseUser):
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

        is_active = models.BooleanField(
            _('active'),
            default=True,
            help_text=_(
                'Designates whether this user should be treated as active. '
                'Unselect this instead of deleting accounts.'
            ),
        )
        is_staff = models.BooleanField(
            _('staff status'),
            default=False,
            help_text=_('Designates whether the user can log into this admin site.'),
        )
        is_superuser = models.BooleanField(
            _('superuser status'),
            default=False,
            help_text=_(
                'Designates that this user has all permissions without '
                'explicitly assigning them.'
            ),
        )
# Can be fill with Camelot
        last_name = models.CharField(_('Nom'), max_length=35)
        birth_name = models.CharField(_('Nom de naissance'), max_length=35)
        first_name = models.CharField(_('Prénom'), max_length=35)
        status = models.CharField(
            _('Nom'), max_length=4, choices=STATUS_CHOICES)
        email = models.EmailField(_('email address'), blank=True)
        cmp = models.CharField(_('Composante'), max_length=3)
        birth_date = models.DateField(
            _('Date de naissance'), blank=True, null=True)
        username = models.CharField(
            _('Identifiant'), max_length=35, unique=True)

# To manually add depending on selected input
        profile = models.CharField(
            _("Profil"), max_length=10, choices=PROFILE_CHOICES)

        is_staff
        users = MeccUserManager()

        USERNAME_FIELD = 'username'
        REQUIRED_FIELDS = ['email']


class ScolManagerUser(MeccUser):
    is_ref_app = models.BooleanField(_('Référent application'), default=False)
