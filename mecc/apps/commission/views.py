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
    print('home ')
    print(request)
    print('-------------')
    if request.method == 'POST':
        form_data = ECICommissionMemberForm(request.POST)
        instance = form_data.save(commit=False)
        instance.save()

    data['commission_staff'] = ECICommissionMember.objects.all()
    return render(request, template, data)


def delete_member(request, pk):
    print(pk)
    return render(request)


def search(request, template='commission/select.html'):

    if request.is_ajax():
        print("i'm ajax, man")

    data = {}
    x = request.GET.get('member', '')
    data['title'] = _('Result for "%s"' % x)
    print("\n============\n  Asking : %s \n============\n" % x)
    request.session['liste'] = data['liste'] = ask_camelot(x)
    print('.....')
    return render(request, template, data)
