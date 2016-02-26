from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from mecc.apps.adm.models import Group_DES3
from mecc.apps.spoof.forms import UserForm
from django.contrib.auth.models import User


def home(request, template='adm/home.html'):
    asked_user = request.POST.get('asked_username')
    generic_pass = request.POST.get('pass')
    data = {}
    return render(request, template, data)


def spoof_user(request, username):
    if isAllowed(request.user):
        new_user = get_object_or_404(User, username=username)
        request.session['is_spoofed_user'] = True
        request.session['real_user'] = request.user
        print(request.user)


def isAllowed(user):
    """
    Return True if current user can view unpaids
    """
    return user.has_perm('adm.can_spoof_user')


class DES3Create(CreateView):

        model = Group_DES3
        form_class = UserForm
        success_url = '/institute'


class DES3Edit(UpdateView):

    model = Group_DES3
    form_class = UserForm
    success_url = '/institute'
