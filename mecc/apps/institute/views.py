from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.contrib.auth.models import User
from django_cas.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from mecc.apps.institute.forms import InstituteForm,  \
    DircompInstituteForm
from mecc.apps.years.forms import DircompInstituteYearForm, \
    DircompUniversityYearForm, DisabledInstituteYearForm
from mecc.apps.institute.models import Institute
from mecc.apps.years.models import InstituteYear, UniversityYear
from mecc.apps.utils.ws import get_list_from_cmp_by_ldap
from mecc.apps.adm.models import MeccUser, Profile
from mecc.apps.utils.manage_pple import manage_dircomp_rac
from datetime import datetime
from mecc.apps.utils.querries import currentyear
from mecc.apps.training.models import Training
from mecc.decorators import is_post_request


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def granted_edit_institute(request, code, template='institute/granted.html'):
    """
    Dispatch forms according to user profile
    """
    data = {}
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['university_year'] = current_year
    institute = Institute.objects.get(code=code)
    data['institute'] = institute
    data['latest_instit_id'] = institute.id
    data['label_cmp'] = institute.label
    data['form_institute'] = DircompInstituteForm(instance=institute)
    institute_year = InstituteYear.objects.get(
        id_cmp=institute.id, code_year=current_year.code_year)
    profiles = Profile.objects.filter(
        cmp=code).filter(Q(code="DIRCOMP") | Q(code="RAC") | Q(code="REFAPP"))
    if any(True for x in profiles if x in request.user.meccuser.profile.all()):
        data['can_edit_diretu'] = True
    else:
        data['can_edit_diretu'] = False
    try:
        institute_year.date_expected_MECC = datetime.strftime(
            institute_year.date_expected_MECC, '%d/%m/%Y')
    except TypeError:
        institute_year.date_expected_MECC = ''
    data['form_university_year'] = DircompUniversityYearForm(
        instance=current_year)
    data['form_institute_year'] = DircompInstituteYearForm(
        instance=institute_year)
    data['disabled_institute_year'] = DisabledInstituteYearForm(
        instance=institute_year)
    data['cadre_gen'] = UniversityYear.objects.get(is_target_year=True).pdf_doc
    if request.POST:
        try:
            expected_mecc = datetime.strptime(
                request.POST.get('date_expected_MECC', ''), '%d/%m/%Y')
            institute_year.date_expected_MECC = datetime.strftime(
                expected_mecc, '%Y-%m-%d')
            institute_year.save()
        except ValueError:
            granted_edit_institute(
                request, code, template='institute/dircomp.html')
        return redirect('/')  # Redirect after POST

    return render(request, template, data)


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def add_pple(request):
    """
    Process add diretu / gescol ajax querries
    """
    label_profile = {
        'DIRETU': "Directeurs d'études",
        'GESCOL': "Gestionnaire de scolarité",
        'REFAPP': "Référent d'application"}
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('mail')
        if any(True for x in [username, email] if x in ['', ' ', None]):
            return JsonResponse({
                'message': _('Veuillez remplir la zone de recherche')})

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = User.objects.create_user(username, email)
            user.last_name = request.POST.get('last_name')
            user.first_name = request.POST.get('first_name')
            user.save()

        try:
            meccuser = MeccUser.objects.get(user__username=username)
        except ObjectDoesNotExist:
            meccuser = MeccUser.objects.create(user=user)

        profile, created = Profile.objects.get_or_create(
            code=request.POST.get('type').upper(),
            cmp=request.POST.get('code_cmp'),
            year=currentyear().code_year,
            label=label_profile.get(request.POST.get('type').upper())
        )
        meccuser.cmp = request.POST.get('code_cmp')

        institute = Institute.objects.get(code=request.POST.get('code_cmp'))
        if request.POST.get('type') in ['diretu', 'DIRETU']:
            if meccuser in institute.diretu.all():
                return JsonResponse({
                    'message': _("%(last_name)s %(first_name)s est déjà \
                    directeur d'études" % {
                        'last_name': request.POST.get('last_name'),
                        'first_name': request.POST.get('first_name')
                    })
                })
            institute.diretu.add(meccuser)
            institute.save()
        else:
            if meccuser in institute.scol_manager.all():
                return JsonResponse({
                    'message': _("%(last_name)s %(first_name)s est déjà \
                    gestionnaire de scolarité" % {
                        'last_name': request.POST.get('last_name'),
                        'first_name': request.POST.get('first_name')
                    })
                })
            meccuser.is_ref_app = False if request.POST.get(
                'is_ref_app') == 'false' else True
            if meccuser.is_ref_app:
                profile, created = Profile.objects.get_or_create(
                    code="REFAPP",
                    cmp=request.POST.get('code_cmp'),
                    year=currentyear().code_year,
                    label=label_profile.get('REFAPP')
                )
            institute.scol_manager.add(meccuser)
            institute.save()

        meccuser.profile.add(profile)
        meccuser.save()

        return JsonResponse({
            'success': _("%(last_name)s %(first_name)s a bien été ajouté" % {
                'last_name': request.POST.get('last_name'),
                'first_name': request.POST.get('first_name')
            })
        })


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def remove_pple(request):
    """
    Process remove diretu/gescol ajax querriessc
    """
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        institute = Institute.objects.get(code=request.POST.get('code_cmp'))
        meccuser = MeccUser.objects.get(user__username=username)
        code = 'REFAPP' if request.POST.get(
            'type') == 'GESCOL' and meccuser.is_ref_app else request.POST.get('type')
        prof = [e for e in meccuser.profile.all() if
                e.code == code and
                e.cmp == request.POST.get('code_cmp') and
                e.year == currentyear().code_year][0]

        if request.POST.get('type') in ['diretu', 'DIRETU']:
            institute.diretu.remove(meccuser)
            institute.save()
        else:
            institute.scol_manager.remove(meccuser)
            institute.save()

        meccuser.profile.remove(prof)
        if len(meccuser.profile.all()) < 1:
            meccuser.user.delete()
            meccuser.delete()

        return JsonResponse({
            'success': _("%(last_name)s %(first_name)s a bien été supprimé" % {
                'last_name': meccuser.user.last_name,
                'first_name': meccuser.user.first_name
            })
        })


