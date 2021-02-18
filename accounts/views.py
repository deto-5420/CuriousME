import random
import string
# import stripe 
import requests

from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.views import APIView
from collectanea.globals import (USER_STATUS, STRIPE_RETURN_URL,
                                STRIPE_REFRESH_URL)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Profile, User, ProfessionList
from .serializers import (
                            ForgotPasswordEmailSerializer,
                            RegistrationSerializer, SetNewPasswordSerializer
                    )

from .profile_serializer import (
                        ProfileSerializer,
                    )

from .tokens import account_activation_token


@api_view(['POST',])
def register_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        username = request.data.get('username')

        check_user = User.objects.filter(email=email).first()
        check_username = User.objects.filter(username__iexact=username).first()

        if check_user and not check_user.is_active:
            check_user.delete()
            check_username = ''
        
        if check_username:
            response = {
                'message':'SignUp failed !!',
                'error':['Username is already taken'],
                'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        if len(username.strip().split(" "))>1:
            response = {
                'message':'SignUp failed !!',
                'error':['Username cannot contain spaces.'],
                'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        print(request.data)
        serializer = RegistrationSerializer(data = request.data)
        print(serializer)
        if serializer.is_valid():
            account = serializer.save()
            print(account)
            fullname = request.data.get('fullname')
            profes = request.data.get('profession')

            try:
               profession = ProfessionList.objects.filter(Q(name__icontains = profes) | Q(id=profes)).first()
            except:
                response = {
                    'message':'Profession not available',
                    'error':["Profile couldn't be created"],
                    'status':HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)
            
            Profile.objects.create(user=account, fullname=fullname, profession=profession)

            current_site = get_current_site(request)
            mail_subject = '[noreply] Activate your Account'
            msg = 'Thanks for Signing up with Collectanea.'

            message = render_to_string('acc_email_active.html', {
                'user': account,
                'domain': current_site.domain,
                'msg':msg,
                'uid':urlsafe_base64_encode(force_bytes(account.pk)),
                'token':account_activation_token.make_token(account),
            })

            to_email = [account.email]
            # from_email = settings.SENDER_EMAIL
            from_email = ''
            email = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=mail_subject,
                html_content=message,
            )
            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(email)
            except Exception as e:
                response = {
                    'message':'User Registration failed',
                    'error':["Mail not sent"],
                    'status':HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            response = {
                'message':'User registered successfully, Please verify your accoumt using the link sent via email',
                'body':[],
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)

        else:
            response = {
                'message':'User Registration failed',
                'error':serializer.errors,
                'status':HTTP_401_UNAUTHORIZED
            }
        return Response(response, status=HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        email = user.email

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        email=None

    if user is not None and account_activation_token.check_token(user, token):
        profile = user.userAssociated.all().first()

        # stripe.api_key = settings.STRIPE_API_KEY

        # try:
        #     account = stripe.Account.create(
        #         country="US",
        #         type='custom',
        #         email=profile.user.email,
        #         requested_capabilities=['transfers', 'card_payments'],
        #         business_type='individual',
        #         settings={
        #             "payouts": {
        #                 "schedule": {
        #                     "interval": "manual"
        #                 }
        #             }
        #         }
        #     )

        #     profile.stripe_id = account['id']
        #     profile.save()

        #     account_link = stripe.AccountLink.create(
        #         account=account['id'],
        #         refresh_url=STRIPE_REFRESH_URL,
        #         return_url=STRIPE_RETURN_URL,
        #         type="account_onboarding",
        #     )
        
        # except Exception as e:
        #     response = {
        #         'message': 'Activation Failed',
        #         'error': str(e),
        #         'status': HTTP_400_BAD_REQUEST
        #     }
        #     return Response(response, status=HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        response = {
                'message':'Account Activation done',
                'body': {
                    # 'stripe_verification': account_link['url'],
                    # 'expires_at': account_link['expires_at'],
                },
                'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

    else:
        if user and not user.is_active:
            User.objects.filter(email=email).delete()
        response = {
                'message':'Account activation failed',
                'error':['Token expired'],
                'status':HTTP_401_UNAUTHORIZED
            }
        return Response(response, status=HTTP_401_UNAUTHORIZED)

@api_view(['POST',])
def login_user(request):
    if request.method == 'POST':
        email = password = ''
        email = request.data['email']
        password = request.data['password']
        print(email, password)
        user = authenticate(email=email, password=password)
        obj = User.objects.filter(email=email).first()

        if obj is None:
            message = "You do not have an account please signup to continue."
            response = {
                'message': 'Login Failed',
                'error': [message],
                'status':HTTP_401_UNAUTHORIZED
            }
            return Response(response, status=HTTP_401_UNAUTHORIZED)

        elif user is None:
            message = "Invalid Password !!"
            response = {
                'message': 'Login Failed',
                'error':[message],
                'status':HTTP_401_UNAUTHORIZED
            }
            return Response(response, status=HTTP_401_UNAUTHORIZED)

        elif user.status == 'Blocked' or user.status == 'Deleted':
            message = "Your Account is {}".format(user.status)
            response = {
                'message': 'Login Failed',
                'error': [message],
                'status':HTTP_401_UNAUTHORIZED
            }
            return Response(response, status=HTTP_401_UNAUTHORIZED)

        elif user.is_active:
            try:
                token = Token.objects.get(user=user).key
                if token is None:
                    raise Http404
            except:
                response = {
                    'message':'Login Failed !!',
                    'error':['Token does not exist'],
                    'status':HTTP_401_UNAUTHORIZED
                }
                return Response(response, status=HTTP_401_UNAUTHORIZED)

            profile = user.userAssociated.all().first()
            data = ProfileSerializer(profile).data
            data['token'] = token

            response = {
                'message':'Login successfull.',
                'body':data,
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)

        else:
            message = "Your account is not yet activated, please click on the activation link sent on your email or Signup again."
            response = {
                'message': 'Login Failed',
                'error':[message],
                'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

class PasswordResetEmail(APIView):
    serializer_class = ForgotPasswordEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        email = request.data['email']
        user = User.objects.filter(email=email).first()
        if user:
            print(user.status)
            if user.status == 'Blocked' or user.status == 'Deleted':
                message = "Your Account is {}".format(user.status)
                response = {
                    'message': 'Failed',
                    'error': [message],
                    'status':HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            current_site = get_current_site(request)
            mail_subject = '[noreply] Reset your Password'
            msg = 'You will be redirected to the password reset page.'

            message = render_to_string('password_reset_link.html', {
                'user': user,
                'domain': current_site.domain,
                'msg':msg,
                'uid':uidb64,
                'token':token,
            })

            to_email = [user.email]
            from_email = settings.SENDER_EMAIL

            email = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=mail_subject,
                html_content=message,
            )
            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(email)
            except Exception as e:
                response = {
                    'message':'User Registration failed',
                    'error': [e],
                    'status':HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            response = {
                "message":"Password reset link sent on your mail.",
                "body": [],
                "status":HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)

        else:
            response = {
                "message": "Password reset Failed",
                "error":"Enter Correct email",
                "status":HTTP_400_BAD_REQUEST
            }
        
        return Response(response, status=HTTP_400_BAD_REQUEST)

class PasswordTokenCheck(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            email = user.email

        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            email=None

        if user is not None:
            if PasswordResetTokenGenerator().check_token(user, token):
                response = {
                    'message':'Credentials Verified',
                    'success':True,
                    'token':token,
                    'uidb64':uidb64,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

            return Response({
                'message': "Failed",
                'error':['Token expired'],
                'status':HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

        else:      
            response = {
                    'message':'Password Reset Failed !!',
                    'error':['error'],
                    'status':HTTP_400_BAD_REQUEST
                }
            return Response(response, status=HTTP_400_BAD_REQUEST)

class SetNewPassword(APIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'success':True,
            'message':'Password reset Successful.',
            'status':HTTP_200_OK
        }, status=HTTP_200_OK)

class ChangePassword(APIView):
    permission_classes=(IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        user = self.request.user

        if user.status == 'Blocked' or user.status == 'Deleted':
            message = "Your Account is {}".format(user.status)
            response = {
                'message': 'Password was not changed',
                'error': [message],
                'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            response = {
                    'message':'Password was not changed',
                    'error':['Old Passowrd is wrong, Please enter correct password.'],
                    'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            response = {
                    'message':'Password was not changed',
                    'error':['new password and confirm password are different'],
                    'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        if new_password == old_password:
            response = {
                    'message':'Password was not changed',
                    'error':['new password and old password are same, please enter a different password.'],
                    'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            response = {
                    'message':'Password was not changed',
                    'error':['Password too short, password length must me between 8 to 16 characters.'],
                    'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        response = {
            'message':'Password changed Successfully',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class DeleteAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        current_password = request.data.get('current_password')
        confirm_password = request.data.get('confirm_password')
        
        user = self.request.user
        profile = user.userAssociated.all().first()
        
        if not user.check_password(current_password):
            response = {
                'message':'Account deletion failed !!',
                'error':['Passowrd is wrong, Please enter correct password.'],
                'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        if current_password != confirm_password:
            response = {
                    'message':'Account deletion failed !!',
                    'error':["Passowrds didn't match, Please enter correct password."],
                    'status':HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        user.status = 'Deleted'
        user.save()
        user.refresh_from_db()

        token = Token.objects.get(user=user).delete()

        response = {
            'message':'Account Deleted Successfully.',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
