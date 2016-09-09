from django.http import HttpResponseForbidden
from django.shortcuts import redirect

class CanUdoIt(object):
    """
Check if user can do what he's going to do according to this table :

                    SU	DIRCOMP	RAC	REFAPP	GESCOL	DIRETU	RESPFORM		DES1	DES2	DES3
COMPOSANTES Read		Y	   Y	 Y	   Y	   Y	   Y	    Y		      N      N	     N
COMPOSANTES Write		Y	   Y	 Y	   Y	   N	   N	    N		      N      N	     N

FORMATIONS Read 		Y	   Y	 Y	   Y	   Y	   Y	    N		      Y      N	     N
FORMATIONS Write 		Y	   Y	 Y	   Y	   Y	   Y	    N		      Y      N	     N


MES FORMATIONS		    N	   N	 N	   N	   N	   N	    Y		      N      N	     N
Moteur de gen des MECCS	Y	   Y	 Y	   Y	   Y	   Y	    N		      Y      N	     N

REGLES Read		        Y	   N	 N	   N	   N	   N	    N		      Y      N	     N
REGLES Write		    Y	   N	 N	   N	   N	   N	    N		      Y      N	     N

TYPES DIPLOMES Read		Y	   N	 N	   N	   N	   N	    N		      Y      Y	     N
TYPES DIPLOMES Write	Y	   N	 N	   N	   N	   N	    N		      Y      Y	     N

ANNEES Read		        Y	   N	 N	   N	   N	   N	    N		      Y      N	     N
ANNEES Write		    Y	   N	 N	   N	   N	   N	    N		      Y      N	     N

COMMISSION ECI Read		Y	   N	 N	   N	   N	   N	    N		      Y      N	     N
COMMISSION ECI Wirte	Y	   N	 N	   N	   N	   N	    N		      Y      N	     N

USURPATION D'IDENTITÉ	Y	   N	 N	   N	   N	   N	    N		      N      N	     Y



ADMINISTRATION		    Y	   N	 N	   N	   N	   N	    N		      N	     N	     N
"""

    def process_request(self, request):
        authorized = False
        if "/" == request.path or request.path in '/spoof/release/':
            authorized = True
        print(request.user)
        print(request.path)

        unauthorized = HttpResponseForbidden("<h1>Forbidden</h1>You cannot \
        access this page.")
        if request.user.is_superuser:
            authorized = True


        # User does no exist !
        # print(dir(request))
        # if not hasattr(request, 'user') and 'accounts' not in request.path:
        #     print('************************************************')
        #     return unauthorized
        # if request.user.is_superuser:
        #     return response
        #
        # if 'institute/granted' in request.path:
        #     print(request.user.meccuser.profile.all())
        #     return response
        # print(request.path)

        return None if authorized else unauthorized

    def process_response(self, request, response):
        return response
