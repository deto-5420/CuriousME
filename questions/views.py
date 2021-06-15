import requests
import pytz
from django.conf import settings
from django.contrib import messages
from django.db.models.functions import StrIndex

from datetime import datetime, date

from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage, send_mail
from django.http import Http404
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.db.models import F, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from collections import OrderedDict
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_411_LENGTH_REQUIRED)
from rest_framework.views import APIView
from collectanea.globals import ( USER_STATUS, MAX_VALIDITY_DAYS, MAX_QUESTION_SIZE, 
                                MAX_ANSWER_LIMIT, MIN_ANSWER_LIMIT
                            )

from accounts.models import Profile, User
from accounts.profile_serializer import ProfileSerializer, ViewProfileSerializer
from questions.keywords_models import Keywords

from .models import Question, Category, BookmarkQuestion, UserVotes, Like
from .serializers import ( QuestionDetailSerializer, 
                            BookmarksSerializer, OtherQuestionsSerializer,
                            BriefQuestionSerializer,OptionSerializer,AnonQuestionsSerializer
                        )
import pdfkit, json, math, os

from answers.models import Answer
from replies.models import Replies
from replies.serializers import BriefReplySerializer
from answers.serializers import AnsSerializer

from django.template.loader import get_template
import pdfkit
from django.http import HttpResponse

    
# from refund.models import Refund, SecurityRefund

from collectanea.permission import AuthorizedPermission
from collectanea.global_checks import check_user_status
from collectanea.helpers import get_days, get_days_from_now
#from adminpanel.dynamic_preferences_registry import QuestionLimit,AnswerLimit,ReplyLimit

question_limit=10 #QuestionLimit.default
answer_limit=10 #AnswerLimit.default