@login_required
def get_list(request, employee_type, pk):
    """
    Return list of professor or administration staff
    """
    status = {'prof': 'Enseignant', 'adm': 'Administratif'}
    t = get_list_from_cmp_by_ldap(cmp=pk)
    result = [e for e in t if e.get('status') == status.get(employee_type)]
    return JsonResponse(result, safe=False)


class InstituteDelete(DeleteView):
    """
    Delete Institute view
    """
    model = Institute

    slug_field = 'code'
    slug_url_kwarg = 'code'

    success_url = '/institute'

    def get_context_data(self, **kwargs):
        context = super(InstituteDelete, self).get_context_data(**kwargs)
        trainings = Training.objects.filter(institutes=kwargs['object'])
        context['trainings'] = trainings if len(trainings) > 0 else None
        return context


class InstituteCreate(CreateView):
    """
    Create institute view
    """

    def get_context_data(self, **kwargs):
        context = super(InstituteCreate, self).get_context_data(**kwargs)
        try:
            context['latest_instit_id'] = Institute.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_instit_id'] = 1
        try:
            uy = UniversityYear.objects.get(is_target_year=True)
            current_year = uy.code_year
            context['cadre_gen'] = uy.pdf_doc
            context['institute_year'] = InstituteYear.objects.filter(
                code_year=current_year)
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        current_year = UniversityYear.objects.get(
            is_target_year=True).code_year
        context['university_year'] = UniversityYear.objects.get(
            code_year=current_year)
        return context

    model = Institute
    form_class = InstituteForm

    success_url = '/institute'


@login_required
def edit_insitute(request, template='institute/institute_form.html', code=None):
    """
    Edit instiute view
    """
    institute = Institute.objects.get(code=code)

    if request.method == 'POST':
        go = ['rac', 'dircomp']
        for e in go:
            username = request.POST.get("%s_username" % e)
            name = request.POST.get("id_%s" % e)
            manage_dircomp_rac(username, e, institute, request, name)

        form = InstituteForm(request.POST, request.FILES, instance=institute)
        if form.is_valid():
            form.save()
            return redirect('institute:home')  # Redirect after POST
    else:
        form = InstituteForm(instance=institute)

    return render(request, template, {'form': form, 'institute': institute})


