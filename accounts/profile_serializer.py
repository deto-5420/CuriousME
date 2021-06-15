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
from .models import User, Profile, Websites,UserFollowing,ProfessionList
from collectanea.globals import *
from questions.keywords_serializers import KeyWordsSerializer
from rest_framework.authtoken.models import Token

class MyInterestSerializer(serializers.Serializer):
    id=serializers.SerializerMethodField()
    name=serializers.SerializerMethodField()
    def get_id(self,obj):
        return obj.id
    def get_name(self,obj):
        return obj.name

class UserSerializer(serializers.ModelSerializer):
    role=serializers.SerializerMethodField()
    fullname=serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['email', 'username', 'status','role','fullname']  #, 'signup_time'

    def get_fullname(self,obj):
        return Profile.objects.get(user=obj).fullname
    def get_role(self,obj):
        var=obj
        if var.is_admin:
            return "Admin"
        elif var.is_moderator:
            return "Moderator"
        else:
            return "User"
            
class FollowingDetailSerializer(serializers.Serializer):
    username=serializers.SerializerMethodField()
    userID=serializers.SerializerMethodField()
    profileURL=serializers.SerializerMethodField()
    role=serializers.SerializerMethodField()
    bio=serializers.SerializerMethodField()
    is_following=serializers.SerializerMethodField()
    def get_username(self,obj):
        return obj.following_user_id.user.username
    def get_userID(self,obj):
        return obj.following_user_id.user.id
    def get_bio(self,obj):
        return obj.following_user_id.bio
    def get_profileURL(self,obj):
        try:
            return obj.following_user_id.avatar.url
        except:
            return ""

        # if obj.following_user_id.websites.all():
        #     return list(map(lambda ob: (ob.key,ob.pair),obj.following_user_id.websites.all()))
        # else:
        #     return None

    def get_role(self,obj):
        var=obj.following_user_id.user
        if var.is_admin:
            return "Admin"
        elif var.is_moderator:
            return "Moderator"
        else:
            return "User"
    def get_is_following(self,obj):
        if UserFollowing.objects.filter(user_id=obj.following_user_id,following_user_id=obj.user_id).exists():
            return True
        return False
class FollowerDetailSerializer(serializers.Serializer):
    username=serializers.SerializerMethodField()
    userID=serializers.SerializerMethodField()
    profileURL=serializers.SerializerMethodField()
    role=serializers.SerializerMethodField()
    bio=serializers.SerializerMethodField()
    is_follower=serializers.SerializerMethodField()
    def get_username(self,obj):
        return obj.user_id.user.username
    def get_userID(self,obj):
        return obj.user_id.user.id
    def get_bio(self,obj):
        return obj.user_id.bio
    def get_profileURL(self,obj):
        try:
            return obj.user_id.avatar.url
        except:
            return ""

        # if obj.user_id.websites.all():
        #     return list(map(lambda ob: (ob.key,ob.pair),obj.user_id.websites.all()))
        # else:
        #     return None

    def get_role(self,obj):
        var=obj.user_id.user
        if var.is_admin:
            return "Admin"
        elif var.is_moderator:
            return "Moderator"
        else:
            return "User"
    def get_is_follower(self,obj):
        if UserFollowing.objects.filter(user_id=obj.following_user_id,following_user_id=obj.user_id).exists():
            return True
        return False

class WebsitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Websites
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    userID = serializers.SerializerMethodField()
    # Token=serializers.SerializerMethodField()
    created_at=serializers.SerializerMethodField()
    profileURL=serializers.SerializerMethodField()
    Profession=serializers.SerializerMethodField()
    Websites=serializers.SerializerMethodField()
    myInterest=serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [  'userID',
                    'user',  
                    'bio', 
                    'Websites',
                    'Profession',
                    'myInterest',
                    'created_at',
                    'followers_count',
                    'followings_count',
                    'profileURL'


                ]
    def get_myInterest(self,obj):
        return MyInterestSerializer(obj.MyInterest.all(),many=True).data
    
    def get_profileURL(self,obj):
        try:
            return obj.avatar.url
        except Exception as E:
            print(E)
            return "None"
        

    def get_user(self, obj):
        return UserSerializer(obj.user).data
    
    def get_userID(self, obj):
        return obj.user.pk
        

    
    def get_Profession(self,obj):
        try:
            return obj.profession.name
        except :
            return None 
    def get_Websites(self, obj):
        objs=Websites.objects.filter(user_id=obj.user)
        data = WebsitesSerializer(objs, many=True).data
        return data
    # def get_Token(self,obj):
    #     try:
    #         return Token.objects.get(user=obj.user).key
    #     except:
    #         return None 
    def get_created_at(self,obj):
        return obj.user.created_at
    

class ViewProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    userID = serializers.SerializerMethodField()
    profileURL=serializers.SerializerMethodField()
    Profession=serializers.SerializerMethodField()
    Websites=serializers.SerializerMethodField()
    myInterest=serializers.SerializerMethodField()
    is_following=serializers.SerializerMethodField()
    is_follower=serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [  'userID',
                    'user',  
                    'bio', 
                    'fullname',
                    'Websites',
                    'Profession',
                    'myInterest',
                    'created_at',
                    'followers_count',
                    'followings_count',
                    'profileURL',
                    'is_following',
                    'is_follower'

                ]
    def get_myInterest(self,obj):
        return MyInterestSerializer(obj.MyInterest.all(),many=True).data

    def get_profileURL(self,obj):
        try:
            return obj.avatar.url
        except Exception as E:
            print(E)
            return None

    def get_user(self, obj):
        return UserSerializer(obj.user).data
    
    def get_userID(self, obj):
        return obj.user.pk
        

    def get_avatar(self, obj):
        try:
            return obj.avatar.url
        except:
            return ''
    def get_Profession(self,obj):
        try:
            return obj.profession.name
        except :
            return None 
    def get_Websites(self, obj):
        print(obj.user)
        objs=Websites.objects.filter(user_id=obj.user)

        data = WebsitesSerializer(objs, many=True).data
        return data
    def get_is_following(self,obj):
        try:
            if UserFollowing.objects.filter(user_id=self.context["request"].user.userAssociated,following_user_id=obj).exists():
                return True
            return False
        except Exception as E:
            print(E)
            return None
    def get_is_follower(self,obj):
        try:
            if UserFollowing.objects.filter(user_id=obj,following_user_id=self.context["request"].user.userAssociated).exists():
                return True
            return False
        except:
            return None
# class dataSerializer(serializers.Serializer):
#     profile=serializers.SerializerMethodField()
#     trending=

class BriefProfileSerializer(serializers.Serializer):
    username=serializers.SerializerMethodField()
    userID=serializers.SerializerMethodField()
    profileURL=serializers.SerializerMethodField()
    role=serializers.SerializerMethodField()
    bio=serializers.SerializerMethodField()
    is_following=serializers.SerializerMethodField()
    def get_username(self,obj):
        return obj.user.username
    def get_userID(self,obj):
        return obj.user.id
    def get_bio(self,obj):
        return obj.bio
    def get_profileURL(self,obj):
        try:
            return obj.avatar.url
        except:
            return None
        
        # if obj.user_id.websites.all():
        #     return list(map(lambda ob: (ob.key,ob.pair),obj.user_id.websites.all()))
        # else:
        #     return None

    def get_role(self,obj):
        var=obj.user
        if var.is_admin:
            return "Admin"
        elif var.is_moderator:
            return "Moderator"
        else:
            return "User"
    def get_is_following(self,obj):
        try:
            if UserFollowing.objects.filter(user_id=self.context["request"].user.userAssociated,following_user_id=obj).exists():
                return True
            return False
        except:
            return None 

class professionSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProfessionList
        fields="__all__"