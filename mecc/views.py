# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.template import RequestContext
from mecc.apps.years.models import UniversityYear
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    try:
        o = UniversityYear.objects.get(is_target_year=True)

        request.session['current_year'] = o.label_year
        request.session['current_code_year'] = o.code_year
    except ObjectDoesNotExist:
        pass
    return render(request, 'base.html')
