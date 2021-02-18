from django.core.exceptions import ValidationError
from accounts.models import User, Profile

def check_user_status(user):
    """
    raise an error when user is Blocked or Deleted.
    """

    if user.status != 'Activated':
        raise ValidationError("User is {}".format(user.status))

# def user_is_active(function, *fargs, **args):
# 	def wrapper(*args, s_id):
# 		print(*args)
# 		print(args.user.id)
# 		profile = Profile.objects.filter(id = args.user.id)
# 		user = User.objects.filter(id = profile.user)
# 		if user.is_active:
# 			return function()
# 	return wrapper

def user_is_active(request):
	if request.user.is_active:
		return True