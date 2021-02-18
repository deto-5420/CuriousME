import requests
from django.conf import settings
from django.contrib import messages

from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
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
                                   HTTP_401_UNAUTHORIZED, HTTP_411_LENGTH_REQUIRED)
from rest_framework.views import APIView
from collectanea.globals import USER_STATUS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Profile, User
from .profile_serializer import ProfileSerializer, ViewProfileSerializer
from .tokens import account_activation_token
from questions.keywords_models import Keywords

from collectanea.permission import AuthorizedPermission
from .validators import username_validator, bio_validator, avatar_validator
from collectanea.global_checks import check_user_status

class UpdateInterests(APIView):
    """
    update profile interests
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def patch(self, request, *args, **kwargs):
        keywords = request.data.getlist('keyword')

        user = self.request.user
        profile = user.userAssociated.all().first()

        profile.MyInterest.clear()

        for i in range(len(keywords)):
            try:
                keyword = get_object_or_404(Keywords, pk=int(keywords[i]))
                profile.MyInterest.add(keyword)
                profile.save()
            except:
                response = {
                    'message': 'Invalid Keyword Id',
                    'error': ['ID {} does not exist'.format(keywords[i])],
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)
        
        response = {
            'message': 'Interests updated successfully',
            'body':str([]),
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetMyProfile(APIView):
    """
    Get profile details 
    NOTE: their are some info that needs to be fetched from the stripe server.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated.all().first()

        data = ProfileSerializer(profile).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class EditProfile(APIView):
    """
    Edit username, fullname, country, bio and Profile_image
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        fullname = request.data.get('fullname')
        # country = request.data.get('country')
        bio = request.data.get('bio')
        # print(bio)
        user = self.request.user
        print(user)
        # profile = user.userAssociated.all().first()
        profile = Profile.objects.get(user = user)
        check_username = Profile.objects.filter(user__username = username).exclude(user=user)
        # print(check_username)
        if check_username:
            response = {
                'message': 'Failed',
                'error': ['Username already exists'],
                'status': HTTP_400_BAD_REQUEST 
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:
            username_validator(username)
            print(username_validator(username))
            bio_validator(bio)
            print(bio_validator(bio))

            profile.user.username = username
            profile.user.fullname = fullname
            profile.bio = bio

            if avatar is not None:
                avatar_validator(avatar)
                profile.avatar = avatar

            profile.user.save()
            profile.save()

        except Exception as e:
            response = {
                'message': 'Failed',
                'error': e,
                'status': HTTP_400_BAD_REQUEST 
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        response = {
            'message': 'Profile updated successfully',
            'body': [],
            'status': HTTP_200_OK 
        }
        return Response(response, status=HTTP_200_OK)

class GetUserProfile(APIView):
    """
    get user profile by userID
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        userID = request.data.get('userID')
        user = self.request.user
        logged_profile = user.userAssociated.all().first()

        try:
            userID = int(userID)
            profile = get_object_or_404(Profile, pk=userID)

            if logged_profile.pk == userID:
                raise HTTPError

        except:
            response = {
                'message': 'Invalid Request',
                'error': [
                    'Invalid UserID'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:
            check_user_status(profile.user)
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
    
        data = ViewProfileSerializer(profile).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
