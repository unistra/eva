def sidebar(request):
    context = {}
    if request.user.is_superuser:
        pass
    else:
        context['profiles'] = request.user.meccuser.profile.all()

    return context
