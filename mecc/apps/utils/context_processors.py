from mecc.apps.utils.queries import currentyear
from mecc.apps.years.models import UniversityYear
from django.core.exceptions import ObjectDoesNotExist


def sidebar(request):
    context = {}
    try:
        target_year = UniversityYear.objects.get(is_target_year=True)
        current_year = target_year.code_year
    except ObjectDoesNotExist:
        pass
    if request.user.is_superuser:
        pass
    else:
        profiles = request.user.meccuser.profile.all()
        new_p = []
        level_1 = ['DIRCOMP', 'RAC', 'REFAPP']
        level_2 = ['DIRETU', 'GESCOL']
        level_3 = ['RESPFORM', 'RESPENS']
        for e in profiles:
            if (e.code, e.cmp) not in [(e.code, e.cmp) for e in new_p]:
                if e.code in level_2 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_2]:
                    new_p.append(e)

                if e.code in level_3 \
                        and e.cmp not in [
                            e.cmp for e in new_p if e.code in level_3] \
                        and e.year == current_year:
                    new_p.append(e)

                if e.code in level_1 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_1]:
                    new_p.append(e)

        context['profiles'] = new_p
        if 'DIRCOMP' in [e.code for e in profiles]:
            context['dircomp'] = True
        if 'RESPENS' in [e.code for e in profiles] and current_year in [e.year for e in profiles]:
            context['is_respens'] = True
    return context
