import json

from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django_cas.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import formats

from mecc.apps.institute.forms import InstituteForm,  \
    DircompInstituteForm
from mecc.apps.institute.models import Institute
from mecc.apps.years.forms import DircompInstituteYearForm, \
    DircompUniversityYearForm, DisabledInstituteYearForm

from mecc.apps.years.models import InstituteYear, UniversityYear
from mecc.apps.utils.ws import get_list_from_cmp_by_ldap
from mecc.apps.adm.models import MeccUser, Profile
from mecc.apps.utils.manage_pple import manage_dircomp_rac
from mecc.apps.utils.queries import institute_staff
from datetime import datetime
from mecc.apps.utils.queries import currentyear
from mecc.apps.training.models import Training
from mecc.decorators import is_post_request, group_required, is_ajax_request
from mecc.apps.files.models import FileUpload


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def granted_edit_institute(request, code, template='institute/granted.html'):
    """
    Dispatch forms according to user profile
    """
    data = {}
    try:
        current_year = currentyear().code_year
    except AttributeError:
        return render(request, 'msg.html', {'msg': "Initialisation de l'année non effectuée"})
    institute = Institute.objects.get(code=code)
    institute_year = InstituteYear.objects.get(
        id_cmp=institute.id, code_year=current_year)
    if request.POST:
        date_to_pass = request.POST.get('date_expected_MECC')
        request.POST = {}
        try:
            expected_mecc = datetime.strptime(
                date_to_pass, '%d/%m/%Y')
            institute_year.date_expected_MECC = datetime.strftime(
                expected_mecc, '%Y-%m-%d')
            institute_year.save()
        except ValueError:
            granted_edit_institute(
                request, code, template='institute/granted.html')
        return granted_edit_institute(
            request, code, template='institute/granted.html')  # Redirect after POST
    data['university_year'] = current_year
    data['institute'] = institute
    data['latest_instit_id'] = institute.id
    data['label_cmp'] = institute.label
    data['form_institute'] = DircompInstituteForm(instance=institute)

    profiles = Profile.objects.filter(
        cmp=code).filter(
            Q(code="DIRCOMP") | Q(code="RAC") | Q(code="REFAPP")
    )
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
        instance=currentyear())
    data['form_institute_year'] = DircompInstituteYearForm(
        instance=institute_year)
    data['disabled_institute_year'] = DisabledInstituteYearForm(
        instance=institute_year)
    data['cadre_gen'] = FileUpload.objects.filter(
        object_id=currentyear().id).first()
    data['letter_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='letter_%s/%s' % (
            current_year, current_year + 1))
    data['misc_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='misc_%s/%s' % (
            current_year, current_year + 1))
    data['year_object'] = currentyear()
    data['published_meccs'] = Training.objects.filter(
        is_used=True,
        code_year=current_year,
        supply_cmp=institute.code,
    ).prefetch_related(
        'degree_type',
    ).order_by(
        'degree_type__display_order',
        'label',
    )

    return render(request, template, data)


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def add_pple(request):
    """
    Process add diretu / gescol ajax queries
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
                    'message': _("%(first_name)s %(last_name)s est déjà \
                    directeur d'études" % {
                        'first_name': request.POST.get('first_name'),
                        'last_name': request.POST.get('last_name')
                    })
                })
            institute.diretu.add(meccuser)
            institute.save()
        else:
            if meccuser in institute.scol_manager.all():
                return JsonResponse({
                    'message': _("%(first_name)s %(last_name)s  est déjà \
                    gestionnaire de scolarité" % {
                        'first_name': request.POST.get('first_name'),
                        'last_name': request.POST.get('last_name')
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
            'success': _("%(first_name)s %(last_name)s a bien été ajouté" % {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name')
            })
        })


@user_passes_test(lambda u: True if 'DIRCOMP' or 'RAC' in [e.code for e in u.meccuser.profile.all()] else False)
def remove_pple(request):
    """
    Process remove diretu/gescol ajax queriessc
    """

    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        institute = Institute.objects.get(code=request.POST.get('code_cmp'))
        meccuser = MeccUser.objects.get(user__username=username)
        code = 'REFAPP' if request.POST.get(
            'type') == 'GESCOL' and meccuser.is_ref_app else request.POST.get('type')
        prof = [e for e in meccuser.profile.all() if
                e.code == code and
                e.cmp == request.POST.get('code_cmp')][0]

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
            'success': _("%(first_name)s %(last_name)s a bien été supprimé" % {
                'first_name': meccuser.user.first_name,
                'last_name': meccuser.user.last_name
            })
        })


@login_required
def get_list(request, employee_type, pk):
    """
    Return list of professor or administration staff
    """
    status = {'prof': 'Enseignant', 'adm': 'Administratif'}
    t = get_list_from_cmp_by_ldap(cmp=pk)
    result = [e for e in t if e.get('status') == status.get(
        employee_type)] if employee_type != "all" else t
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
            context['cadre_gen'] = FileUpload.objects.filter(
                object_id=uy.id).first()
            context['institute_year'] = InstituteYear.objects.filter(
                code_year=current_year)
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        current_year = UniversityYear.objects.get(
            is_target_year=True).code_year
        context['university_year'] = UniversityYear.objects.get(
            code_year=current_year)
        return context

    def get_form_kwargs(self):
        kwargs = super(InstituteCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    model = Institute
    form_class = InstituteForm

    success_url = '/institute'


@login_required
def edit_institute(request, template='institute/institute_form.html', code=None):
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

        form = InstituteForm(request.POST, request.FILES, instance=institute, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('institute:home')  # Redirect after POST
    else:
        form = InstituteForm(instance=institute, user=request.user)

    return render(request, template, {'form': form, 'institute': institute})


class InstituteUpdate(UpdateView):
    """
    Institute update view
    """
    model = Institute

    form_class = InstituteForm

    def post(self, request, *args, **kwargs):
        # En mode ROF le champ ROF_support ne peut être modifié que si user.is_staff
        # Le formulaire ne retourne donc aucune valeur : reprise ici de l'info en BD
        obj = self.get_object()  # type: Institute
        if not request.user.is_staff:
            request.POST = request.POST.copy()
            request.POST['ROF_support'] = obj.ROF_support
        return super(InstituteUpdate, self).post(request, *args, **kwargs)

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
            context['cadre_gen'] = FileUpload.objects.filter(
                object_id=uy.id).first()
            context['institute_year'] = InstituteYear.objects.get(
                code_year=current_year, id_cmp=self.object.id)
            context['university_year'] = uy
            context['institute'] = self.object
            context['letter_file'] = FileUpload.objects.filter(
                object_id=self.object.id, additional_type='letter_%s/%s' % (current_year, current_year + 1))
            context['misc_file'] = FileUpload.objects.filter(
                object_id=self.object.id, additional_type='misc_%s/%s' % (current_year, current_year + 1))
            context['published_meccs'] = Training.objects.filter(
                is_used=True,
                code_year=uy.code_year,
                supply_cmp=self.object.code,
            ).prefetch_related(
                'degree_type',
            ).order_by(
                'degree_type__display_order',
                'label',
            )
        except UniversityYear.DoesNotExist:
            context['institute_year'] = _('Aucune année selectionnée')
        return context

    def get_form_kwargs(self):
        kwargs = super(InstituteUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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
    institute = Institute.objects.get(code=code)
    institute_year = InstituteYear.objects.get(
        id_cmp=institute.id, code_year=current_year.code_year)
    data['letter_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='letter_%s/%s' % (current_year.code_year, current_year.code_year + 1))
    data['misc_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='misc_%s/%s' % (current_year.code_year, current_year.code_year + 1))
    data['university_year'] = current_year
    data['institute'] = institute
    data['latest_instit_id'] = institute.id
    data['label_cmp'] = institute.label
    data['form_institute'] = DircompInstituteForm(instance=institute)
    data['date_last_notif'] = institute_year.date_last_notif
    trainings = Training.objects.filter(
        code_year=currentyear().code_year if currentyear() is not None else None,
        institutes__code=code,
        is_used=True
    ).order_by(
        'degree_type',
        'label'
    )
    trainings = _filter_out_rof_excluded_trainings(institute, trainings)
    data['trainings'] = trainings
    data['notification_to'] = settings.MAIL_FROM
    data['notification_object'] = "%s - %s %s" % (
        institute.label, request.user.first_name, request.user.last_name)
    data['mail_prefix'] = settings.EMAIL_SUBJECT_PREFIX

    if hasattr(settings, 'EMAIL_TEST'):
        data['test_mail'] = _("""
