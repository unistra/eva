from django.shortcuts import render, redirect
from mecc.apps.utils.switch_users import request_with_other_user, \
    check_generic_password
from django.contrib.auth.models import User
from django_cas.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden


@login_required
def home(request, template='spoof/form.html'):
    """
     Default spoof page.
    """

    if request.user.has_perm('adm.can_spoof_user') or \
            'DES3' in request.user.groups.values_list('name', flat=True):

        try:
            if request.session['is_spoofed_user'] == False:
                request.session['real_username'] = request.user.username
        except KeyError:
            request.session['is_spoofed_user'] = False
            request.session['real_username'] = request.user.username

        data = {}
        if request.POST:
            asked_user = request.POST.get('asked_username')
            generic_pass = request.POST.get('pass')
            try:
                new_user = User.objects.get(username=asked_user)
            except ObjectDoesNotExist as e:
                data['error'] = _("L'utilisateur '%s' n'a pas \
                été trouvé." % asked_user)
                return render(request, template, data)
            if new_user.is_superuser or new_user.has_perm('cannot_be_spoofed'):
                data['error'] = _("Vous ne pouvez pas usurper \
                l'identité de %s." % asked_user)
                return render(request, template, data)

            if check_generic_password(generic_pass):

                real_username = request.session['real_username']
                r = request_with_other_user(request, new_user)
                r.session['real_username'] = real_username
                r.session['is_spoofed_user'] = True
                return redirect("/", request=r)
            else:
                data['error'] = _('Le mot de passe est érroné.')
        return render(request, template, data)

    return HttpResponseForbidden("<h1>Forbidden</h1>You do not have permission \
        to access this page.")


def release_user(request):
    """
    Go back to original user
    """
    real_username = request.session['real_username']
    new_user = User.objects.get(username=real_username)
    r = request_with_other_user(request, new_user)

    request.session['is_spoofed_user'] = False

    return redirect('/')
