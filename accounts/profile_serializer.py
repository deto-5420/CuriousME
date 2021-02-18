from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,Http404
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.hashers import check_password

import json

from .tokens import account_activation_token
from .models import User, Profile, Websites
from questions.keywords_serializers import KeyWordsSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'status', 'signup_time']

class WebsitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Websites
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    userID = serializers.SerializerMethodField()
    MyInterest = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [  'userID',
                    'user', 
                    'fullname', 
                    'email', 
                    'bio', 
                    'MyInterest', 
                    'avatar',
                    'websites',
                    'profession',
                ]
        
    def get_user(self, obj):
        return UserSerializer(obj.username).data
    
    def get_userID(self, obj):
        return obj.pk

    def get_avatar(self, obj):
        try:
            return obj.avatar.url
        except:
            return ''

    def get_websites(self, obj):
        keywords = obj.websites.all()
        data = WebsitesSerializer(keywords, many=True).data
        return data

    def get_MyInterest(self, obj):
        keywords = obj.MyInterest.all()
        data = KeyWordsSerializer(keywords, many=True).data
        return data

class ViewProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    userID = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [  'user', 
                    'userID', 
                    'fullname', 
                    'bio', 
                    'avatar',
                ]
        
    def get_user(self, obj):
        return UserSerializer(obj.user).data
    
    def get_userID(self, obj):
        return obj.pk

    def get_avatar(self, obj):
        try:
            return obj.avatar.url
        except:
            return ''
