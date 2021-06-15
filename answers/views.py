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
# from BitsyBits.globals import ( USER_STATUS, MAX_VALIDITY_DAYS, MAX_QUESTION_SIZE, 
#                                 MAX_ANSWER_LIMIT, MIN_ANSWER_LIMIT, SECURITY_AMOUNT_RATE,
#                                 SERVICE_CHARGE_RATE, X_RATING , MAX_MEDIA_ALLOWED,
#                                 MAX_MEDIA_SIZE
#                             )

from accounts.models import Profile, User
from accounts.profile_serializer import ProfileSerializer, ViewProfileSerializer
from adminpanel.models import SpammedAnswer,SpammedReply
from questions.keywords_models import Keywords

from questions.models import Question,  Category, BookmarkQuestion, Options, OptionVotes
from questions.serializers import (  QuestionDetailSerializer, 
                            BookmarksSerializer, OtherQuestionsSerializer,
                            BriefQuestionSerializer,OptionSerializer
                        )

from answers.models import Answer, AnswerMedia, UserLikes as AnswerUserLikes
from answers.serializers import AnswerSerializer

# from refund.models import Refund, SecurityRefund

# from BitsyBits.permission import AuthorizedPermission
# from BitsyBits.global_checks import check_user_status
# from BitsyBits.helpers import get_days, get_days_from_now

from replies.models import Replies, ReplyMedia,UserLikes as ReplyUserLikes
from replies.serializers import ReplySerializer
from rest_framework.pagination import LimitOffsetPagination

from collectanea.globals import MAX_MEDIA_SIZE,MAX_MEDIA_ALLOWED,MAX_ANSWER_LIMIT

# class HookViewSet(viewsets.ModelViewSet):
#     """
#     create webhooks.
#     """
#     queryset = Hook.objects.all()
#     model = Hook
#     serializer_class = HookSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
# from django.views.decorators.http import require_http_methods
# @require_http_methods(["GET", "POST"])
# def hook_receiver_view(request):
#     answer_id = request.GET.get('id', None)
#     # Save the payment status
#     payment = Payment.objects.get(user_id=user_id)
#     payment.payment_successful = True
#     payment.save()
#     return HttpResponse('success')

class GetLatestAnswer(APIView):
    
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        a=Answer.objects.filter().latest("created_at")
        return Response(AnswerSerializer(a).data,status=200)

class FlagAnswer(APIView):
    """
    Spam Accept and Reject answer
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        
        profile = user.userAssociated

        object_id = request.data.get('Id')
        flag = request.data.get('Flag').lower()
        flag = flag.lower()
        types=request.data.get('type').lower()
        if flag !="spammed":
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid Flag '
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if types=="answer":
            answer=None
            try:
                answer = get_object_or_404(Answer, pk=int(object_id))
            except:
                response = {
                    'message': 'Failed',
                    'error': [
                        'Invalid AnswerId'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)
            
            try:
                if answer.status in ('spammed', 'Spammed') or answer.status in ('Deleted', 'Deleted'):
                    response = {
                        'message': 'Answer not Found',
                        'status': HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
                if SpammedAnswer.objects.filter(by=profile,answer=answer).exists():
                    response = {
                        'message': 'this Answer / reply is already flagged as spam',
                        'status': HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
                else:
                    SpammedAnswer.objects.create(by=profile,answer=answer)
                    
                
                
            
            except Exception as e:
                response = {
                    'message': 'Failed',
                    'error': e,
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            response = {
                'message': 'Success',
                'body': [],
                'status': HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
            
            
           
        elif types=="reply":
            reply=None
            try:
                reply = get_object_or_404(Replies, pk=int(object_id))
            except:
                response = {
                    'message': 'Failed',
                    'error': [
                        'Invalid RepliesId'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)
            
            try:
                if reply.status in ('spammed', 'Spammed') or reply.status in ('Deleted', 'Deleted'):
                    response = {
                        'message': 'Reply not found',
                        'status': HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
                if SpammedReply.objects.filter(by=profile,reply=reply).exists():
                    response = {
                        'message': 'this reply is already flagged as spam',
                        'status': HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
                else:
                    SpammedReply.objects.create(by=profile,reply=reply)
                    
                
                
            
            except Exception as e:
                response = {
                    'message': 'Failed',
                    'error': e,
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            
            response = {
                'message': 'Success',
                'body': [],
                'status': HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        else:
            response = {
                'message': 'Invalid Type',
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

# # class AddTip(APIView):
#     """
#     Question author can give tip to any answer 
#     on his private question only.
#     """

