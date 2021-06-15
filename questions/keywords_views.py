import requests
from django.conf import settings
from django.contrib import messages

from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage, send_mail
from django.http import Http404
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.db.models import F, Count, Q
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

from collections import OrderedDict
from .keywords_models import Keywords
from .keywords_serializers import KeyWordsSerializer, CategorySerializer

from .models import Category,Question

from collectanea.permission import AuthorizedPermission

from datetime import date,datetime
import math

class AddKeyword(APIView):
    """
    add a new and different Keyword
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            key=Keywords.objects.filter(name=name)
            if key.exists():
                respone = {
                    'message': 'Keyword Already Exists',
                    'body': [],
                    'status': HTTP_200_OK
                }
                return Response(respone, status=HTTP_200_OK)

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

    # permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')

        keywords_list = Keywords.objects.filter(Q(name__icontains=text)).order_by('-created_at')

        data = KeyWordsSerializer(keywords_list, many=True).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
        
class SearchCategory(APIView):
    """
    search keyword on the basis of an input text.
    """

    # permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        print(text)
        category_list = Category.objects.filter(Q(name__icontains=text),status='Active').order_by('-created_at')
        print(category_list)
        data = CategorySerializer(category_list, many=True).data
        print(data)
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

    # permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(status='Active').order_by('-created_at')

        data = CategorySerializer(categories, many=True).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class getPopularKeyword(APIView):
    # permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):

        keywords_list = Keywords.objects.all().order_by('-created_at')
        print(keywords_list)
        all_keys=[]
        z_scores = {}
        for keyword in keywords_list:
            # print(keyword.id,"A")
            var=keyword.associatedKeywords.all().order_by('-created_at')

            days={}
            obj=var.values_list("created_at")
            for dt in obj:
                if dt[0].date() not in days:
                    days[dt[0].date()]=0 
            for key_obj in var:
                days[key_obj.created_at.date()]+=1

            print(days)
            use_count=var.count()
            if use_count:
                date_today = datetime.now(timezone.utc)
                created_at = keyword.created_at
                most_recent_used = var.latest('created_at').created_at
                days_created_before = date_today-created_at
                days_created_before = int(days_created_before.days)
                not_used_days = days_created_before - len(days.keys())
                if days_created_before>0:
                    avg_trend = int(use_count)/(days_created_before)
                else:
                    avg_trend = int(use_count)
                # print(keyword.id,"A")
                std_deviation = sum(((int(c) - avg_trend) ** 2) for c in days.values())
                std_deviation += (((0-avg_trend)**2) * (not_used_days))
                print
                if days_created_before>0:
                    standard_deviation = math.sqrt(abs(std_deviation) / (days_created_before))
                else:
                    standard_deviation = math.sqrt(abs(std_deviation))

                standard_deviation = -1*standard_deviation if std_deviation<0 else standard_deviation
                # print(most_recent_used)
                if most_recent_used-date_today == 0:            
                    current_trend =int(use_count)
                else:
                    current_trend=0

                standard_deviation = 1 if standard_deviation==0 else standard_deviation
                z_score = (current_trend-avg_trend)/standard_deviation
                # print(keyword.id,"A")
                z_scores[keyword.id] = z_score
        print(z_scores)
        sorted_words = OrderedDict(sorted(z_scores.items(), key = lambda kv:kv[1], reverse=True))
        
        print(sorted_words)
        for ob in sorted_words:
            keyw_obj=Keywords.objects.filter(id=ob).first()
            all_keys.append(keyw_obj)




        data = KeyWordsSerializer(all_keys, many=True).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)