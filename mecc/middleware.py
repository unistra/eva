from django.contrib.auth.models import User


class UsefullDisplay(object):

    def process_request(self, request):
        # always sent real user in order e.g. to display last first name
        if request.session.get('is_spoofed_user'):
            u = User.objects.get(username=request.session['real_username'])
        else:
            u = request.user
        request.display = {'user': u}

    def process_response(self, request, response):
        return response
