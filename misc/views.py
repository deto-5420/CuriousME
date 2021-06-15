from django.shortcuts import render
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_411_LENGTH_REQUIRED)
from rest_framework.views import APIView
from .models import ReportIssue
from accounts.models import ProfessionList,User
from accounts.profile_serializer import professionSerializer
from answers.models import Answer
from questions.models import Question
from questions.serializers import LikedAnswerSerializer,LikedReplySerializer,OtherQuestionsSerializer
from replies.models import Replies

from accounts.models import Profile
from accounts.profile_serializer import ProfileSerializer
from collectanea.permission import AuthorizedPermission
from notifications.signals import notify
from misc.serializers import NotificationSerializer
from questions.models import Question
from questions.serializers import AnonQuestionsSerializer
class get_user_liked_Question_View(APIView):
    permission_classes = [IsAuthenticated, AuthorizedPermission]
    pagination_classes=LimitOffsetPagination
    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated
        liked_question_id=profile.userLikes.all().values_list('question_id')
        liked_question_obj=Question.objects.filter(id__in=liked_question_id,status__in=("open","Open"))
        if liked_question_obj:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(liked_question_obj, request)
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
                data = OtherQuestionsSerializer(liked_question_obj, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No questions found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
class get_user_liked_Answer_View(APIView):
    permission_classes = [IsAuthenticated, AuthorizedPermission]
    pagination_classes=LimitOffsetPagination
    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated
        liked_answer=profile.user_Likes_answers.filter(reaction_type__in=("Like","like")).values_list('answer')
        liked_answer_obj=Answer.objects.filter(id__in=liked_answer)
        if liked_answer_obj:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(liked_answer_obj, request)
                data = LikedAnswerSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = LikedAnswerSerializer(liked_answer_obj, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)
        else:
            response = {
                    'message':'success',
                    'body':[],
                    'status':HTTP_200_OK
                }
            return Response(response, status=HTTP_200_OK)

class get_user_liked_replies_View(APIView):
    permission_classes = [IsAuthenticated, AuthorizedPermission]
    pagination_classes=LimitOffsetPagination
    def get(self, request, *args, **kwargs):
        user = self.request.user
        print(user.id,user.username)
        profile = user.userAssociated
        print(profile.id,profile)
        liked_reply=profile.user_Likes_replies.filter(reaction_type__in=("Like","like")).values_list('reply').distinct()
        liked_reply_obj=Replies.objects.filter(id__in=liked_reply)
        print(liked_reply,liked_reply_obj)
        if liked_reply_obj:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(liked_reply_obj, request)
                data = LikedReplySerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = LikedReplySerializer(liked_reply_obj, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)
        else:
            response = {
                    'message':'success',
                    'body':[],
                    'status':HTTP_200_OK
                }
            return Response(response, status=HTTP_200_OK)
class ReportIssueView(APIView):
    permission_classes = [IsAuthenticated, AuthorizedPermission]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated

        title = request.data.get('title')
        description = request.data.get('description')
        image = request.FILES.get('image')
        if not title or not description:
            response = {
                'message':'Either Title or description is empty',
                'body':[],
                'status':400
            }
            return Response(response, status=400)

        ReportIssue.objects.create(user=profile,title=title,description=description,image=image)
       
        response = {
            'message':'Success',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class getProfessionList(APIView):
    # permission_classes = [IsAuthenticated, AuthorizedPermission]

    def get(self, request, *args, **kwargs):
        p=ProfessionList.objects.all()
        data=professionSerializer(p,many=True).data
        response = {
            'message':'Success',
            'body':data,
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class getNotification(APIView):
    

    permission_classes = [IsAuthenticated, AuthorizedPermission]
    pagination_classes=LimitOffsetPagination
    def post(self, request, *args, **kwargs):

        user=request.user
        objs=user.notifications.all().order_by("-timestamp")

        if objs.exists():
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(objs, request)
                data = NotificationSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = NotificationSerializer(objs, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No notifications found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class getUsersList(APIView):
    # permission_classes = [IsAuthenticated, AuthorizedPermission]
    pagination_classes=LimitOffsetPagination
    def get(self, request, *args, **kwargs):
        p=Profile.objects.filter(user__is_active=True)
        
        if p.exists():
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(p, request)
                data = ProfileSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = ProfileSerializer(p, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No notifications found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class getQuesList(APIView):
    # permission_classes = [IsAuthenticated, AuthorizedPermission]
    pagination_classes=LimitOffsetPagination
    def get(self, request, *args, **kwargs):
        p=Question.objects.filter(status__in=("open","Open"))
        if p.exists():
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(p, request)
                data = AnonQuestionsSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = AnonQuestionsSerializer(p, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No notifications found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
