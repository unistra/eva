def sidebar(request):
    context = {}
    if request.user.is_superuser:
        pass
    else:
        profiles = request.user.meccuser.profile.all()
        context['profiles'] = profiles
        if 'DIRCOMP' in [e.code for e in profiles]:
            context['dircomp'] = True

    return context