Il s'agit d'un mail de test, Veuillez ne pas le prendre en considération.
Merci.
        """)

    try:
        errors = False

        if request.POST:

            data['date_mecc'] = request.POST.get('date_mecc')
            datetime_mecc = datetime.strptime(data['date_mecc'], '%d/%m/%Y')
            # datetime.strptime(
            #    data['date_mecc'], '%d/%m/%Y')
            if datetime_mecc > datetime.today():
                errors = True
                messages.add_message(request, messages.ERROR, _(
                    'La date ne peut être ulterieure à la date du jour !'))

            data['selected_trainings'] = Training.objects.filter(
                pk__in=request.POST.getlist('chkbox[]'))

            if not data['selected_trainings']:
                errors = True
                messages.add_message(request, messages.ERROR, _(
                    'Veuillez selectionner au moins un diplôme !'))

            for training in data['selected_trainings']:
                if training.progress_rule == 'E' or training.progress_table == 'E':
                    errors = True
                    messages.add_message(request, messages.ERROR, _(
                        'La saisie des règles ou du tableau pour les élements sélectionnés n\'est pas terminée'))
                if training.date_visa_des or training.date_val_cfvu:
                    errors = True
                    messages.add_message(request, messages.ERROR, _(
                        'Vous ne pouvez pas modifier la date de validation : une date de visa DES ou de validation CFVU a été enregistrée'))

            if not errors:
                # TODO tz needed (???)
                date_mecc = datetime.strftime(datetime_mecc, '%Y-%m-%d')
                data['selected_trainings'].filter(progress_rule="A", progress_table="A").update(
                    date_val_cmp=date_mecc)

    except (ValueError, TypeError):
        messages.add_message(request, messages.ERROR, _(
            'Veuillez renseigner une date de validation valide'))
    return render(request, template, data)


@group_required('DES1', 'DES2', 'DES3')
def check_validate_institute(request, code, template='institute/check_validate.html'):
    """
    Check institutes' Mecc validation
    """
    data = {}
    try:
        current_year = list(UniversityYear.objects.filter(
            Q(is_target_year=True))).pop(0)
    except:
        return render(request, 'msg.html', {'msg' : "Initialisation de l'année non effectuée"})

    institute = Institute.objects.get(code=code)
    institute_year = InstituteYear.objects.get(
        id_cmp=institute.id, code_year=current_year.code_year)
    staff = institute_staff(code)
    data['letter_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='letter_%s/%s' % (current_year.code_year, current_year.code_year + 1))
    data['misc_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='misc_%s/%s' % (current_year.code_year, current_year.code_year + 1))
    data['university_year'] = current_year
    data['institute'] = institute
    data['latest_instit_id'] = institute.id
    data['label_cmp'] = institute.label
    data['form_institute'] = DircompInstituteForm(instance=institute)
    data['date_last_notif'] = institute_year.date_last_notif
    trainings = Training.objects.filter(
        code_year=currentyear().code_year if currentyear() is not None else None,
        institutes__code=code,
        is_used=True
    ).order_by(
        'degree_type',
        'label'
    )
    trainings = _filter_out_rof_excluded_trainings(institute, trainings)
    data['trainings'] = trainings
    data['notification_to'] = [user.email for user in staff.filter(
        meccuser__profile__code__in=["RAC", "DIRCOMP", "DIRETU"]).distinct()]
    data['notification_cc'] = [user.email for user in staff.filter(
        meccuser__profile__code="REFAPP").distinct()]
    data['notification_full'] = data[
        'notification_to'] + data['notification_cc']
    data['notification_object'] = "%s" % institute.label
    data['mail_prefix'] = settings.EMAIL_SUBJECT_PREFIX

    if hasattr(settings, 'EMAIL_TEST'):
        data['test_mail'] = _("""
