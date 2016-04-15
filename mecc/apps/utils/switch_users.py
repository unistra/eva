from django.contrib.auth import login, load_backend, BACKEND_SESSION_KEY
from django.contrib.auth.models import User


def request_with_other_user(request, user):
    """
    Return request with necessary backend and logged as asked user
    """
    backend_str = request.session[BACKEND_SESSION_KEY]
    backend = load_backend(backend_str)
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    login(request, user)
    return request


def check_generic_password(raw_password):
    """
    Get or create user, if created the generic password will be the one entered.
    Return true if raw_password is correct.
    """
    gen_user, created = User.objects.get_or_create(username='DES3')
    if created:
        gen_user.set_password(raw_password)
        gen_user.save()
    return gen_user.check_password(raw_password)
