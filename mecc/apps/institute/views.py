from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import JsonResponse, HttpResponse


from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from ..utils.ws import get_list_from_cmp
import json

from .models import Institute, AcademicField
from .forms import InstituteForm

from ..years.models import UniversityYear, InstituteYear


from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.signals import request_finished


def get_list(request, employee_type, pk):
    if employee_type == 'prof':
        type_staff = 'Enseignant'
    elif employee_type == 'adm':
        type_staff = 'Administratif'
    t = get_list_from_cmp(cmp=pk, employee_type=type_staff, result=[])
    return JsonResponse(t, safe=False)


def get_dircom_and_rac(request):
    data = []
    if request.is_ajax():
        code = request.GET.get('code_cmp', '')
        institute = Institute.objects.get(code=code)
        data['dircomp'] = institute.dircomp
        data['rac'] = institute.rac


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


def edit_insitute(request, template='institute/institute_form.html', code=None):
    if code:
        f = Institute.objects.get(code=code)
    else:
        f = None

    if request.method == 'POST':
        form = InstituteForm(request.POST, request.FILES, instance=f)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = InstituteForm(instance=f)

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
