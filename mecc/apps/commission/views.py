from django.utils.translation import ugettext as _
from django.shortcuts import render,  redirect
from django.http import JsonResponse
from mecc.apps.utils.ws import get_from_ldap

from .models import ECICommissionMember
from .forms import ECIForm
from django_cas.decorators import login_required


@login_required
def home(request, template='commission/home.html'):
    """
    Home view
    """
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username', '')
        type_member = request.POST.get('type_member', '')
        member = ECICommissionMember.objects.get(username=username)
        member.member_type = type_member
        member.save()

    data = {}
    data['form'] = ECIForm
    if request.method == 'POST':
        form_data = ECIForm(request.POST)
        if form_data.is_valid():
            instance = form_data.save(commit=False)
            instance.save()

    data['commission_staff'] = ECICommissionMember.objects.all()
    data['staff_mails'] = [e.email for e in data['commission_staff']]

    return render(request, template, data)


@login_required
def delete_member(request):
    """
    Delete view
    """
    if request.method == 'POST':
        username = request.POST.get('username', '')
        member = ECICommissionMember.objects.get(username=username)
        member.delete()
        return redirect('commission:home')
    return render(request)


@login_required
def get_list_of_pple(request):
    # TODO: NOT A VIEW
    """
    Ajax : return list of pple with searched name
    """
    data = {}
    if request.is_ajax():
        x = request.GET.get('member', '')
        if len(x) > 1:
            ppl = [
                e for e in get_from_ldap(x) if e['username'] not in [
                    e.username for e in ECICommissionMember.objects.all()
                ]
            ]
            data['pple'] = sorted(ppl, key=lambda x: x['first_name'])
            return JsonResponse(data)
        else:
            return JsonResponse(
                {'message': _('Veuillez entrer au moins deux caractères.')})
