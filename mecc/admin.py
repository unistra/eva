from django.forms import ModelForm
from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.forms import UserChangeForm
from django.forms import ModelForm
from django import forms
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _


class CustomUser(User):
    stuff = CharField(_('Stuff'), max_length=35)


class UserCreationFormWithoutPass(forms.ModelForm):
    """
    UserCreationForm without password
    """

    password1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    password2 = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ("username", "stuff")

    def save(self, commit=True):
        user = super(UserCreationFormWithoutPass, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        return user


class UserChangeFormWithoutPass(UserChangeForm):

    stuff = forms.CharField(max_length=15, min_length=None)


    def clean_password(self):
        return ""


class UserAdmin(UserAdmin):
    """
    Custom UserAdmin can create user without password
    """

    # list_display = ('username', 'is_superuser') #, 'des', 'agc')
    list_filter = ('is_staff',)

    form = UserChangeFormWithoutPass
    add_form = UserCreationFormWithoutPass
    #
    # def des(self, obj):
    #     return obj.has_perm('stats.can_view_counter')
    #
    # def agc(self, obj):
    #     return obj.has_perm('unpaids.can_view_unpaid')
    #
    # des.short_description = "Gestionnaire DES"
    # agc.short_description = "Gestionnaire Agence Comptable"

    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'groups', 'stuff')}),
    )


admin.site.site_header = "Administration"
admin.site.site_title = 'Justificatifs de scolarité'
admin.site.unregister(User)
admin.site.unregister(Site)
admin.site.register(User, UserAdmin)
