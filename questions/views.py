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
from collectanea.globals import ( USER_STATUS, MAX_VALIDITY_DAYS, MAX_QUESTION_SIZE, 
                                MAX_ANSWER_LIMIT, MIN_ANSWER_LIMIT
                            )

from accounts.models import Profile, User
from accounts.profile_serializer import ProfileSerializer, ViewProfileSerializer
from questions.keywords_models import Keywords

from .models import Question, Category, BookmarkQuestion, Like
from .serializers import ( QuestionSerializer, QuestionDetailSerializer, 
                            BookmarksSerializer, OtherQuestionsSerializer,
                            BriefQuestionSerializer
                        )


from answers.models import Answer
 
# from refund.models import Refund, SecurityRefund

from collectanea.permission import AuthorizedPermission
from collectanea.global_checks import check_user_status
from collectanea.helpers import get_days, get_days_from_now

class PostQuestion(APIView):
    """
    post a question + payment check
    NOTE: stripe not integrated.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        question = request.data.get('question')
        category_id = request.data.get('category')

        try:
            keywords = request.data.getlist('keywords')
        except:
            keywords = request.data.get('keywords')


        user = self.request.user
        profile = user.userAssociated.all().first()

        # validity_days = get_days_from_now(validity_date) 

        try:
            # if validity_days > MAX_VALIDITY_DAYS or validity_days < 1:
                # raise ValidationError("Validity can be of maximum 30 days and minimum 1 day.")

            if len(question) > MAX_QUESTION_SIZE:
                raise ValidationError("Question can be of maximum 200 characters.")

            # if answer_limit<MIN_ANSWER_LIMIT or answer_limit>MAX_ANSWER_LIMIT:
                # raise ValidationError("Answer limit should be between {} and {}".format(MIN_ANSWER_LIMIT, MAX_ANSWER_LIMIT))

            category = Category.objects.filter(pk=int(category_id)).first()
            if category is None:
                raise ValidationError("Invalid category")

            keywords_array = []
            for i in range(len(keywords)):
                keyword_obj = Keywords.objects.filter(pk=int(keywords[i])).first()

                if keyword_obj is None:
                    raise ValidationError("Invalid Keyword ID {}".format(keywords[i]))
                    
                keywords_array.append(keyword_obj)
            
        except Exception as e:
            response = {
                'message': "Failed",
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        # valid_date = datetime.strptime(validity_date, '%d/%m/%Y').date()

        question_object = Question.objects.create(
                                                    author = profile,
                                                    content = question,
                                                    category = category,
                                                )
        
        question_object.keywords_associated.set(keywords_array)

        # if is_anonymous or is_anonymous == 'true':
            # question_object.is_anonymous = True
        
        # if reward_amount and int(reward_amount) > 0:
        #     question_object.public = True
        #     question_object.save()

        #     reward_amount = int(reward_amount)

        #     security_amount = SECURITY_AMOUNT_RATE*reward_amount/100
        #     service_charge = SERVICE_CHARGE_RATE*reward_amount/100

            # PaymentStatus.objects.create(
            #                                 question_id = question_object,
            #                                 reward_amount = reward_amount,
            #                                 security_amount = security_amount,
            #                                 service_charge = service_charge,
            #                                 currency=currency,
            #                             )

        question_object.save()
        print(question_object)
        data = QuestionSerializer(question_object).data

        response = {
            'message': 'Sucess',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class DeleteQuestion(APIView):
    """
    Delete paid and unaid question both.
    If the question has been answered by someone then it can't be deleted.
    NOTE: Incase of paid question refund will be initiated once.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def delete(self, request, *args, **kwargs):
        question_id = request.data.get('question_id')
        user = self.request.user

        profile = user.userAssociated.all().first()

        try:
            question = get_object_or_404(Question, pk=int(question_id))
        except:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid questionID'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:    
            if profile.pk != question.author.pk:
                raise ValidationError('You are not the author of this question.')
            
            if question.status == 'deleted':
                raise ValidationError('This question is already deleted.')

            all_answers = question.questionAnswer.all()
            if len(all_answers) > 0:
                raise ValidationError('You cannot delete this question, this question has been answered by users.')

        except Exception as e:
            response = {
                'message': 'Failed',
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
    
        # if not question.public:
        #     # payment = question.questionPayment.all().first()
        #     refund = Refund.objects.create(
        #                                     question_id = question, 
        #                                     # amount = payment.reward_amount + payment.service_charge,
        #                                     # currency = payment.currency,
        #                                     reason = 'Question deleted'
        #                                 )
            
        #     security_refund = SecurityRefund.objects.create(
        #                                     question_id = question,
        #                                     # amount = payment.security_amount,
        #                                     # currency = payment.currency,
        #                                     reason = 'Question deleted'
        #                                 )
            
        question.status = 'deleted'
        question.save()

        response = {
            'message': 'success',
            'body': [],
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
        
class EditQuestion(APIView):
    """
    edit questions 
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        question_content = request.data.get('question')
        question_id = request.data.get('question_id')
        category_id = request.data.get('category')

        try:
            keywords = request.data.getlist('keywords')
        except:
            keywords = request.data.get('keywords')

        answer_limit = int(request.data.get('answer_limit'))
        is_anonymous = request.data.get('is_anonymous')

        user = self.request.user
        profile = user.userAssociated.all().first()


        try:
            question = get_object_or_404(Question, pk=int(question_id))
        except:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid QuestionID'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:
            if question.author.pk != profile.pk:
                raise ValidationError("You are not the author of this question, you cannot edit this question.")

            all_answers = question.questionAnswer.all()
            if len(all_answers) > 0 and not question.public:
                raise ValidationError('You cannot delete this question, this question has been answered by users.')

            # if validity_days > MAX_VALIDITY_DAYS or validity_days < 1:
            #     raise ValidationError("Validity can be of maximum 30 days and minimum 1 day.")

            if len(question_content) > MAX_QUESTION_SIZE:
                raise ValidationError("Question can be of maximum 200 characters.")

            if answer_limit<MIN_ANSWER_LIMIT or answer_limit>MAX_ANSWER_LIMIT:
                raise ValidationError("Answer limit should be between {} and {}".format(MIN_ANSWER_LIMIT, MAX_ANSWER_LIMIT))

            category = Category.objects.filter(pk=int(category_id)).first()
            if category is None:
                raise ValidationError("Invalid category")

            keywords_array = []
            for i in range(len(keywords)):
                keyword_obj = Keywords.objects.filter(pk=int(keywords[i])).first()

                if keyword_obj is None:
                    raise ValidationError("Invalid Keyword ID {}".format(keywords[i]))
                    
                keywords_array.append(keyword_obj)
            
            question.keywords_associated.clear()

        except Exception as e:
            response = {
                'message': "Failed",
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        # valid_date = datetime.strptime(validity_date, '%d/%m/%Y').date()

        question.content = question_content
        question.category = category
        question.answer_limit = answer_limit
                
        question.keywords_associated.set(keywords_array)

        
        
        # payment_check = question.questionPayment.all().first()

        # if payment_check is None:
            # question.public = True
            # question.save()

            # reward_amount = int(reward_amount)

            # security_amount = SECURITY_AMOUNT_RATE*reward_amount/100
            # service_charge = SERVICE_CHARGE_RATE*reward_amount/100

            # PaymentStatus.objects.create(
                                        #     question_id = question,
                                        #     reward_amount = reward_amount,
                                        #     security_amount = security_amount,
                                        #     service_charge = service_charge,
                                        #     currency=currency,
                                        # )

        question.save()

        data = QuestionDetailSerializer(question).data

        response = {
            'message': 'Sucess',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetMyQuestions(APIView):
    """
    get all questions posted by the logged in user.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated.all().first()

        status = request.data.get('status')

        questions = profile.questionAuthor.all().filter(status=status)

        if questions:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(questions, request)
                data = QuestionDetailSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = QuestionDetailSerializer(questions, context={ 'request': request }, many=True).data

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

class AddBookmark(APIView):
    """
    simply add bookmark 
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated.all().first()

        question_id = request.data.get('question_id')

        try:
            question = get_object_or_404(Question, pk=int(question_id))
        except:
            response = {
                'message': 'Failed',
                'error': [
                    'Invalid Question Id'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        check_bookmark = BookmarkQuestion.objects.filter(question_id=question).filter(user_id=profile).first()

        if check_bookmark is None:
            BookmarkQuestion.objects.create(
                                            user_id = profile,
                                            question_id = question
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
        profile = user.userAssociated.all().first()

        all_bookmarks = profile.userBookmarked.all()
        
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

    def get(self, request, *args, **kwargs):
        search_text = request.data.get('text')

        questions = Question.objects.filter(content__icontains=search_text)
        data = OtherQuestionsSerializer(questions, context={ 'request': request }, many=True).data

        return Response({'questions':data}, status=HTTP_200_OK)

class GetQuestionByAnswer(APIView):
    """
    get question by answer ID
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
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

class SuggestQuestions(APIView):
    """
    suggest a question on the basis of a input text.
    NOTE: ordering on the basis of % match is left.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        search_text = request.data.get('text')

        questions = Question.objects.filter(content__icontains=search_text).filter(public=True)
        data = BriefQuestionSerializer(questions, context={ 'request': request }, many=True).data

        return Response({'questions':data}, status=HTTP_200_OK)



class GetQuestionsByCategory(APIView):
    """
    get questions by category 
    NOTE: sort_by unanswered, popular and price is remaining.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        category_id = request.data.get('category_id')
        status = request.data.get('status')
        sort_by = request.data.get('sort_by')
        sort_in = request.data.get('sort_in')

        user = self.request.user
        profile = user.userAssociated.all().first()

        try:
            category = get_object_or_404(Category, pk=int(category_id))
        except:
            response = {
                'message': 'Failed',
                'error': ['Invalid category ID'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        all_questions = Question.objects.filter(category=category)

        if status == 'private':
            all_questions = all_questions.filter(public=False)
        elif status == 'public':
            all_questions = all_questions.filter(public=True)
        
        if sort_by == 'new':
            if sort_in == 'increasing':
                all_questions.filter('created_date')
            else:
                all_questions.filter('-created_date')
        
        elif sort_by == 'validty_date':
            if sort_in == 'increasing':
                all_questions.filter('validty_date')
            else:
                all_questions.filter('-validty_date') 
        
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


# Get Question by Interests/myFeed remains

class LikeQuestion(APIView):
    """
    Toggle Likes
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated.all().first()

        question_id = request.data.get('question_id')

        try:
            question = get_object_or_404(Question, pk=int(question_id))
        except:
            response = {
                'message': 'Failed',
                'error': ['Invalid QuestionID'],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        get_Like = Like.objects.filter(user_id=profile).filter(question_id=question).first()

        if get_Like is None:
            message = "Liked"

            Like.objects.create(user_id=profile, question_id=question)
        else:
            get_Like.delete()
            message = "Removed from Like"
        
        response = {
            'message': message,
            'body': [],
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)



# def uservotes pending












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