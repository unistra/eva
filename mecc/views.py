# -*- coding: utf-8 -*-

from django_cas.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from mecc.apps.years.models import UniversityYear


@login_required
def home(request):
    """
    root of all evil:
    dispatch according to user profile
    """ 
    try:
        target_year = UniversityYear.objects.get(is_target_year=True)
        request.session['current_year'] = target_year.label_year
        request.session['current_code_year'] = target_year.code_year
    except ObjectDoesNotExist:
        pass
    for e in request.user.groups.all():
        if e.name == "VP":
            return redirect('dashboards:general')
        if e.name == "DES1":
            return redirect('training:list_all')
    for e in request.user.meccuser.profile.all():
        if e.code == "RESPFORM" and e.year == request.session['current_code_year']:
            return redirect('training:list_resp')
        if e.code == 'REFAPP':
            return redirect('training:list', cmp=e.cmp)
        if e.code == 'DIRETU':
            return redirect('training:list', cmp=e.cmp)
        if e.code == "GESCOL":
            return redirect('training:list', cmp=e.cmp)
        if e.code in ['DIRCOMP', 'RAC']:
            return redirect('dashboards:institute', code=e.cmp)
        if e.code == "ECI":
            return redirect('training:list_all_meccs')
        if e.code == "RESPENS" and e.year == request.session['current_code_year']:
            return redirect('training:my_teachings')

    return render(request, 'base.html')
