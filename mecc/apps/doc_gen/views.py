"""
View for document generator 3000
"""
from django.utils.translation import ugettext as _
from django.shortcuts import render,  redirect
from django.http import JsonResponse


def home(request, template='doc_generator/home.html'):
    data = []
    return render(request, template, data)
