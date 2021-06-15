from django.urls import path,include

from .views import (
                register_user, PasswordResetEmail, login_user,
                PasswordTokenCheck, SetNewPassword, ChangePassword,
                DeleteAccount, activate
            )

from .profile_views import (
                UpdateInterests, GetMyProfile, EditProfile,
                GetUserProfile, AddUpdateUrl, DeleteWebUrl, GetFollowersList, GetFollowingsList, ToggleFollowingView, getPopularUsers
            )

from .social_views import (
                FacebookLogin, GoogleLogin,TwitterLogin
            )

app_name = 'accounts'

urlpatterns = [
    # Authentication APIs
    path('signup/', register_user, name="registerNewUser"),
    path('login/', login_user, name="LoginView"),
    path('activate/<slug:uidb64>/<slug:token>/', activate, name='ActivateUser'),
    path('request-password-reset/', PasswordResetEmail.as_view(), name="SendPasswordResetEmail"),
    path('password-reset/<slug:uidb64>/<slug:token>/', PasswordTokenCheck.as_view(), name="PasswordResetConfirm"),
    path('password-reset-complete/',SetNewPassword.as_view(), name="PasswordResetComplete"),
    path('change-password/', ChangePassword.as_view(), name="ChangePassword"),

    # Social login
    path('social/facebook/', FacebookLogin.as_view(), name='socialaccount_signup_facebook'),
    path('social/google/', GoogleLogin.as_view(), name='socialaccount_signup_google'),
    path('social/twitter/', TwitterLogin.as_view(), name='socialaccount_signup_twitter'),
    path('social/rest-auth/login/', FacebookLogin.as_view(), name='authorize'),

    # Delete Account
    path('delete-account/', DeleteAccount.as_view(), name="DeleteAccount"),

    # Profile urls
    path('update-interests/', UpdateInterests.as_view(), name="UpdateInterests"),
    path('get-my-profile/', GetMyProfile.as_view(), name="GetMyProfile"),
    path('edit-profile/', EditProfile.as_view(), name="EditProfile"),
    path('get-user-profile/', GetUserProfile.as_view(), name="GetUserProfile"),
    path('add-update-url/', AddUpdateUrl.as_view(), name="AddUpdateUrl"),
    path('delete-web-profile/', DeleteWebUrl.as_view(), name="DeleteWebUrl"),
    path('get-followers-list/', GetFollowersList.as_view(), name="GetFollowersList"),
    path('get-followings-list/', GetFollowingsList.as_view(), name="GetFollowingsList"),
    path('toggle-following-view/', ToggleFollowingView.as_view(), name="GetFollowingsList"),
    path('get-Popular-Users/', getPopularUsers.as_view(), name="getPopularUsers")


]