from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django_cas.decorators import login_required

from mecc.apps.utils.switch_users import request_with_other_user, \
    check_generic_password
from mecc.decorators import is_post_request, user_can_spoof


@login_required
@is_post_request
def spoof_user(request, template='spoof/form.html'):

    data = {}

    asked_user = request.POST.get('asked_username').replace(" ", "").lower()
    generic_pass = request.POST.get('pass')
    try:
        new_user = User.objects.get(username=asked_user)
    except ObjectDoesNotExist:
        data['error'] = _("L'utilisateur '%s' n'a pas \
        été trouvé." % asked_user)
        return render(request, template, data)
    if new_user.is_superuser or new_user.has_perm('cannot_be_spoofed'):
        data['error'] = _("Vous ne pouvez pas endosser \
        l'identité de %s." % asked_user)
        return render(request, template, data)

    if check_generic_password(generic_pass):

        real_username = request.session['real_username']
        r = request_with_other_user(request, new_user)
        r.session['real_username'] = real_username
        r.session['is_spoofed_user'] = True
        return redirect("/", request=r)
    else:
        data['error'] = _('Le mot de passe est erroné.')
    return render(request, template, data)


@user_can_spoof
@login_required
def home(request, template='spoof/form.html'):
    """
    Home spoof page.
    """
    try:
        if not request.session['is_spoofed_user']:
            request.session['real_username'] = request.user.username
    except KeyError:
        request.session['is_spoofed_user'] = False
        request.session['real_username'] = request.user.username
    return render(request, template)


def release_user(request):
    """
    Go back to original user
    """
    real_username = request.session['real_username']
    new_user = User.objects.get(username=real_username)
    request_with_other_user(request, new_user)

    request.session['is_spoofed_user'] = False

    return redirect('/')