class InstituteUpdate(UpdateView):
    """
    Institute update view
    """
    model = Institute

    form_class = InstituteForm

    def get_context_data(self, **kwargs):
        self.object = self.get_object()

        context = super(InstituteUpdate, self).get_context_data(**kwargs)

        if self.kwargs.get('code') in [
                e.cmp for e in self.request.user.meccuser.profile.all() if
                e.code == "RESPFORM"]:
            context['cannot_edit'] = True
        else:
            context['cannot_edit'] = False
        try:
            context['latest_instit_id'] = Institute.objects.latest('id').id + 1
        except ObjectDoesNotExist:
            context['latest_instit_id'] = 1
        try:
            uy = UniversityYear.objects.get(is_target_year=True)
            current_year = uy.code_year
            context['cadre_gen'] = uy.pdf_doc
            context['institute_year'] = InstituteYear.objects.get(
                code_year=current_year, id_cmp=self.object.id)
            context['university_year'] = uy
            context['institute'] = self.object

        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        return context

    slug_field = 'code'
    slug_url_kwarg = 'code'

    success_url = '/institute'


class InstituteListView(ListView):
    """
    Institute List view
    """

    def get_context_data(self, **kwargs):
        context = super(InstituteListView, self).get_context_data(**kwargs)
        institute_list = []
        warnme = []
        try:
            current_year = UniversityYear.objects.get(
                is_target_year=True).code_year
            ordered_list = Institute.objects.all().order_by('field', 'label')
            for institute in ordered_list:
                try:
                    iy = InstituteYear.objects.get(
                        code_year=current_year, id_cmp=institute.id)
                    field = {
                        'domaine': institute.field.name,
                        'code': institute.code,
                        'labelled': "%s - %s" % (institute.label, institute.ROF_code) if institute.ROF_code not in ['', ' ', None] else institute.label,
                        'dircomp': institute.id_dircomp,
                        'rac': institute.id_rac,
                        'date_expected_MECC': iy.date_expected_MECC,
                        'date_last_notif': iy.date_last_notif,
                        'is_late': iy.is_expected_date_late,
                        'ROF_support': institute.ROF_support,
                        'is_hs': not institute.is_on_duty,
                    }
                    institute_list.append(field)
                except:
                    warnme.append("%s - %s" % (institute.label, institute.ROF_code)
                                  if institute.ROF_code not in ['', ' ', None] else institute.label,)

        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée.')
        except InstituteYear.DoesNotExist:
            context['institute_year'] = _("L'initialisation des composantes \
            pour l'année selectionnée n'a pas encore été effectuée.")

        if len(warnme) > 0:
            context['warning'] = _('Il y a de(s) composante(s) non initialisée(s) \
                pour cette année universitaire : %s' % (warnme))
        context['ordered_list'] = institute_list
        return context
    model = Institute


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def validate_institute(request, code, template='institute/validate.html'):
    """
    Validate MECC in institute
    """
    data = {}
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    data['university_year'] = current_year
    institute = Institute.objects.get(code=code)
    data['institute'] = institute
    data['latest_instit_id'] = institute.id
    data['label_cmp'] = institute.label
    data['form_institute'] = DircompInstituteForm(instance=institute)
    institute_year = InstituteYear.objects.get(
        id_cmp=institute.id, code_year=current_year.code_year)

    data['trainings'] = Training.objects.filter(
        code_year=currentyear().code_year if currentyear() is not None else None,
        institutes__code=code).order_by('degree_type')

    try:
        institute_year.date_expected_MECC = datetime.strftime(
            institute_year.date_expected_MECC, '%d/%m/%Y')
    except TypeError:
        institute_year.date_expected_MECC = ''

    return render(request, template, data)


@is_post_request
@login_required
def send_mail(request):
    """
    Send mail
    """
    meccuser = MeccUser.objects.get(user__username=request.user.username)

    s = "[MECC] Notification"
    b = _("""
    Il s'agit d'un mail de test, Veuillez ne pas le prendre en considération.
    Merci.
    """)
    to = ['ibis.ismail@unistra.fr', 'weible@unistra.fr', 'baguet@unistra.fr']
    cc = bcc = ['ibis.ismail@unistra.fr']
    subject = request.POST.get('subject', s) if request.POST.get(
        'subject') not in ['', ' '] else s
    body = request.POST.get('body', b) if request.POST.get(
        'body') not in ['', ' '] else b

    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email="MECC Admin<%s>" % settings.MAIL_FROM,
        to=[settings.MAIL_FROM],
        cc=cc,
        bcc=to,
        headers={"Reply-To": request.user.email}
    )
    mail.send()

    return redirect('/institute/validate/%s' % meccuser.cmp)