class AddBookmark(APIView):
    """
    simply add bookmark 
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated

        question_id = request.data.get('question_id')
        print(question_id)
        question=Question.objects.filter(id=question_id,status__in=('open', 'Open'))
        if not question.exists():
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid Question Id'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        check_bookmark = BookmarkQuestion.objects.filter(question_id=question[0]).filter(user_id=profile).first()

        if check_bookmark is None:
            BookmarkQuestion.objects.create(
                                            user_id = profile,
                                            question_id = question[0]
                                        )
            message = 'Bookmark added'
        else:
            check_bookmark.delete()
            message = 'Bookmark removed'

        response = {
            'message': message,
            'body': [],
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetAllBookmarks(APIView):
    """
    List of all my bookmarks
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated

        all_bookmarks = profile.userBookmarked.filter(question_id__status__in=("open","Open"))  
        
        if all_bookmarks:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(all_bookmarks, request)
                data = BookmarksSerializer(paginated_list, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'links': {
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link()
                    },
                    'count': paginator.count,
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)
            except:
                print(all_bookmarks)
                data = BookmarksSerializer(all_bookmarks, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No bookmarks found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class SearchQuestions(APIView):
    """
    search a question on the basis of a input text.
    NOTE: ordering on the basis of % match is left.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        search_text = request.data.get('text')
        search_on=request.data.get('type').lower()
        all_questions=None
        print(search_on)
        if search_on == "user":
            objs=Profile.objects.filter(Q(fullname__icontains=search_text)  | Q(user__username__icontains=search_text))
            objs=objs.filter(user__status="Activated")
            if not objs.exists():
                return Response({"message":"No result found"}, status=HTTP_200_OK)
            # for i in range(len(objs )):
            #     q=objs[i].questionAuthor.all().filter(status__in=('open','Open'))
            #     if i==0:
            #         all_questions=q
            #     if q.exists():
            #         all_questions=all_questions | q
            
            # if not all_questions:
            #     return Response({"message":"No result found"}, status=HTTP_200_OK)
            
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(objs, request)
                data = ViewProfileSerializer(paginated_list, context={ 'request': request }, many=True).data
                
                response = {
                    'message':'success',
                    'links': {
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link()
                    },
                    'count': paginator.count,
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)
            except:
                data = ViewProfileSerializer(objs, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        elif search_on=="answer":

            objs=Answer.objects.filter(Q(content__icontains=search_text),status__in=('open','Open') ).values_list("question_id")

            if not objs:
                return Response({"message":"No result found"}, status=HTTP_200_OK)
            all_questions=Question.objects.filter(id__in=objs,status__in=('open','Open'))
        elif search_on=="reply":
            objs=Replies.objects.filter(Q(content__icontains=search_text),status__in=('open','Open')).values_list("answer")
            if not objs:
                return Response({"message":"No result found"}, status=HTTP_200_OK)

            anser_obj=Answer.objects.filter(id__in=objs,status__in=('open','Open')).values_list("question_id")
            if not anser_obj:
                return Response({"message":"No result found"}, status=HTTP_200_OK)
            all_Question.objects.filter(id__in=anser_obj,status__in=('open','Open'))
        elif search_on=="question":  
        
            all_questions = Question.objects.filter(content__icontains=search_text,status__in=('open','Open'))
            
        if all_questions:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(all_questions, request)
                data = OtherQuestionsSerializer(paginated_list, context={ 'request': request }, many=True).data
                
                response = {
                    'message':'success',
                    'links': {
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link()
                    },
                    'count': paginator.count,
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)
            except:
                print(all_questions,type(all_questions))
                data = OtherQuestionsSerializer(all_questions, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No Questions found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetQuestionByAnswer(APIView):
    """
    get question by answer ID
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        answer_id = request.data.get('answer_id')

        try:
            answer = get_object_or_404(Answer, pk=int(answer_id))
        except:
            response = {
                'message': 'Failed',
                'error': ['Invalid answerID'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        data = OtherQuestionsSerializer(answer.question_id, context={ 'request': request }).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetQuestionByID(APIView):
    """
    get question by ID
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        question_id = request.data.get('question_id')

        try:
            question = get_object_or_404(Question, pk=int(question_id))
        except:
            response = {
                'message': 'Failed',
                'error': ['Invalid ID'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        data = OtherQuestionsSerializer(question, context={ 'request': request }).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class SuggestQuestions(APIView):
    """
    suggest a question on the basis of a input text.
    NOTE: ordering on the basis of % match is left.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        search_text = request.data.get('text')

        questions = Question.objects.filter(content__icontains=search_text).filter(public=True)
        data = BriefQuestionSerializer(questions, context={ 'request': request }, many=True).data

        return Response({'questions':data}, status=HTTP_200_OK)



class GetQuestionsByCategory(APIView):
    """
    get questions by category 
    NOTE: sort_by unanswered, popular and price is remaining.
    """

    #permission_classes = (IsAuthenticated, AuthorizedPermission)
    pagination_class=LimitOffsetPagination
    def post(self, request, *args, **kwargs):
        category_id = request.data.get('category_id')
        sort_by = request.data.get('sort_by')

        # user = self.request.user
        # profile = user.userAssociated
        category=None
        try:
            category = get_object_or_404(Category, pk=int(category_id))
        except:
            response = {
                'message': 'Failed',
                'error': ['Invalid category ID'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        all_questions = Question.objects.filter(status__in=('open', 'Open'),category=category)
        
        
        if sort_by == 'new':
            all_questions=all_questions.order_by('-created_at')
        
        elif sort_by == 'Popular':
            all_questions=all_questions.annotate(fieldsum=F("answer_count")+F("upvote_count")).order_by("fieldsum")

        elif sort_by == 'Unanswered':
            all_questions=all_questions.filter(answer_count=0)
        elif sort_by == 'Rising':
            z_scores = {}
            for ques in all_questions:
                user_upvotes=list(ques.question_votes.filter(vote_type__in=("Upvote","upvote")).values('created_at').order_by('created_at').annotate(count=Count("created_at")))
                if user_upvotes:
                    date_today = datetime.now(timezone.utc)
                    created_at = ques.created_at
                    most_recent_used = user_upvotes[-1]['created_at']
                    days_created_before = date_today-created_at
                    days_created_before = int(days_created_before.days)
                    not_used_days = days_created_before - len(user_upvotes)
                    if days_created_before>0:
                        avg_trend = len(user_upvotes)/(days_created_before)
                    else:
                        avg_trend = len(user_upvotes)

                    std_deviation = sum(((int(c['count']) - avg_trend) ** 2) for c in user_upvotes)
                    std_deviation += (((0-avg_trend)**2) * (not_used_days))

                    if days_created_before>0:
                        standard_deviation = math.sqrt(abs(std_deviation) / (days_created_before))
                    else:
                        standard_deviation = math.sqrt(abs(std_deviation))

                    standard_deviation = -1*standard_deviation if std_deviation<0 else standard_deviation

                    if most_recent_used-date_today == 0:            
                        current_trend = user_upvotes[-1]['count']
                    else:
                        current_trend=0

                    standard_deviation = 1 if standard_deviation==0 else standard_deviation
                    z_score = (current_trend-avg_trend)/standard_deviation
                    z_scores[ques.id] = z_score

            sorted_question = OrderedDict(sorted(z_scores.items(), key = lambda kv:kv[1], reverse=True))
            
            all_questions =[]
            for ques in sorted_question:
                # if sorted_hashtags[hashtag]<0:
                #     break
                ques_obj=Question.objects.filter(id=ques).first()
                all_questions.append(ques_obj)
        else:
            response = {
                'message': 'Failed',
                'error': ['Invalid sort by attribute :choices are ["new","Rising","Unanswered","Popular"]'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        if request.user.is_authenticated:
            if all_questions:
                try:
                    paginator = LimitOffsetPagination()
                    paginated_list = paginator.paginate_queryset(all_questions, request)
                    data = OtherQuestionsSerializer(paginated_list, context={ 'request': request }, many=True).data
                    
                    response = {
                        'message':'success',
                        'links': {
                            'next': paginator.get_next_link(),
                            'previous': paginator.get_previous_link()
                        },
                        'count': paginator.count,
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
                except:
                    data = OtherQuestionsSerializer(all_questions, context={ 'request': request }, many=True).data

                    response = {
                        'message':'success',
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)

            response = {
                'message':'No Questions found',
                'body':[],
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        else:
            all_questions=list(all_questions)
            var=None
            try:
                var=all_questions[:question_limit]
            except:
                var=all_questions
            data = AnonQuestionsSerializer(var, many=True).data

            response = {
                'message':'success',
                'body':data,
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)


class GetQuestionsByKeyword(APIView):
    """
    get questions by category 
    NOTE: sort_by unanswered, popular and price is remaining.
    """

    #permission_classes = (IsAuthenticated, AuthorizedPermission)
    pagination_classes=LimitOffsetPagination
    def post(self, request, *args, **kwargs):
        keyword_id = request.data.get('keyword_id')
        
        sort_by = request.data.get('sort_by')
        # user = self.request.user
        # profile = user.userAssociated
        print("Check1")
        try:
            keyword = get_object_or_404(Keywords, pk=int(keyword_id))
        except:
            response = {
                'message': 'Failed',
                'error': ['Invalid keyword ID'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        all_questions =keyword.associatedKeywords.filter(status="open") #Question.objects.filter(category=category)

        if sort_by == 'new':
            all_questions=all_questions.order_by('-created_at')
        
        elif sort_by == 'Popular':
            all_questions=all_questions.annotate(fieldsum=F("answer_count")+F("upvote_count")).order_by("fieldsum")

        elif sort_by == 'Unanswered':
            all_questions=all_questions.filter(answer_count=0)
        elif sort_by == 'Rising':
            z_scores = {}
            for ques in all_questions:
                user_upvotes=list(ques.question_votes.filter(vote_type__in=("Upvote","upvote")).values('created_at').order_by('created_at').annotate(count=Count("created_at")))
                if user_upvotes:
                    date_today = datetime.now(timezone.utc)
                    created_at = ques.created_at
                    most_recent_used = user_upvotes[-1]['created_at']
                    days_created_before = date_today-created_at
                    days_created_before = int(days_created_before.days)
                    not_used_days = days_created_before - len(user_upvotes)
                    if days_created_before>0:
                        avg_trend = len(user_upvotes)/(days_created_before)
                    else:
                        avg_trend = len(user_upvotes)

                    std_deviation = sum(((int(c['count']) - avg_trend) ** 2) for c in user_upvotes)
                    std_deviation += (((0-avg_trend)**2) * (not_used_days))

                    if days_created_before>0:
                        standard_deviation = math.sqrt(abs(std_deviation) / (days_created_before))
                    else:
                        standard_deviation = math.sqrt(abs(std_deviation))

                    standard_deviation = -1*standard_deviation if std_deviation<0 else standard_deviation

                    if most_recent_used-date_today == 0:            
                        current_trend = user_upvotes[-1]['count']
                    else:
                        current_trend=0

                    standard_deviation = 1 if standard_deviation==0 else standard_deviation
                    z_score = (current_trend-avg_trend)/standard_deviation
                    z_scores[ques.id] = z_score

            sorted_question = OrderedDict(sorted(z_scores.items(), key = lambda kv:kv[1], reverse=True))
            
            all_questions =[]
            for ques in sorted_question:
                # if sorted_hashtags[hashtag]<0:
                #     break
                ques_obj=Question.objects.filter(id=ques).first()
                all_questions.append(ques_obj)
        
        else:
            response = {
                'message': 'Failed',
                'error': ['Invalid sort by attribute :choices are ["new","Rising","Unanswered","Popular"]'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
 
        if request.user.is_authenticated:
            if all_questions:
                try:
                    paginator = LimitOffsetPagination()
                    paginated_list = paginator.paginate_queryset(all_questions, request)
                    data = OtherQuestionsSerializer(paginated_list, context={ 'request': request }, many=True).data
                    
                    response = {
                        'message':'success',
                        'links': {
                            'next': paginator.get_next_link(),
                            'previous': paginator.get_previous_link()
                        },
                        'count': paginator.count,
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
                except:
                    data = OtherQuestionsSerializer(all_questions, context={ 'request': request }, many=True).data

                    response = {
                        'message':'success',
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)

            response = {
                'message':'No Questions found',
                'body':[],
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        else:
            all_questions=list(all_questions)
            var=None
            try:
                var=all_questions[:10]
            except:
                var=all_questions
            data = AnonQuestionsSerializer(var, many=True).data

            response = {
                'message':'success',
                'body':data,
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)


class myFeed(APIView):
    permission_classes = (IsAuthenticated, AuthorizedPermission)
    permission_class=LimitOffsetPagination
    def post(self,request):
        sort_by = request.data.get('sort_by')
        user = self.request.user
        user_obj=user.userAssociated
        following=user_obj.following.all()
        ques_obj=[]
        for obj in following:
            ques=None
            try:
                ques=obj.following_user_id.allAnswers.all().latest("created_at").question_id
            except:
                pass
            if ques and ques.status=="open":
                ques_obj.append((ques,ques.id))
        interest=user_obj.MyInterest.all()
        q=Question.objects.filter(category__in=interest,status__in=("open","Open"))
        for obj in q:
            ques_obj.append((obj,obj.id))
        id_list=list(map(lambda a: a[1],ques_obj))
        all_questions=Question.objects.filter(id__in=id_list)
        if sort_by == 'new':
            all_questions=all_questions.order_by('-created_at')
            print(all_questions.values_list("id"))
        
        elif sort_by == 'Popular':
            all_questions=all_questions.annotate(fieldsum=F("answer_count")+F("upvote_count")).order_by("-fieldsum")

        elif sort_by == 'Unanswered':
            all_questions=all_questions.filter(answer_count=0)
        elif sort_by == 'Rising':
            z_scores = {}
            for ques in all_questions:
                user_upvotes=list(ques.question_votes.filter(vote_type__in=("Upvote","upvote")).values('created_at').order_by('created_at').annotate(count=Count("created_at")))
                if user_upvotes:
                    date_today = datetime.now(timezone.utc)
                    created_at = ques.created_at
                    most_recent_used = user_upvotes[-1]['created_at']
                    days_created_before = date_today-created_at
                    days_created_before = int(days_created_before.days)
                    not_used_days = days_created_before - len(user_upvotes)
                    if days_created_before>0:
                        avg_trend = len(user_upvotes)/(days_created_before)
                    else:
                        avg_trend = len(user_upvotes)

                    std_deviation = sum(((int(c['count']) - avg_trend) ** 2) for c in user_upvotes)
                    std_deviation += (((0-avg_trend)**2) * (not_used_days))

                    if days_created_before>0:
                        standard_deviation = math.sqrt(abs(std_deviation) / (days_created_before))
                    else:
                        standard_deviation = math.sqrt(abs(std_deviation))

                    standard_deviation = -1*standard_deviation if std_deviation<0 else standard_deviation

                    if most_recent_used-date_today == 0:            
                        current_trend = user_upvotes[-1]['count']
                    else:
                        current_trend=0

                    standard_deviation = 1 if standard_deviation==0 else standard_deviation
                    z_score = (current_trend-avg_trend)/standard_deviation
                    z_scores[ques.id] = z_score

            sorted_question = OrderedDict(sorted(z_scores.items(), key = lambda kv:kv[1], reverse=True))
            
            all_questions =[]
            for ques in sorted_question:
                # if sorted_hashtags[hashtag]<0:
                #     break
                ques_obj=Question.objects.filter(id=ques).first()
                all_questions.append(ques_obj)
        else:
            response = {
                'message': 'Failed',
                'error': ['Invalid sort by attribute :choices are ["new","Rising","Unanswered","Popular"]'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if all_questions:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(all_questions, request)
                data = OtherQuestionsSerializer(paginated_list, context={ 'request': request }, many=True).data
                
                response = {
                    'message':'success',
                    'links': {
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link()
                    },
                    'count': paginator.count,
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)
            except:
                data = OtherQuestionsSerializer(all_questions, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No Questions found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
     

class LikeQuestion(APIView):
    """
    Toggle Likes
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated

        question_id = request.data.get('question_id')

        question=Question.objects.filter(id=question_id,status__in=('open', 'Open'))
      
        if not question.exists():
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid Question Id'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=400)

        get_Like = Like.objects.filter(user_id=profile).filter(question_id=question[0]).first()

        if get_Like is None:
            message = "Liked"

            Like.objects.create(user_id=profile, question_id=question[0])
        else:
            get_Like.delete()
            message = "Removed from Like"
        
        response = {
            'message': message,
            'body': [],
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class ReactionQuestion(APIView):
    """
    React upvote ,downvote or null to remove the reaction
    """

    #permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated

        question_id = request.data.get('question_id')
        reaction = request.data.get('Reaction')
        if  reaction and reaction not in ("upvote","downvote"):
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid reaction'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=400)

        question=Question.objects.filter(id=question_id,status__in=('open', 'Open')).first()
        if not question:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid Question Id'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=400)

        get_vote = UserVotes.objects.filter(user=user,question=question)
        print(get_vote)
        if reaction :
            if not get_vote :
                message = reaction

                UserVotes.objects.create(user=profile.user, question=question,vote_type=reaction)
            else:
                if get_vote[0].vote_type==reaction:
                    message="Already "+reaction
                else: 
                    
                    print(get_vote.delete())
                    UserVotes.objects.create(user=profile.user, question=question,vote_type=reaction)
                    message = reaction
        else:
            print(get_vote)
            print(bool(get_vote))
            if get_vote:
                message=get_vote[0].vote_type +"Removed"
                get_vote.delete()
            else:
                message="You can't remove reaction when you have not reacted "
                response = {
                    'message': message,
                    'body': [],
                    'status': 400
                }
                return Response(response, status=400)
                
        response = {
            'message': message,
            'body': [],
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

from reportlab.pdfgen import canvas
from django.http import HttpResponse
from xhtml2pdf import pisa 
from io import BytesIO
from wkhtmltopdf.views import PDFTemplateResponse
import pdfkit

class getdownloadBook(APIView):
    # permission_classes = (IsAuthenticated, AuthorizedPermission)
    def post(self,request):
        ID=request.data.get("QuestionID")
        ques_obj=Question.objects.filter(id=ID,status__in=('open','Open'))
        if not ques_obj.exists():
            return Response({"message":"Invalid ID"},status=400)
        
        ques_data=QuestionDetailSerializer(ques_obj,many=True,context={ 'request': request }).data
        del ques_data[0]['Answer']
        dict1={"ques_data":ques_data}
        if ques_obj.first().question_type not in ('poll', 'Poll'):
            answers=ques_obj.first().questionAnswer.filter(status__in=('open','Open'))
            
            
            dict1["Answers"]=[]
            for ans in answers:
                answer_data=AnsSerializer(ans,context={ 'request': request }).data
                replies=ans.AnswerReplies.filter(status__in=('open','Open')).order_by("like_count")
                print(ans,replies)
                replies_data=BriefReplySerializer(replies,many=True,context={ 'request': request }).data
                dict1["Answers"].append({"answer_data":answer_data,"replies_data":replies_data})
        print(dict1)
        
        template = get_template('pdf.html')
        html = template.render(context={
            "data":dict1
        })
        pdfkit.from_string(html,"question.pdf")
        pdf=open("question.pdf",'rb')
        response=HttpResponse(pdf.read(),content_type='application/pdf')
        response["Content-Disposition"]='attachment; filename=output.pdf'
        # buffer=BytesIO()
        # p=canvas.Canvas(buffer)
        # p.drawString(100,100,json.dumps(dict1))
        # print(json.dumps(dict1))
        # p.save()
        # pdf.close()
        # # os.remove("question.pdf")
        # pdf=buffer.getvalue()
        # buffer.close()
        response.write(pdf)
        return response
        # template = get_template("templatePrint.html")
        # context = {"user": user_obj,"formula":formula_obj,"cnsobj":consumptions_obj,"prodobj":productions_obj,"over":overhead_obj} # data is the context data that is sent to the html file to render the output. 
        # html = template.render(context)  # Renders the template with the context data.
        # path_wkhtmltopdf = r'C:\\Program Files (x86)\\wkhtmltox\\bin\\wkhtmltopdf.exe'
        #""""
        # config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
        # pdfkit.from_string(html, 'out.pdf',configuration=config)
        # pdf = open("out.pdf","r",encoding='utf-8',errors='ignore')
        # response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
        # response['Content-Disposition'] = 'attachment; filename=output.pdf'
        # pdf.close()
        # return response

        # response = PDFTemplateResponse(request=request,
        #                            template='pdf.html',
        #                            filename="hello.pdf",
        #                            context={"data":"HI"},
        #                            show_content_in_browser=False,
        #                            cmd_options=settings.    WKHTMLTOPDF_CMD_OPTIONS,
        #                            )
        # return response
        
        # html = template.render(context)  # Renders the template with the context data.
        # path_wkhtmltopdf = r''
        # config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        # pdfkit.from_string(html, 'out.pdf',configuration=config)
        # pdf = open("out.pdf","r",encoding='utf-8',errors='ignore')
        # response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
        # response['Content-Disposition'] = 'attachment; filename=output.pdf'
        # pdf.close()
        # return response
        # print(html)
        # # Create a Django response object, and specify content_type as pdf
        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=report.pdf'
        # # find the template and render it.
        # result = BytesIO()
        # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        # if not pdf.err:
        #     print("H")
        #     return HttpResponse(result.getvalue(), content_type='application/pdf')
        # return None
        # # create a pdf
        # pisa_status = pisa.CreatePDF(
        #     html, dest=response)
        # # if error then show some funy view
        # if pisa_status.err:
        #     return HttpResponse('We had some errors <pre>' + html + '</pre>')
        # return response

        # pdfkit.from_string(html, "sample_pdf.pdf")
        # pdf=open("sample_pdf.pdf",'rb')
        # print(pdf.read())
        # response = HttpResponse(pdf.read(), content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=output.pdf'
        # pdf.close()

        # return response
        # print(json.dumps(dict1))
        # pdfkit.from_string(json.dumps(dict1),"question.pdf")
        # pdf=open("question11.pdf",'rb')
        # response=HttpResponse(pdf.read(),content_type='application/pdf')
        # response["Content-Disposition"]='attachment; filename=output.pdf'
        # buffer=BytesIO()
        # p=canvas.Canvas(buffer)
        # p.drawString(100,100,json.dumps(dict1))
        # print(json.dumps(dict1))
        # p.save()
        # pdf.close()
        # # os.remove("question.pdf")
        # pdf=buffer.getvalue()
        # buffer.close()
        # response.write(pdf)
        # return response
        
        
















# class UpVoteQuestion(APIView):

#     permission_classes = (IsAuthenticated, AuthorizedPermission)

#     def post(self, request, *args, **kwargs):
#         user = self.request.user
#         profile = user.userAssociated.all().first()

#         question_id = request.data.get('question_id')

#         try:
#             question = get_object_or_404(Question, pk=int(question_id))
#         except:
#             response = {
#                 'message': 'Failed',
#                 'error': ['Invalid QuestionID'],
#                 'status': HTTP_400_BAD_REQUEST
#             }
#             return Response(response, status=HTTP_400_BAD_REQUEST)
        
#         # print(DownVote.objects.get_object_or_404(user_id = profile, question_id = question))
#         # try:
#         #     get_downvote = DownVote.objects.filter(user_id=profile).filter(question_id=question).first()
#         #     get_upvote = UpVote.objects.filter(user_id=profile).filter(question_id=question).first()
#         #     # message = ''

#         #     if get_downvote is not None:
#         #         DownVote.objects.delete(user_id = profile, question_id = question)
#         #         UpVote.objects.create(user_id = profile, question_id = question)
#         #         message = 'UpVoted'

#         #     elif get_upvote is not None:
#         #         UpVote.objects.delete(user_id = profile, question_id = question)
#         #         message = 'Removed from UpVote'
#         #     # else:
#         #     #     message = 'Invalid'

#         # except:
#         #     pass

#         try:
#             DownVote.objects.filter(user_id=profile).filter(question_id=question).first()
#             message = 'already downvoted'
#         except:
#             # if get_downvote is not None:
#             #     DownVote.objects.delete(user_id = profile, question_id = question)
#             UpVote.objects.create(user_id = profile, question_id = question)
#             message = 'UpVoted'
#         response = {
#             'message': message,
#             'body': [],
#             'status': HTTP_200_OK
#         }
#         return Response(response, status=HTTP_200_OK)

# class DownVoteQuestion(APIView):
#     permission_classes = (IsAuthenticated, AuthorizedPermission)

#     def post(self, request, *args, **kwargs):
#         user = self.request.user
#         profile = user.userAssociated.all().first()

#         question_id = request.data.get('question_id')

#         try:
#             question = get_object_or_404(Question, pk=int(question_id))
#         except:
#             response = {
#                 'message': 'Failed',
#                 'error': ['Invalid QuestionID'],
#                 'status': HTTP_400_BAD_REQUEST
#             }
#             return Response(response, status=HTTP_400_BAD_REQUEST)

#         if UpVote.objects.get(user_id = profile, question_id = question):
#             UpVote.objects.delete(user_id = profile, question_id = question)
#             DownVote.objects.create(user_id = profile, question_id = question)
#             body = 'DownVoted'

#         elif DownVote.objects.get(user_id = profile, question_id = question):
#             DownVote.objects.delete(user_id = profile, question_id = question)
#             body = 'Removed from DownVote'

#         response = {
#             'message': 'success',
#             'body': [],
#             'status': HTTP_200_OK
#         }
#         return Response(response, status=HTTP_200_OK)