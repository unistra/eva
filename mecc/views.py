# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from mecc.apps.years.models import UniversityYear
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    try:
        request.session['current_year'] = UniversityYear.objects.get(is_target_year=True).label_year
    except ObjectDoesNotExist:
        pass
    return render_to_response('base.html')
