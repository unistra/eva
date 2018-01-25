from django.contrib.auth.models import User
from mecc.apps.years.models import UniversityYear


class UsefullDisplay(object):

    def process_request(self, request):
        # always sent real user in order e.g. to display last first name
        if request.session.get('is_spoofed_user'):
            u = User.objects.get(username=request.session['real_username'])
        else:
            u = request.user
        request.display = {'user': u}

        # give current year
        y = UniversityYear.objects.filter(is_target_year=True).first()
        c = "%s/%s" % (y.code_year, y.code_year + 1) if y is not None else ":\
            aucune année selectionnée"
        request.display.update({'current_year': c})

    def process_response(self, request, response):
        return response
