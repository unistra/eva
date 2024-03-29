from django.contrib.sites.models import Site
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.utils.translation import ugettext as _
from django.conf.urls import patterns
from django.shortcuts import render
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


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class MeccUserInline(admin.StackedInline):
    model = MeccUser
    can_delete = False
    fieldsets = (
        (_('Informations complémentaires'), {
            'fields': ('status', "cmp", "profile")}),
    )


class UserAdmin(BaseUserAdmin):

    form = UserChangeFormWithoutPass
    add_form = UserCreationFormWithoutPass

    list_filter = ('is_staff', 'groups__name', 'meccuser__profile__year', )
    list_display = ('username', 'is_superuser', 'get_profile', 'get_year',
                    'get_group', 'get_cmp')

    def get_cmp(self, obj):
        return obj.meccuser.cmp

    def get_profile(self, obj):
        return "<br>".join(
            ["%s %s" % (e.label, e.cmp) for e in obj.meccuser.profile.all()])
    # Allow br to work
    get_profile.allow_tags = True
    
    
    def get_year(self, obj):
        return "<br>".join(
            ["%s" % e.year for e in obj.meccuser.profile.all()])
    # Allow br to work
    get_year.allow_tags = True

    def get_group(self, obj):
        """
        get group, separate by comma, and display empty string if user has
        no group
        """
        return ','.join(
            [g.name for g in obj.groups.all()]) if obj.groups.count() else ''


    def lookup_allowed(self, key, value):
        if key in ('meccuser__profile__year',):
            return True
        return super(UserAdmin, self).lookup_allowed(key, value)

    get_cmp.short_description = _('Composante')
    get_group.short_description = _('Groupe')
    get_profile.short_description = _('Profil')
    get_year.short_description = _('Année')
    get_profile.admin_order_field = 'meccuser__profile'

    fieldsets = (
        (None, {'fields': ("username", "last_name", "first_name", "email")}),
        (None, {'fields': ('is_superuser', 'is_staff', 'groups')}),
    )


def editDES3password(request, template='admin/DES3.html'):
    data = {}
    if request.user.is_superuser:
        if request.POST:
            gen_user, created = User.objects.get_or_create(username='DES3')
            passw = request.POST.get('pass')
            gen_user.set_password(passw)
            gen_user.save()
            data['message'] = _('Le mot de passe a bien été modifié')

        return render(request, template, data)


def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns(
            '',
            (r'^DES3/$', admin.site.admin_view(editDES3password)),
        )
        return my_urls + urls
    return get_urls


# Set & Register adm stuff

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.register(User, UserAdmin)


admin.site.get_urls = get_admin_urls(admin.site.get_urls())
admin.site.site_header = "Administration"
admin.site.site_title = 'MECC'
