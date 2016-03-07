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
from django_cas.decorators import login_required, user_passes_test, \
    permission_required

from mecc.apps.institute.forms import InstituteForm, DircompInstituteForm
from mecc.apps.years.forms import DircompInstituteYearForm, DircompUniversityYearForm
from mecc.apps.institute.models import Institute, AcademicField
from mecc.apps.years.models import InstituteYear
from mecc.apps.utils.ws import get_list_from_cmp
from mecc.apps.years.models import UniversityYear, InstituteYear
from mecc.apps.adm.models import MeccUser, Profile

import json
from datetime import datetime


@user_passes_test(lambda u: True if 'DIRCOMP' in [e.code for e in u.meccuser.profile.all()] else False)
def dircomp_edit_institute(request, code, template='institute/dircomp.html'):
    data = {}
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['expected_mecc'] = current_year.date_expected
    data['date_validation'] = current_year.date_validation
    data['university_year'] = current_year
    code_cmp = request.user.meccuser.cmp
    institute = Institute.objects.get(code=code)
    data['latest_instit_id'] = institute.id
    data['label_cmp'] = institute.label
    data['form_institute'] = DircompInstituteForm(instance=institute)
    institute_year = InstituteYear.objects.get(id_cmp=institute.id, code_year=current_year.code_year)
    try:
        institute_year.date_expected_MECC = datetime.strftime(institute_year.date_expected_MECC, '%d/%m/%Y')
    except TypeError:
        institute_year.date_expected_MECC = ''
    data['form_university_year'] = DircompUniversityYearForm(instance=current_year)
    data['form_institute_year'] = DircompInstituteYearForm(instance=institute_year)
    data['cadre_gen'] = "xxxxx.pdf"
    if request.POST:
        try:
            expected_mecc = datetime.strptime(request.POST.get('date_expected_MECC', ''), '%d/%m/%Y')
            institute_year.date_expected_MECC = datetime.strftime(expected_mecc, '%Y-%m-%d')
            institute_year.save()
        except ValueError:
            dircomp_edit_institute(request, code, template='institute/dircomp.html')
        return redirect('/') # Redirect after POST

    return render(request, template, data)


@user_passes_test(lambda u: True if 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def view_institute(request, code, template='institute/rac.html'):
    data = {}
    code_cmp = request.user.meccuser.cmp
    return render(request, template, data)


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
        current_year = UniversityYear.objects.get(
            is_target_year=True).code_year
        context['university_year'] = UniversityYear.objects.get(
                code_year=current_year)
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
        self.object = self.get_object()

        context = super(InstituteUpdate, self).get_context_data(**kwargs)
        try:
            context['latest_instit_id'] = Institute.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_instit_id'] = 1
        try:
            current_year = UniversityYear.objects.get(
                is_target_year=True).code_year
            context['institute_year'] = InstituteYear.objects.get(
                code_year=current_year, id_cmp=self.object.id)
            context['university_year'] = UniversityYear.objects.get(
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
        institute_list = []
        try:
            current_year = UniversityYear.objects.get(
                is_target_year=True).code_year
            ordered_list = Institute.objects.all().order_by('field', 'label')

            for e in ordered_list:
                iy = InstituteYear.objects.get(code_year=current_year, id_cmp=e.id)
                print(e.field.name)
                field = {
                    'domaine': e.field.name,
                    'label': e.label,
                    'code': e.code,
                    'dircomp': e.id_dircomp,
                    'rac': e.id_rac,
                    'date_expected_MECC': iy.date_expected_MECC,
                    'date_last_notif': iy.date_last_notif
                }
                institute_list.append(field)
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')

        context['ordered_list'] = institute_list
        return context
    model = Institute