#     permission_classes = (IsAuthenticated, AuthorizedPermission)
    
#     def post(self, request, *args, **kwargs):
#         user = self.request.user
#         profile = user.userAssociated.all().first()

#         answer_id = request.data.get('answer_id')
#         tip_amount = request.data.get('tip_amount')
#         currency = request.data.get('currency')
#         remarks = request.data.get('remarks')

#         try:
#             answer = get_object_or_404(Answer, pk=int(answer_id))
#         except:
#             response = {
#                 'message': 'Failed',
#                 'error': [
#                     'Invalid AnswerId'
#                 ],
#                 'status': HTTP_400_BAD_REQUEST
#             }
#             return Response(response, status=HTTP_400_BAD_REQUEST)

#         AnswerTip.objects.create(
#                                 answer_id=answer,
#                                 tip_amount=tip_amount,
#                                 currency=currency,
#                                 remarks=remarks,
#                             )

#         response = {
#             'message': 'Success',
#             'body': [],
#             'status': HTTP_200_OK
#         }
#         return Response(response, status=HTTP_200_OK)
class WriteAnswer(APIView):
    """
    post an answer for any question
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        question_id = request.data.get('questionID')
        media = request.FILES.getlist('media')
        content=request.data.get('content')
        block_reply=  request.data.get('blockReplies').lower()

        if block_reply not in ("true","false"):
            response = {
                'message': 'Failed',
                'error': "Invalid blockreply response ",
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        user = self.request.user
        profile = user.userAssociated
        
        try:
            question = get_object_or_404(Question, pk=int(question_id))
            if question.status not in ("open","Open"):
                response = {
                    'message': 'Failed',
                    'error': "Invalid Question's Status,Can't Reply",
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)


        except:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid questionId'
                    ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:
            
            if len(media) > MAX_MEDIA_ALLOWED:
                print(len(media))
                raise ValidationError("You can upload maximum {} files".format(MAX_MEDIA_ALLOWED))

            for i in range(len(media)):
                if media[i].size > MAX_MEDIA_SIZE:
                    raise ValidationError("You can upload a file of maximum {}mb".format(str(MAX_MEDIA_SIZE//1000000)))
        
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        print(len(media),media)
        for i in range(len(media)):

            if media[i].content_type  in ("audio/mpeg","application/pdf"):
                response = {
                    'message': 'Failed',
                    'error': "Invalid media type",
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

        answer_obj = Answer.objects.create(
                                            user_id=profile, 
                                            question_id=question,
                                            content=content
                                        )
        if block_reply =="true":
            answer_obj.reply_permission=False
        elif block_reply =="false":
            answer_obj.reply_permission=True
        
        answer_obj.save()

        for i in range(len(media)):
            a=AnswerMedia.objects.create(
                                        file=media[i],
                                        answer=answer_obj,
                                        file_type=media[i].content_type
                                    )

        
        response = {
            'message': 'Success',
            'body': AnswerSerializer(answer_obj,context={"request":request}).data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)



class WriteReplies(APIView):
    """
    post an answer for any question
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        answer_id = request.data.get('answerID')
        media = request.FILES.getlist('media')
        content=request.data.get('content')

        user = self.request.user
        profile = user.userAssociated

        try:
            answer = get_object_or_404(Answer, pk=int(answer_id))
            if answer.status not in ("open","Open"):
                response = {
                    'message': 'Failed',
                    'error': "Invalid Answer's Status,Can't Reply",
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)
        except:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid answerId'

                    ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if not answer.reply_permission:
            response = {
                'message': 'Failed',
                'error': [
                    'Reply to this answer is blocked'

                    ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        for i in range(len(media)):

            if media[i].content_type  in ("audio/mpeg","application/pdf"):
                response = {
                    'message': 'Failed',
                    'error': "Invalid media type",
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)


        try:
            

            if len(media) > MAX_MEDIA_ALLOWED:
                raise ValidationError("You can upload maximum {} files".format(MAX_MEDIA_ALLOWED))

            for i in range(len(media)):
                if media[i].size > MAX_MEDIA_SIZE:
                    raise ValidationError("You can upload a file of maximum {}mb".format(str(MAX_MEDIA_SIZE//1000000)))
        
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        reply_obj = Replies.objects.create(
                                            user_id=profile, 
                                            answer=answer,
                                            content=content
                                        )
        
        reply_obj.save()

        for i in range(len(media)):
            ReplyMedia.objects.create(
                                        file=media[i],
                                        reply=reply_obj,
                                        file_type=media[i].content_type
                                    )
        
        response = {
            'message': 'Success',
            'body': ReplySerializer(reply_obj).data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetAnswers(APIView):
    """
    get all answers for a particular question
    """

    permission_classes = [IsAuthenticated]
    pagination_class=LimitOffsetPagination
    def post(self, request, *args, **kwargs):

        question_id = request.data.get('QuestionID')

        try:
            print(1,question_id)
            question = get_object_or_404(Question, pk=int(question_id))
        except:
            print(2)    
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid questionId'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        print(question)
        user = self.request.user
        print(user)
        profile = user.userAssociated
        answers=None
        if question.status in ('open', 'Open') :  #or question.author.pk == profile.pk
            answers = question.questionAnswer.filter(status__in=('open', 'Open','deleted', 'Deleted'))
        else:
            response = {
            'message': 'Invalid Question ID',
            'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if not user.is_authenticated:
            ans=None
            try:
                ans=list(answers)[:20]
            except:
                ans=list(answers)
            data = AnswerSerializer(ans, context={ 'request': request } ,many=True).data

            response = {
                'message':'success',
                'body':data,
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        if answers.exists():
            
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(answers, request)
                data = AnswerSerializer(paginated_list, context={ 'request': request } ,many=True).data
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
            except Exception as E:
                # print(E)
                data = AnswerSerializer(answers, context={ 'request': request } ,many=True).data
                print(data)
                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }

                return Response(data, status=HTTP_200_OK)

        response = {

            'message':'No Results found',
            'body':[] ,
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
        
class GetReplies(APIView):
    """
    get all answers for a particular question
    """

    # permission_classes = (IsAuthenticated)
    pagination_class=LimitOffsetPagination
    def post(self, request, *args, **kwargs):
        answer_id = request.data.get('answerID')

        try:
            answer = get_object_or_404(Answer, pk=int(answer_id))
        except:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid AnswerId'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if not answer.reply_permission:
            return Response("Replies to this answer is blocked",status=200)
        user = self.request.user
        profile = user.userAssociated
        replies=None
        #if answer.status in ('open', 'Open') :  #or question.author.pk == profile.pk
        replies = answer.AnswerReplies.filter(status__in=('open', 'Open','deleted', 'Deleted'))
        # else:
        #     response = {
        #     'message': 'Invalid Question ID',
        #     'status': HTTP_400_BAD_REQUEST
        #     }
        #     return Response(response, status=HTTP_400_BAD_REQUEST)
        if not user.is_authenticated:
            ans=None
            try:
                reply=list(replies)[:20]
            except:
                reply=list(replies)
            data = ReplySerializer(reply, context={ 'request': request } ,many=True).data

            response = {
                'message':'success',
                'body':data,
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        if replies.exists():
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(replies, request)
                data = ReplySerializer(paginated_list, context={ 'request': request } ,many=True).data
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
                data = ReplySerializer(replies, context={ 'request': request } ,many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No Reply  found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetMyAnswersReply(APIView):
    """
    get all my answers for a particular status
    """

    permission_classes = [IsAuthenticated]
    pagination_class=LimitOffsetPagination
    def post(self, request, *args, **kwargs):
        
        user = self.request.user
        profile = user.userAssociated
        types=request.data.get('type').lower()
        print(types)
        if types=="answer":

            answers = profile.allAnswers.filter(status__in=('open', 'Open'))
            print(answers)
            if answers.exists():
                try:
                    paginator = LimitOffsetPagination()
                    paginated_list = paginator.paginate_queryset(answers, request)
                    data = AnswerSerializer(paginated_list, context={ 'request': request } ,many=True).data
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
                    data = AnswerSerializer(answers, context={ 'request': request } ,many=True).data

                    response = {
                        'message':'success',
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)

            response = {
                'message':'No Answer found',
                'body':[],
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
            
           
        elif types=="reply":

            replies = profile.UserReplied.filter(status__in=('open', 'Open'))
            if replies.exists():
                try:
                    paginator = LimitOffsetPagination()
                    paginated_list = paginator.paginate_queryset(replies, request)
                    data = ReplySerializer(paginated_list, context={ 'request': request } ,many=True).data
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
                    data = ReplySerializer(replies, context={ 'request': request } ,many=True).data

                    response = {
                        'message':'success',
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)
            response = {
                'message':'No Reply  found',
                'body':[],
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        else:
            response = {
                'message': 'Invalid Type',
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

            
class ReactAnswers(APIView):
    """
    A user can like or dislike any answer
    he can only like or dislike one at a time
    This api will toggle status based on the 
    user request.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated
        types=request.data.get('type').lower()
        ids = request.data.get('id')
        reaction = request.data.get('reaction').lower()
        if reaction and reaction not in ("like","dislike"):
            return Response({"message":"Invalid reaction can Either Like or Dislike "},status=400)
        if types=='answer':
            answer=Answer.objects.filter(id=ids,status="open").first()
            if not answer:
                response = {
                    'message': 'Failed',
                    'error': [
                        'Invalid AnswerId'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            reaction_obj = AnswerUserLikes.objects.filter(user=profile).filter(answer=answer).first()
            #print(reaction,reaction_obj)
            if reaction:
                if reaction_obj :
                    if  reaction_obj.reaction_type.lower() == reaction:
                        return Response(f'Already {reaction}', status=400)

                    else:
                        reaction_obj.delete()
                        AnswerUserLikes.objects.create(user=profile,answer=answer,reaction_type=reaction)
                        
                else:
                    AnswerUserLikes.objects.create(user=profile,answer=answer,reaction_type=reaction)
                        
            else:
                if reaction_obj:
                    reaction=reaction_obj.reaction_type
                    reaction_obj.delete()
                    return Response(f'Removed {reaction}', status=200)
        elif types=="reply":
            reply=Replies.objects.filter(id=ids,status="open").first()
            if not reply:
                response = {
                    'message': 'Failed',
                    'error': [
                        'Invalid ReplyId'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)

            reaction_obj = ReplyUserLikes.objects.filter(user=profile).filter(reply=reply).first()

            if reaction:
                if reaction_obj :
                    if reaction_obj.reaction_type.lower() == reaction:
                        return Response(f'Already {reaction}', status=400)

                    else:
                        reaction_obj.delete()
                        ReplyUserLikes.objects.create(user=profile,reply=reply,reaction_type=reaction)
                        
                else:
                    ReplyUserLikes.objects.create(user=profile,reply=reply,reaction_type=reaction)
                        
            else:
                if reaction_obj:
                    reaction=reaction_obj.reaction_type
                    reaction_obj.delete()
                    return Response(f'Removed {reaction}', status=200)


        else:
            response = {
                'message': 'Invalid Type',
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        response = {
            'message': "Done",
            'body': [],
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
        


class DeleteAnswer(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        print(user.id)
        profile = user.userAssociated
        print(profile.id)
        answer_id = request.data.get('answerID')

   
        answer=None
        try:
            answer = get_object_or_404(Answer, pk=int(answer_id))
            print(answer.status)
            if answer.status=='Deleted' or answer.status=='deleted':
                response = {
                    'message': 'Failed',
                    'error': [
                        'Already Deleted Answer'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
            
                return Response(response, status=HTTP_400_BAD_REQUEST)

        except:

            response = {
                'message': 'Failed',
                'error': [
                    'Invalid AnswerId'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if answer.user_id.id != profile.id:
            print(answer.user_id.id,answer.user_id.user.id)
            response = {
                    'message': 'Failed',
                    'error': [
                        'Only Owner can Delete'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
            
            return Response(response, status=HTTP_400_BAD_REQUEST)
        try:
            AnswerMedia.objects.filter(answer=answer).delete()
        except:
            pass
        answer.status="deleted"
        answer.save()
        response = {
            'message': 'Successfully Deleted',
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class DeleteReply(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated
        reply_id = request.data.get('replyID')
       
   
        reply=None
        try:
            reply = get_object_or_404(Replies, pk=int(reply_id))
            if reply.status=='Deleted' or reply.status=='deleted':
                response = {
                    'message': 'Failed',
                    'error': [
                        'Already Deleted Reply'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
            
                return Response(response, status=HTTP_400_BAD_REQUEST)
        except:

            response = {
                'message': 'Failed',
                'error': [
                    'Invalid ReplyId'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        if reply.user_id.id != profile.id:
            response = {
                    'message': 'Failed',
                    'error': [
                        'Only Owner can Delete'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
            
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        
        try:
            ReplyMedia.objects.filter(answer=answer).delete()
        except:
            pass
        reply.status="deleted"
        reply.save()
        response = {
            'message': 'Successfully Deleted',
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)


class SubmitPoll(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated
        ques_id = request.data.get('questionID')
        option_id=request.data.get('optionID')
        print(option_id,ques_id)
        option_obj=None
        try:
            option_obj = get_object_or_404(Options, pk=int(option_id))
            
            # print(option_obj.id,0,option_obj.question.id,0,option_obj.question,0,ques_id)
            if option_obj.question.id != ques_id:
                response = {
                    'message': 'Failed',
                    'error': [
                        'Invalid Question Option Pair '
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
            
                return Response(response, status=HTTP_400_BAD_REQUEST)
        except Exception as E:
            print(E)
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid OptionId'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
        ques=None
        try:
            ques = get_object_or_404(Question, pk=int(ques_id))
            if ques.status not in ('open','Open'):
                response = {
                    'message': 'Failed',
                    'error': [
                        'Invalid Question status '
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
            
                return Response(response, status=HTTP_400_BAD_REQUEST)
        except:

            response = {
                'message': 'Failed',
                'error': [
                    'Invalid QuestionId'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        obj=OptionVotes.objects.filter(user=user.userAssociated,question=ques)
        if obj.exists():
            if option_obj.id==obj[0].option.id:
                return Response({"message":"Already voted the same option"}, status=HTTP_200_OK)
            else:
                print(obj)
                try:
                    obj.delete()
                except Exception as E:
                    print(E)
        print(user.userAssociated,ques,option_obj)
        OptionVotes.objects.create(user=user.userAssociated,question=ques,option=option_obj)
        all_option=Options.objects.filter(question=ques)

        data=OptionSerializer(all_option,many=True).data
        response = {
            'message':'success',
            'body':data,
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
        