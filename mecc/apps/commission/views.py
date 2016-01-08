from django.utils.translation import ugettext_lazy as _
import re   # ### REGEX
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from mecc.apps.utils.ws import ask_camelot

from .models import ECICommissionMember
from .forms import ECICommissionMemberForm


def home(request, template='commission/home.html'):
    if request.is_ajax() and request.method == 'POST':
        id_member = request.POST.get('id_member', '')
        last_name = request.POST.get('last_name', '')
        type_member = request.POST.get('type_member', '')
        member = ECICommissionMember.objects.get(id_member=id_member)
        if member.name == last_name:
            member.member_type = type_member
            member.save()

    data = {}
    data['form'] = ECICommissionMemberForm
    # if request.method == 'POST':
    #     form_data = ECICommissionMemberForm(request.POST)
    #     instance = form_data.save(commit=False)
    #     instance.save()

    data['commission_staff'] = ECICommissionMember.objects.all()
    data['staff_mails'] = re.sub(r"'| |]|\[", "",  # ###### REGEX POWA !!!
        str([e.mail for e in data['commission_staff']])).replace('|', ',')

    return render(request, template, data)


def delete_member(request):
    if request.method == 'POST':
        id_member = request.POST.get('id_member', '')
        member = ECICommissionMember.objects.get(id_member=id_member)
        member.delete()
        return redirect('commission:home')
    return render(request)


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
    request.session['liste'] = data['liste'] = ask_camelot(x)
    nb_found = len(data['liste'])
    data['form'] = ECICommissionMemberForm
    #
    # if nb_found == 1:
    #     print(data['liste'])
    #     print('only one')
    # elif nb_found == 0:
    #     print('nyulllll')
    # else:
    #     print('a looooooooooooooooooooooooooooooooooooot')
    return render(request, template, data)
