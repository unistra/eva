from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.signals import request_finished
from django.db.models import Q
from django.contrib.auth.models import User

from django_cas.decorators import login_required

from .models import Institute, AcademicField
from .forms import InstituteForm
from ..utils.ws import get_list_from_cmp
from ..years.models import UniversityYear, InstituteYear
from mecc.apps.adm.models import MeccUser, Profile

import json


@login_required
def get_list(request, employee_type, pk):
    if employee_type == 'prof':
        type_staff = 'Enseignant'
    elif employee_type == 'adm':
        type_staff = 'Administratif'
    t = get_list_from_cmp(cmp=pk, employee_type=type_staff, result=[])
    return JsonResponse(t, safe=False)


class InstituteDelete(DeleteView):

    model = Institute

    slug_field = 'code'
    slug_url_kwarg = 'code'

    success_url = '/institute'


class InstituteCreate(CreateView):
    def get_context_data(self, **kwargs):
        context = super(InstituteCreate, self).get_context_data(**kwargs)
        try:
            context['latest_instit_id'] = Institute.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_instit_id'] = 1
        try:
            current_year = UniversityYear.objects.get(
                is_target_year=True).code_year
            context['institute_year'] = InstituteYear.objects.filter(
                code_year=current_year)
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        context['cadre_gen'] = "xxxxx.pdf"
        return context

    model = Institute
    form_class = InstituteForm

    success_url = '/institute'


def out(new_username, profile, institute, request, name):
    inst = {'rac': institute.id_rac, 'dircomp': institute.id_dircomp}

    if name == inst[profile]:
        return

    user_profile = Profile.objects.get(code=profile.upper())
    u = MeccUser.objects.filter(
        Q(cmp__contains=institute.code) &
        Q(profile__code__contains=profile.upper())
    )

    old = list(u[:1])
    if old:
        old[0].profile.remove(user_profile)
        profiles = old[0].profile.all()
        if len(profiles) < 1:
            old[0].user.delete()
            old[0].delete()

    if new_username in ['', ' ', None]:
        return

    user, user_created = User.objects.get_or_create(username=new_username)
    if user_created:
        user.first_name = request.POST.get(str(profile) + '_first_name', '')
        user.last_name = request.POST.get(str(profile) + '_last_name', '')
        user.email = request.POST.get(str(profile) + '_mail', '')
        user.save()

    meccuser, meccuser_created = MeccUser.objects.get_or_create(user=user)
    meccuser.profile.add(user_profile)
    meccuser.cmp = institute.code

    meccuser.save()


@login_required
def edit_insitute(request, template='institute/institute_form.html', code=None):
    institute = Institute.objects.get(code=code)

    if request.method == 'POST':
        go = ['rac', 'dircomp']
        for e in go:
            username = request.POST.get("%s_username" % e)
            name = request.POST.get("id_%s" % e)
            out(username, e, institute, request, name)


        form = InstituteForm(request.POST, request.FILES, instance=institute)
        if form.is_valid():
            form.save()
            return redirect('institute:home') # Redirect after POST
    else:
        form = InstituteForm(instance=institute)

    return render(request, template, {'form': form})


class InstituteUpdate(UpdateView):

    model = Institute

    form_class = InstituteForm

    def get_context_data(self, **kwargs):
        context = super(InstituteUpdate, self).get_context_data(**kwargs)
        try:
            context['latest_instit_id'] = Institute.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_instit_id'] = 1
        try:
            current_year = UniversityYear.objects.get(
                is_target_year=True).code_year
            context['institute_year'] = InstituteYear.objects.filter(
                code_year=current_year)
            context['dates'] = UniversityYear.objects.get(
                code_year=current_year)
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        context['cadre_gen'] = "xxxxx.pdf"

        return context

    slug_field = 'code'
    slug_url_kwarg = 'code'

    success_url = '/institute'


class InstituteListView(ListView):
    def get_context_data(self, **kwargs):
        context = super(InstituteListView, self).get_context_data(**kwargs)
        try:
            context['ordered_list'] = Institute.objects.all().order_by(
                'field', 'label')
        except Institute.DoesNotExist:
            context['ordered_list'] = False
        try:
            current_year = UniversityYear.objects.get(
                is_target_year=True).code_year
            context['institute_year'] = InstituteYear.objects.filter(
                code_year=current_year)
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        return context

    model = Institute
