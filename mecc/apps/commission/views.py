from django.utils.translation import ugettext_lazy as _
import re   # ### REGEX
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from mecc.apps.utils.ws import ask_camelot, get_pple

from .models import ECICommissionMember
from .forms import ECICommissionMemberForm


def home(request, template='commission/home.html'):
    if request.is_ajax() and request.method == 'POST':
        id_member = request.POST.get('id_member', '')
        type_member = request.POST.get('type_member', '')
        member = ECICommissionMember.objects.get(id_member=id_member)
        member.member_type = type_member
        member.save()

    data = {}
    data['form'] = ECICommissionMemberForm
    if request.method == 'POST':
        form_data = ECICommissionMemberForm(request.POST)
        if form_data.is_valid():
            instance = form_data.save(commit=False)
            instance.save()

    data['commission_staff'] = ECICommissionMember.objects.all()
    data['staff_mails'] = [e.mail for e in data['commission_staff']]

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
        data['pple'] = get_pple(x)
        return JsonResponse(data)


def search(request, template='commission/select.html'):
    if request.method == 'POST':
        form_data = ECICommissionMemberForm(request.POST)
        try:
            instance = form_data.save(commit=False)
            instance.save()
        except ValueError as e:
            return JsonResponse({'message': 'Les donnéees entrées ne\
            permetttent pas de créer un membre.'})
        return redirect('commission:home')

    data = {}
    x = request.GET.get('member', '')
    data['title'] = _('Résultats pour : "%s"' % x)
    request.session['liste'] = data['liste'] = get_pple(x)
    nb_found = len(data['liste'])
    data['form'] = ECICommissionMemberForm
    return render(request, template, data)
