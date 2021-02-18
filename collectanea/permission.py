from rest_framework.permissions import BasePermission

class AuthorizedPermission(BasePermission):
    """
    Global permission check for  deleted or blocked.
    """

    message = "User is not authorized to perform this request."

    def has_permission(self, request, view):
        try:
            user = request.user
            if user.status == 'Activated':
                return True
            return False
        except:
            return False