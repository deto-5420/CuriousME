from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        if request.user.is_moderator:
            path = "/moderator/"
        elif request.user.is_staff:
            path = "/adminpanel/"
        elif request.user.is_admin:
            path = "/adminpanel/"
        else:
            path = "/"

        return path
    
    def get_logout_redirect_url(self, request):
        if request.user.is_moderator:
            path = "/moderator/login/"
        elif request.user.is_staff:
            path = "/adminpanel/logout/"
        elif request.user.is_admin:
            path = "/adminpanel/logout/"
        else:
            path = "/"

        return path