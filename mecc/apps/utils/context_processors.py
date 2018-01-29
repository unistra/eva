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
        perms = {}
        for e in profiles:
            if (e.code, e.cmp) not in [(e.code, e.cmp) for e in new_p]:
                if e.code in level_2 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_2]:
                    # try:
                    #     perms[e.code].append('level_2')
                    # except Exception as ex:
                    #     print(ex)
                    #     perms[e.cmp] = ['level_2']
                    new_p.append(e)
                if e.code in level_3 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_3]:
                    # try:
                    #     perms[e.code].append('level_3')
                    # except Exception as ex:
                    #     print(ex)
                    #     perms[e.cmp] = ['level_3']
                    new_p.append(e)
                if e.code in level_1 and e.cmp not in [
                        e.cmp for e in new_p if e.code in level_1]:
                    # try:
                    #     perms[e.code].append('level_1')
                    # except Exception as ex:
                    #     print(ex)

                    #     perms[e.cmp] = ['level_1']
                    new_p.append(e)

        level_1 += level_2 + level_3
        level_2 += level_3
        # for e in new_p:
        #     print(e.cmp)
        #     if e.code in level_1 and e.cmp not in perms:
        #         perms.append(e.code)
        # print(perms)
        # print(new_p)
        context['profiles'] = new_p
        # context['perms'] = perms
        # print([(e.code, e.cmp) for e in profiles])
        if 'DIRCOMP' in [e.code for e in profiles]:
            context['dircomp'] = True
        if 'RESPENS' in [e.code for e in profiles]:
            context['is_respens'] = True

    return context
