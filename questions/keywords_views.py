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
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.views import APIView
from collectanea.globals import USER_STATUS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .keywords_models import Keywords
from .keywords_serializers import KeyWordsSerializer, CategorySerializer

from .models import Category

from collectanea.permission import AuthorizedPermission


class AddKeyword(APIView):
    """
    add a new Keyword
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')

            Keywords.objects.create(name=name)

            respone = {
                'message': 'Keyword added successfully',
                'body': [],
                'status': HTTP_200_OK
            }
            return Response(respone, status=HTTP_200_OK)
        except Exception as e:
            respone = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(respone, status=HTTP_400_BAD_REQUEST)

class SearchKeywords(APIView):
    """
    search keyword on the basis of an input text.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        text = request.data.get('text')

        keywords_list = Keywords.objects.filter(name__icontains=text).order_by('-created_at')

        data = KeyWordsSerializer(keywords_list, many=True).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetCategories(APIView):
    """
    get all categories sorted by created date.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(status='Active').order_by('-created_at')

        data = CategorySerializer(categories, many=True).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)