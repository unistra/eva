from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers

import json

from .models import Institute, AcademicField
from .forms import InstituteForm


def edit(request, code, template='institute/create.html'):
    instance = get_object_or_404(Institute, code=code)
    form = InstituteForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('institute:home')
    return render(request, template, {'form': form})


def create(request, template='institute/create.html'):
    data = {}
    try:
        data['latest_id'] = Institute.objects.latest('id').id + 1
    except ObjectDoesNotExist:
        data['latest_id'] = 1
    data['form'] = InstituteForm

    return render(request, template, data)


def home(request, template='institute/home.html'):
    if request.method == 'POST':
        form_data = InstituteForm(request.POST)
        try:
            instance = form_data.save(commit=False)
            instance.save()
        except ValueError as e:
            return JsonResponse({'message': 'Les donnéees entrées ne\
            permetttent pas d\'ajouter une composante.'})
        return redirect('commission:home')

    data = {}

    list_institute = serializers.serialize(
        'json', Institute.objects.all(),
        fields=('code', 'label', 'field')
    )

    l = [e['fields'] for e in json.loads(list_institute)]

    data['institutes'] = l

    return render(request, template, data)
