from django.utils.translation import ugettext as _
import re   # ### REGEX
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from mecc.apps.utils.ws import ask_camelot, get_pple

from .models import ECICommissionMember
from .forms import ECIForm, UserForm, MeccUserForm
from ..adm.forms import MeccUserForm, UserForm
from ..adm.models import MeccUser


def home(request, template='commission/home.html'):
    if request.is_ajax() and request.method == 'POST':
        id_member = request.POST.get('id_member', '')
        type_member = request.POST.get('type_member', '')
        user = MeccUser.objects.get(user__username=id_member)
        member = ECICommissionMember.objects.get(user=user)
        member.member_type = type_member
        member.save()

    data = {}
    data['form_user'] = UserForm
    data['form_meccuser'] = MeccUserForm
    data['form_eci'] = ECIForm
    if request.method == 'POST':
        person = {}
        for e in request.POST:
            person[e] = request.POST.get(e)

        member = ECICommissionMember.objects.create_member(person)
        # if form_data.is_valid():
        #     instance = form_data.save(commit=False)
        #     instance.save()


    data['commission_staff'] = ECICommissionMember.objects.all()
    data['staff_mails'] = [e.user.user.email for e in data['commission_staff']]

    return render(request, template, data)


def delete_member(request):
    if request.method == 'POST':
        id_member = request.POST.get('id_member', '')
        member = ECICommissionMember.objects.get(id_member=id_member)
        member.delete()
        return redirect('commission:home')
    return render(request)


def get_list_of_pple(request):
    data = {}
    if request.is_ajax():
        x = request.GET.get('member', '')
        if len(x) > 1:
            data['pple'] = get_pple(x)
            return JsonResponse(data)
        else:
            return JsonResponse({'message': _('Veuillez entrer au moins deux caractères.')})


def search(request, template='commission/select.html'):
    pass
    # if request.method == 'POST':
    #     form_data = ECIForm(request.POST)
    #     try:
    #         instance = form_data.save(commit=False)
    #         instance.save()
    #     except ValueError as e:
    #         return JsonResponse({'message': 'Les donnéees entrées ne\
    #         permetttent pas de créer un membre.'})
    #     return redirect('commission:home')
    #
    # data = {}
    # x = request.GET.get('member', '')
    # print(x)
    # if x != '':
    #     data['title'] = _('Résultats pour : "%s"' % x)
    #     request.session['liste'] = data['liste'] = get_pple(x)
    #     nb_found = len(data['liste'])
    #     data['form'] = ECIForm
    # return render(request, template, data)
