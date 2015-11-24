from django.shortcuts import render, get_object_or_404
from .models import ECICommission
from .forms import ECICommissionForm


def home(request, template='commission/home.html'):
    data = {}
    people = [e for e in ECICommission.objects.all()]
    data['form'] = ECICommissionForm
    print('here ! ')
    print(request)
    print('-------------')
    if request.method == 'POST':
        form_data = ECICommissionForm(request.POST)
        instance = form_data.save(commit=False)
        instance.save()

        print("123")

    data['commission_staff'] = ECICommission.objects.all()
    return render(request, template, data)


def delete_member(request, pk):
    print(pk)
