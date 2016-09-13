def sidebar(request):
    context = {}
    if request.user.is_superuser:
        print('helo')
    else:
        context['profiles'] = request.user.meccuser.profile.all()

    return context
