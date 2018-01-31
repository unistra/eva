def sidebar(request):
    context = {}
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

                if e.code in level_3 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_3]:
                    new_p.append(e)

                if e.code in level_1 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_1]:
                    new_p.append(e)

        context['profiles'] = new_p
        if 'DIRCOMP' in [e.code for e in profiles]:
            context['dircomp'] = True
        if 'RESPENS' in [e.code for e in profiles]:
            context['is_respens'] = True

    return context