Il s'agit d'un mail de test, Veuillez ne pas le prendre en considération.
Merci. """)

    try:
        errors = False

        if request.POST:
            data['date_mecc'] = request.POST.get('date_mecc')
            datetime_mecc = datetime.strptime(data['date_mecc'], '%d/%m/%Y')
            # datetime.strptime(
            #    data['date_mecc'], '%d/%m/%Y')
            if datetime_mecc > datetime.today():
                errors = True
                messages.add_message(request, messages.ERROR, _(
                    'La date ne peut être ulterieure à la date du jour !'))

            data['selected_trainings'] = Training.objects.filter(
                pk__in=request.POST.getlist('chkbox[]'))

            if not data['selected_trainings']:
                errors = True
                messages.add_message(request, messages.ERROR, _(
                    'Veuillez selectionner au moins un diplôme !'))

            for training in data['selected_trainings']:
                if datetime_mecc.date() < training.date_visa_des:
                    errors = True
                    messages.add_message(request, messages.ERROR, _(
                        'La date de CFVU (%s) ne peut être antérieure à la date du visa DES (%s)'
                    ) % (formats.date_format(datetime_mecc.date(), "SHORT_DATE_FORMAT"), formats.date_format(training.date_visa_des, "SHORT_DATE_FORMAT")))

            if not errors:
                # TODO tz needed (???)
                date_mecc = datetime.strftime(datetime_mecc, '%Y-%m-%d')

                # Should not happen but for now control if one of the fields is != 'A'
                for d in data['selected_trainings']:
                    if d.progress_rule != 'A' or d.progress_table != 'A':
                        messages.add_message(request, messages.ERROR, _(
                            "Attention état d'avancement de la saisie des règles ou saisie tableau MECC non achevé pour : ") + d.label)

                data['selected_trainings'].filter(progress_rule="A", progress_table="A").update(
                    date_val_cfvu=date_mecc)

    except (ValueError, TypeError):
        messages.add_message(request, messages.ERROR, _(
            'Veuillez renseigner une date de validation valide'))
    return render(request, template, data)


def _filter_out_rof_excluded_trainings(institute, trainings):
    if institute.ROF_support:
        trainings = trainings.exclude(is_existing_rof=False)
    else:
        trainings = trainings.exclude(is_existing_rof=False, degree_type__ROF_code='EA')
    return trainings


@user_passes_test(lambda u: True if 'DIRETU' or 'GESCOL' or 'RESPFORM' in [e.code for e in u.meccuser.profile.all()] else False)
def documents_institute(request, code, template='institute/documents.html'):
    """
    Show documents relative to Institute
    """
    data = {}
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    institute = Institute.objects.get(code=code)
    # institute_year = InstituteYear.objects.get(
    #    id_cmp=institute.id, code_year=current_year.code_year)
    data['label_cmp'] = institute.label
    data['letter_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='letter_%s/%s' % (current_year.code_year, current_year.code_year + 1))
    data['misc_file'] = FileUpload.objects.filter(
        object_id=institute.id, additional_type='misc_%s/%s' % (current_year.code_year, current_year.code_year + 1))
    trainings = Training.objects.filter(
        is_used=True,
        code_year=current_year.code_year,
        supply_cmp=institute.code,
    ).prefetch_related(
        'degree_type',
    ).order_by(
        'degree_type__display_order',
        'label',
    )
    data['published_meccs'] = trainings
    data['current_year'] = current_year

    return render(request, template, data)


@login_required()
def published_meccs_for_institute_and_year(request, year, institute):
    uy = UniversityYear.objects.get(code_year=year)
    trainings = Training.objects.filter(
        is_used=True,
        code_year=year,
        supply_cmp=institute,
    ).prefetch_related(
        'degree_type',
    ).order_by(
        'degree_type__display_order',
        'label',
    )
    html = render_to_string('institute/modal/published_meccs.html', {'published_meccs': trainings, 'current_year': uy})
    return JsonResponse({'html': html}, content_type='application/json')



@is_post_request
@login_required
def send_mail(request):
    """
    Send mail (TO DES)
    """

    meccuser = MeccUser.objects.get(user__username=request.user.username)
    current_year = list(UniversityYear.objects.filter(
        Q(is_target_year=True))).pop(0)
    code = meccuser.cmp
    institute = Institute.objects.get(code=code)
    institute_year = InstituteYear.objects.get(
        id_cmp=institute.id, code_year=current_year.code_year)
    institute_year.date_last_notif = datetime.now()
    institute_year.save()
    to = settings.EMAIL_TEST if hasattr(
        settings, 'EMAIL_TEST') else ['']
    cc = request.POST.get('cc').split(',') if request.POST.get('cc') else ''
    subject = "%s %s - %s %s" % (settings.EMAIL_SUBJECT_PREFIX,
                                 institute.label,
                                 request.user.first_name,
                                 request.user.last_name)

    body = request.POST.get('body')

    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email="%s %s <%s> " % (
            request.user.first_name,
            request.user.last_name,
            request.user.email),
        to=[settings.MAIL_FROM],
        cc=cc,
        bcc=to
    )

    mail.send()
    messages.success(request, _('Notification envoyée.'))
    return redirect('/institute/validate/%s' % code)


@is_post_request
@login_required
def send_mail_des(request):
    """
    Send mail (from DES)
    """

    to = settings.EMAIL_TEST if hasattr(
        settings, 'EMAIL_TEST') else ''
    cc = request.POST.get('cc').split(',') if request.POST.get('cc') else ''
    subject = request.POST.get('subject')

    body = request.POST.get('body')
    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email="%s %s <%s> " % (
            request.user.first_name,
            request.user.last_name,
            request.user.email),
        to=request.POST.get('to').split(','),
        cc=cc,
        bcc=to,
        reply_to=[settings.MAIL_FROM]
    )

    mail.send()
    messages.success(request, _('Notification envoyée.'))
    return redirect('/institute/checkvalidate/%s' % request.session['visited_cmp'])


@is_post_request
@login_required
def process_upload_letter(request):
    """
        TODO: use a meccuser instance not to duplicate code !!!!
    """
    meccuser = MeccUser.objects.get(user__username=request.user.username)
    code = meccuser.cmp
    return redirect('/institute/validate/%s' % code)


@is_post_request
@login_required
def process_upload_misc(request):
    """
        TODO: use a meccuser instance not to duplicate code !!!!
    """
    meccuser = MeccUser.objects.get(user__username=request.user.username)
    code = meccuser.cmp
    return redirect('/institute/validate/%s' % code)


@is_post_request
@login_required
def process_delete_file(request):
    """
        TODO: use a meccuser instance not to duplicate code !!!!
    """
    meccuser = MeccUser.objects.get(user__username=request.user.username)
    code = meccuser.cmp
    return redirect('/institute/validate/%s' % code)


@group_required('DES1', 'DES2', 'DES3')
@is_post_request
@login_required
def process_check_validate(request):
    tobject = Training.objects.get(id=request.POST.get('code'))
    type = request.POST.get('type')

    if type == 'remove_cfvu':
        tobject.date_val_cfvu = None
    if type == 'remove_visa':
        tobject.date_visa_des = None
    if type == 'remove_reserve':
        tobject.date_res_des = None
    if type == 'remove_validation':
        tobject.date_val_cmp = None
    if type == 'add_visa':
        tobject.date_visa_des = datetime.now()
        tobject.date_res_des = None
    if type == 'add_reserve':
        tobject.date_res_des = datetime.now()
        tobject.date_visa_des = None

    if tobject:
        tobject.save()
        # response = {'status': 1, 'message': _(
        #     "Ok"), 'url': '/institute/checkvalidate/%s' % request.session['visited_cmp']}
        return render(
            request,
            'institute/check_validate_training_list_item.html',
            {'training': tobject}
        )
    else:
        response = {'status': 0, 'message': _("Error")}
        return HttpResponse(json.dumps(response), content_type='application/json')


@is_post_request
@login_required
def process_training_notify(request):
    tobject = Training.objects.get(id=request.POST.get('code'))

    if tobject:
        respform = User.objects.filter(
            meccuser__id__in=tobject.resp_formations.values('id'))
        response = {'status': 1, 'message': _(
            "Ok"), 'url': '/institute/checkvalidate/%s' % request.session['visited_cmp'], 'form': tobject.label, 'resp': list(respform.values('email'))}
    else:
        response = {'status': 0, 'message': _("Error")}

    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
@is_ajax_request
def details_files(request):

    current_year = currentyear().code_year
    cmp = request.POST.get('val')
    institute = Institute.objects.get(id=cmp)
    files = FileUpload.objects.filter(
        object_id=cmp,
        additional_type='misc_%s/%s' % (current_year, current_year + 1)
    )

    f_data = []
    for f in files:
        a = {
            'url': f.file.url,
            'name': f.filename(),
            'comment': f.comment,
            'creator': f.creator.get_full_name(),
            'uploaded_at': formats.date_format(f.uploaded_at.date(), "SHORT_DATE_FORMAT")
        }
        f_data.append(a)
    # list(files.values('file', 'creator', 'uploaded_at')),
    json_response = {
        'files': f_data if len(f_data) > 0 else 0,
        'institute': institute.label
    }

    return JsonResponse(json_response)
