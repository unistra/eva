from django.contrib.sites.models import Site
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from .apps.adm.models import MeccUser



class UserChangeFormWithoutPass(UserChangeForm):

    def clean_password(self):
        return ""


class UserCreationFormWithoutPass(forms.ModelForm):
    """
    Overide ModelForm in order to remove password requirement.
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    password1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    password2 = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "email")

    def save(self, commit=True):
        user = super(UserCreationFormWithoutPass, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeFormWithoutPass(UserChangeForm):

    def clean_password(self):
        return ""



# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class MeccUserInline(admin.StackedInline):
    verbose_name = ""
    model = MeccUser
    can_delete = False
    fieldsets = (
        (_('Informations suplémentaires'), {'fields': ('status', "cmp", "birth_date", "profile")}),
    )


class UserAdmin(BaseUserAdmin):
    inlines = (MeccUserInline, )

    form = UserChangeFormWithoutPass
    add_form = UserCreationFormWithoutPass

    def get_status(self, obj):
        return obj.meccuser.get_status_display

    def get_profile(self, obj):
        return obj.meccuser.profile

    get_status.short_description = _('Statut')
    get_profile.short_description = _('Profil')

    get_status.admin_order_field = 'meccuser__status'
    get_profile.admin_order_field = 'meccuser__profile'

    list_display = ('username', 'is_superuser', 'get_status', 'get_profile')
    list_filter = ('is_staff',)

    fieldsets = (
        (_('Informations générales'), {'fields': ('username', "last_name", "first_name", "email")}),
    )
# Set & Register adm stuff

admin.site.unregister(User)
admin.site.unregister(Site)
admin.site.register(User, UserAdmin)


admin.site.site_header = "Administration"
admin.site.site_title = 'MECC'
