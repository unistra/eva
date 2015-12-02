from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from mecc.apps.utils.ws import ask_camelot


from .models import ECICommissionMember
from .forms import ECICommissionMemberForm


def home(request, template='commission/home.html'):
    data = {}
    people = [e for e in ECICommissionMember.objects.all()]
    data['form'] = ECICommissionMemberForm
    if request.method == 'POST':
        form_data = ECICommissionMemberForm(request.POST)
        instance = form_data.save(commit=False)
        instance.save()

    data['commission_staff'] = ECICommissionMember.objects.all()
    return render(request, template, data)


def delete_member(request, pk):
    return render(request)


def search(request, template='commission/select.html'):

    if request.method == 'POST':
        print('ppp')
        form_data = ECICommissionMemberForm(request.POST)
        instance = form_data.save(commit=False)
        instance.save()

    if request.is_ajax():
        pass

    data = {}
    x = request.GET.get('member', '')
    data['title'] = _('Result for "%s"' % x)
    request.session['liste'] = data['liste'] = ask_camelot(x)
    nb_found = len(data['liste'])
    data['form'] = ECICommissionMemberForm

    # if nb_found == 1:
    #     print('only one')
    # elif nb_found == 0:
    #     print('nyulllll')
    # else:
    #     print('a looooooooooooooooooooooooooooooooooooot')
    return render(request, template, data)
