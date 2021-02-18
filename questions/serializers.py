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

from .models import Question, BookmarkQuestion
from .keywords_serializers import KeyWordsSerializer



class QuestionSerializer(serializers.ModelSerializer):
    """
    question serializer + payment status
    """

    # payment = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
                    'content', 
                    'created_date', 
                    'status', 
                    'category', 
                    'keywords',
                ]

    # def get_payment(self, obj):
    #     if obj.public:
    #         payment_obj = obj.questionPayment.all()
    #         return PaymentStatusSerializer(payment_obj, many=True).data
        
    def get_keywords(selkf, obj):
        return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data

class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    includes upvotes and responses
    """

    # payment = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    upvotes = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
                    'content', 
                    'created_date', 
                    'status', 
                    'category', 
                    # 'payment',
                    'keywords',
                    'upvotes',
                ]

    # def get_payment(self, obj):
    #     if obj.public:
    #         payment_obj = obj.questionPayment.all()
    #         return PaymentStatusSerializer(payment_obj, many=True).data
        
    def get_keywords(selkf, obj):
        return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data
    
    def get_total_responses(self, obj):
        return obj.questionAnswer.all().count()
    
    def get_upvotes(self, obj):
        return obj.questionUpvoted.all().count()

class BookmarksSerializer(serializers.ModelSerializer):
    """
    using question deatil serializer. 
    """

    question = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = BookmarkQuestion
        fields = ['question', 'is_upvoted']

    def get_question(self, obj):
        return QuestionDetailSerializer(obj.question_id).data
    
    def get_is_upvoted(self, obj):
        user = self.context['request'].user
        profile = user.userAssociated.all().first()
        is_upvoted = obj.question_id.questionUpvoted.all().filter(user_id=profile).first()

        if is_upvoted is None:
            return False
        return True

class OtherQuestionsSerializer(serializers.ModelSerializer):
    """
    includes is_upvoted.
    """

    # payment = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    upvotes = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
                    'content', 
                    'created_date', 
                    'status', 
                    'category', 
                    # 'payment',
                    'keywords',
                    'upvotes',
                    'is_upvoted',
                ]

    # def get_payment(self, obj):
    #     if obj.public:
    #         payment_obj = obj.questionPayment.all()
    #         return PaymentStatusSerializer(payment_obj, many=True).data
        
    def get_keywords(selkf, obj):
        return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data
    
    def get_total_responses(self, obj):
        return obj.questionAnswer.all().count()
    
    def get_upvotes(self, obj):
        return obj.questionUpvoted.all().count()
    
    def get_is_upvoted(self, obj):
        user = self.context['request'].user
        profile = user.userAssociated.all().first()
        is_upvoted = obj.questionUpvoted.all().filter(user_id=profile).first()

        if is_upvoted is None:
            return False
        return True

class BriefQuestionSerializer(serializers.ModelSerializer):
    """
    only id and content
    """

    class Meta:
        model = Question
        fields = ['pk', 'content']