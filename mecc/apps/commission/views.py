from django.utils.translation import ugettext as _
from django.shortcuts import render,  redirect
from django.http import JsonResponse
from mecc.apps.utils.ws import get_from_ldap
from mecc.apps.training.models import Training
from .models import ECICommissionMember
from .forms import ECIForm
from django_cas.decorators import login_required

from mecc.decorators import is_ajax_request, is_post_request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@is_post_request
@is_ajax_request
@login_required
def change_typemember(request):
    username = request.POST.get('username', '')
    type_member = request.POST.get('type_member', '')
    member = ECICommissionMember.objects.get(username=username)
    member.member_type = type_member
    member.save()
    return JsonResponse({"Edited": True})


@login_required
def home(request, template='commission/home.html'):
    """
    Home view
    """
    data = {}
    data['form'] = ECIForm
    if request.method == 'POST':
        form_data = ECIForm(request.POST)
        if form_data.is_valid():
            instance = form_data.save(commit=False)
            instance.save()

    data['commission_staff'] = ECICommissionMember.objects.all().order_by('last_name')
    data['staff_mails'] = [e.email for e in data['commission_staff']]
    data['supply_mails'] = [e.email for e in data['commission_staff'] if e.member_type == 'supply']
    data['tenured_mails'] = [e.email for e in data['commission_staff'] if e.member_type == 'tenured']
    data['commission_mails'] = [e.email for e in data['commission_staff'] if e.member_type == 'commission']
    return render(request, template, data)


@is_post_request
@login_required
def delete_member(request):
    """
    Delete view
    """
    username = request.POST.get('username', '')
    member = ECICommissionMember.objects.get(username=username)
    member.delete()
    return redirect('commission:home')


@login_required
def get_list_of_pple(request):
    """
    Ajax : return list of pple with searched name
    """
    data = {}
    x = request.GET.get('member', '')
    y = request.GET.get('research_type', None)
    if y == 'ECI':
        r = [e.username for e in ECICommissionMember.objects.all()]
    if y == 'RESPFORM':
        z = request.GET.get('id_training')
        r = [e.user.username for e in
             Training.objects.get(id=z).resp_formations.all()]
    elif y is None:
        r = []
    if len(x) > 1:
        ppl = [e for e in get_from_ldap(x) if e['username'] not in r]
        data['pple'] = sorted(ppl, key=lambda x: x['first_name'])
        return JsonResponse(data)
    else:
        return JsonResponse(
            {'message': _('Veuillez entrer au moins deux caractères.')})


@is_post_request
@login_required
def send_mail(request):
    """
    Send mail
    """
    s = "[MECC] Notification"
    b = _("""
    Il s'agit d'un mail de test, Veuillez ne pas le prendre en considération.
    Merci.
    """)
    nobody = ['', ' ', None]
    # TODO: A decommenter pour envoyer aux bonnes personnes
    # to = [e.replace(' ', '') for e in request.POST.get('to').split(
    #     ',')] if request.POST.get('to') not in nobody else None
    # cc = [e.replace(' ', '') for e in request.POST.get('cc').split(
    #     ',')] if request.POST.get('cc') not in nobody else None
    # TODO: remove the following lines in production
    to = [
    #     'ibis.ismail@unistra.fr',
        'weible@unistra.fr'
        ]
    cc = ['ibis.ismail@unistra.fr']

    subject = request.POST.get('subject', s) if request.POST.get(
        'subject') not in ['', ' '] else s
    body = request.POST.get('body', b) if request.POST.get(
        'body') not in ['', ' '] else b

    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email="MECC Admin<%s>" % settings.MAIL_FROM,
        to=to,
        cc=cc,
        bcc=[settings.MAIL_ARCHIVES],
        headers={"Reply-To": settings.MAIL_FROM}
    )

    mail.send()
    return redirect('commission:home')
