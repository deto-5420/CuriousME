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

from .keywords_models import Keywords
from .models import Category

class KeyWordsSerializer(serializers.ModelSerializer):
    """
    A serializer for Keywords
    """

    class Meta:
        model = Keywords
        fields = ['name', 'created_at']

class CategorySerializer(serializers.ModelSerializer):

    category_svg = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
                    'name', 
                    'status', 
                    'category_svg', 
                    'category_color', 
                    'created_at', 
                    'updated_at', 
                    'total_questions', 
                    'total_answers'
                ]

    def get_category_svg(self, obj):
        try:
            return obj.category_svg.url
        except:
            return ''