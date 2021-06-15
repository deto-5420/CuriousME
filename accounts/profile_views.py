import requests
from collections import OrderedDict
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum, Avg, StdDev, Count
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404 
from django.core.mail import EmailMessage, send_mail
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone

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
from rest_framework.pagination import LimitOffsetPagination

from collectanea.globals import USER_STATUS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Profile, User ,Websites, UserFollowing,ProfessionList
from .profile_serializer import ProfileSerializer, ViewProfileSerializer,WebsitesSerializer,FollowingDetailSerializer,FollowerDetailSerializer,BriefProfileSerializer
from .tokens import account_activation_token
from questions.keywords_models import Keywords
from questions.models import *
from questions.serializers import BriefQuestionSerializer

from collectanea.permission import AuthorizedPermission
from .validators import username_validator, bio_validator, avatar_validator
from collectanea.global_checks import check_user_status


from datetime import datetime
import math

class UpdateInterests(APIView):
    """
    update profile interests
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def patch(self, request, *args, **kwargs):
        category = request.data.getlist('category')
        if len(category)< 6 or len(category) >30:
            return Response({"message":"the limit for category is 6-30"},status=400)
        user = self.request.user
        profile = user.userAssociated
        objs=Category.objects.filter(id__in=category)
        if len(objs)==len(category):
            profile.MyInterest.clear()
            for keys in objs:
                        profile.MyInterest.add(keys)
                        profile.save()
        else:
            for i in range(len(category)):
                try:
                    keyword = get_object_or_404(Category, pk=int(category[i]))
                except:
                    
                    response = {
                        'message': 'Invalid Keyword Id',
                        'error': ['ID {} does not exist'.format(keywords[i])],
                    }
                    return Response(response, status=HTTP_400_BAD_REQUEST)
            
        response = {
            'message': 'Interests updated successfully',
            'body':str([]),
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class GetMyProfile(APIView):
    """
    Get profile details 
    NOTE: their are some info that needs to be fetched from the stripe server.
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile = user.userAssociated

        data = ProfileSerializer(profile,context={"request":request}).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class EditProfile(APIView):
    """
    Edit username, fullname, IsAuthenticatedcountry, bio and Profile_image
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        fullname = request.data.get('fullname')
        profession = request.data.get('profession')
        prof_obj,created=ProfessionList.objects.get_or_create(name=profession)
        # if not prof_obj:
        #     response = {
        #         'message': 'Failed',
        #         'error': ['Inalid Profession'],
        #         'status': HTTP_400_BAD_REQUEST 
        #     }
        #     return Response(response, status=HTTP_400_BAD_REQUEST)
        bio = request.data.get('bio')
        avatar=request.FILES.get('avatar')
        # print(bio)
        user = self.request.user
        print(user)
        # profile = user.userAssociated.all().first()
        profile = Profile.objects.get(user = user)
        check_username = Profile.objects.filter(user__username = username).exclude(user=user)
        # print(check_username)
        if check_username:
            response = {
                'message': 'Failed',
                'error': ['Username already exists'],
                'status': HTTP_400_BAD_REQUEST 
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:
            username_validator(username)
            print(username_validator(username))
            bio_validator(bio)
            print(bio_validator(bio))

            profile.user.username = username
            profile.fullname = fullname
            profile.bio = bio
            profile.profession=prof_obj
            if avatar is not None:
                
                avatar_validator(avatar)
                profile.avatar = avatar

            profile.user.save()
            profile.save()

        except Exception as e:
            response = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST 
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        data = ViewProfileSerializer(profile,context={"request":request}).data
        response = {
            'message': 'Profile updated successfully',
            'body': data,
            'status': HTTP_200_OK 
        }
        return Response(response, status=HTTP_200_OK)

class GetUserProfile(APIView):
    """
    get user profile by userID
    """

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        userID = request.data.get('userID')
        user = self.request.user
        print(user)
        try:
            logged_profile = user.userAssociated
        except Exception as E:
            print(E)
        try:
            userID = int(userID)
            
            user=User.objects.get(id=userID)
            
            profile = get_object_or_404(Profile, user=user)
            
            if logged_profile.user.id== userID:
                 raise HTTPError

        except:
            response = {
                'message': 'Invalid Request',
                'error': [
                    'Invalid UserID'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        try:
            check_user_status(profile.user)
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
    
        data = ViewProfileSerializer(profile,context={"request":request}).data

        response = {
            'message': 'Success',
            'body': data,
            'status': HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

class AddUpdateUrl(APIView):
    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        
        # print(request.data)
        ID = request.data.get('Id')
        key=request.data.get('key')
        value=request.data.get('value')
        user_obj=self.request.user
        print(user_obj)
        web_obj=None
        try:
            check_user_status(user_obj)
        
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if ID:
            print(bool(ID))
            try:
                ID = int(ID)

                web_obj=get_object_or_404(Websites, pk=ID)
                web_obj.key=key
                web_obj.pair=value
                web_obj.updated_at=datetime.now()
                web_obj.save()
                data=WebsitesSerializer(web_obj).data
                return Response(data, status=HTTP_200_OK)
            except:
                response = {
                    'message': 'Invalid ID',
                    'error': [
                        'Invalid WebID'
                    ],
                    'status': HTTP_400_BAD_REQUEST
                }
                return Response(response, status=HTTP_400_BAD_REQUEST)
            
        else:
            if Websites.objects.filter(user_id=user_obj,key=key,pair=value).exists():
                return Response({"messages":"Cannot add the exact same url to profile"}, status=400)
            web_obj=Websites.objects.create(user_id=user_obj,key=key,pair=value)
            data=WebsitesSerializer(web_obj).data
            return Response(data, status=HTTP_200_OK)
    
        
class DeleteWebUrl(APIView):
    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        ID = request.data.get('Id')
        try:
            ID = int(ID)
            web_obj=get_object_or_404(Websites, pk=ID)
            if web_obj.user_id==request.user:
                web_obj.delete()
                return Response({"messages":"Successfully Deleted."}, status=HTTP_200_OK)
            else:
                return Response({"messages":"You can't delete others."}, status=400)
        except Exception as E:
            # print(E)
            response = {
                'message': 'Invalid Request',
                'error': [
                    'Invalid ID'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

class ToggleFollowingView(APIView):
    permission_classes = (IsAuthenticated, AuthorizedPermission)
    def post(self, request, *args, **kwargs):
        userID = request.data.get('userID')
        user = self.request.user
        print(userID,user)
        try:
            my_profile = user.userAssociated
            
        except Exception as e:
            response= {
                'message': 'Failed',
                'error': e,
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)

        followee_profile=None 
        try:
            userID = int(userID)

            user1=User.objects.get(id=userID)

            followee_profile = get_object_or_404(Profile, user=user1)
            
            if user.id == userID:
                raise HTTPError

        except Exception as E:
            print(E)
            response = {
                'message': 'Invalid Request',
                'error': [
                    'Invalid UserID'
                ],
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        try:
            check_user_status(user)
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        var=UserFollowing.objects.filter(user_id=my_profile,following_user_id=followee_profile)
        if var.exists():
            var.delete()
            return Response({"message":"Successfully unfollowed"}, status=HTTP_200_OK)
        else:
            var=UserFollowing.objects.create(user_id=my_profile,following_user_id=followee_profile)
            return Response({"message":"logged_profile Followed"}, status=HTTP_200_OK)

class GetFollowingsList(APIView):
    permission_classes = (IsAuthenticated, AuthorizedPermission)
    pagination_class = LimitOffsetPagination

    def get(self, request, *args, **kwargs):
        user = self.request.user
        try:
            my_profile = user.userAssociated
        except Exception as e:
            # print(e)
            response = {
                
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        #Following
        queryset1=UserFollowing.objects.filter(user_id=my_profile).select_related("following_user_id").prefetch_related("user_id__user","user_id__websites") 
        following_data=FollowingDetailSerializer(queryset1,context={"request":request},many=True).data
        if queryset1:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(queryset1, request)
                data = FollowingDetailSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = FollowingDetailSerializer(queryset1, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No Following found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)

#Followers

class GetFollowersList(APIView):

    permission_classes = (IsAuthenticated, AuthorizedPermission)
    pagination_class = LimitOffsetPagination
    def get(self, request, *args, **kwargs):
        user = self.request.user
        try:
            my_profile = user.userAssociated
        except Exception as e:
            response = {
                'message': 'Failed',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }
            return Response(response, status=HTTP_400_BAD_REQUEST)
        
        queryset1=UserFollowing.objects.filter(following_user_id=my_profile).select_related("user_id").prefetch_related("user_id__user","user_id__websites") 
        # following_data=FollowerDetailSerializer(queryset1,many=true).data
        if queryset1:
            try:
                paginator = LimitOffsetPagination()
                paginated_list = paginator.paginate_queryset(queryset1, request)
                data = FollowerDetailSerializer(paginated_list, context={ 'request': request }, many=True).data

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
                data = FollowerDetailSerializer(queryset1, context={ 'request': request }, many=True).data

                response = {
                    'message':'success',
                    'body':data,
                    'status':HTTP_200_OK
                }
                return Response(response, status=HTTP_200_OK)

        response = {
            'message':'No Follower found',
            'body':[],
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
class getPopularUsers(APIView):
    # permission_classes = (IsAuthenticated, AuthorizedPermission)
    def get(self, request, *args, **kwargs):
        user_obj=Profile.objects.all()
        user_z_scores = {}
        for user in user_obj:
            user_z_scores[user.id]=[]
            ans_obj=user.allAnswers.all()
            for ans in ans_obj:
                # ques=Question.objects.get(id=ids[0])
                user_likes=list(ans.answer_Likes.filter(reaction_type__in=("Like","like")).values('created_at').order_by('created_at').annotate(count=Count("created_at")))
                z_score=0
                if user_likes:
                    date_today = datetime.now(timezone.utc)
                    created_at = ans.created_at
                    most_recent_used = user_likes[-1]['created_at']
                    days_created_before = date_today-created_at
                    days_created_before = int(days_created_before.days)
                    not_used_days = days_created_before - len(user_likes)
                    if days_created_before>0:
                        avg_trend = len(user_likes)/(days_created_before)
                    else:
                        avg_trend = len(user_likes)

                    std_deviation = sum(((int(c['count']) - avg_trend) ** 2) for c in user_likes)
                    std_deviation += (((0-avg_trend)**2) * (not_used_days))

                    if days_created_before>0:
                        standard_deviation = math.sqrt(abs(std_deviation) / (days_created_before))
                    else:
                        standard_deviation = math.sqrt(abs(std_deviation))

                    standard_deviation = -1*standard_deviation if std_deviation<0 else standard_deviation

                    if most_recent_used-date_today == 0:            
                        current_trend = user_likes[-1]['count']
                    else:
                        current_trend=0

                    standard_deviation = 1 if standard_deviation==0 else standard_deviation
                    z_score = (current_trend-avg_trend)/standard_deviation
                    # z_scores[ques.id] = z_score
                user_z_scores[user.id].append(z_score)
            if len(user_z_scores[user.id]) :
                user_z_scores[user.id]=sum(user_z_scores[user.id])/len(user_z_scores[user.id])
            else:
                user_z_scores[user.id]=0

        sorted_users = OrderedDict(sorted(user_z_scores.items(), key = lambda kv:kv[1], reverse=True))
            
        positive_users = []
        for user in sorted_users:
            # if sorted_hashtags[hashtag]<0:
            #     break
            try:
                user_obj=Profile.objects.get(id=user)
                positive_users.append(user_obj)
            except:
                pass
        if not request.user.is_authenticated:
            try:
                top_n_hashtags = positive_users[:10]
            except:
                top_n_hashtags=positive_users
            data = BriefProfileSerializer(top_n_hashtags,context={"request":request}, many=True).data
            response = {
                'message':'success',
                'body':data,
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)
        else:
            if positive_users:
                try:
                    paginator = LimitOffsetPagination()
                    paginated_list = paginator.paginate_queryset(positive_users, request)
                    data = BriefProfileSerializer(paginated_list,{"request":request}, many=True).data

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
                    data = BriefProfileSerializer(positive_users,context={"request":request}, many=True).data

                    response = {
                        'message':'success',
                        'body':data,
                        'status':HTTP_200_OK
                    }
                    return Response(response, status=HTTP_200_OK)

            response = {
                'message':'No Popular User',
                'body':[],
                'status':HTTP_200_OK
            }
            return Response(response, status=HTTP_200_OK)

        
    
class getPopularQuestions(APIView):

    permission_classes = (IsAuthenticated, AuthorizedPermission)

    def post(self, request, *args, **kwargs):
        limit = request.data.get('limit')
        print(limit)
        ques_obj=Question.objects.all()
        z_scores = {}
        for ques in ques_obj:
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
        
        positive_question = []
        for ques in sorted_question:
            # if sorted_hashtags[hashtag]<0:
            #     break
            ques_obj=Question.objects.get(id=ques)
            positive_question.append(ques_obj)
        
        top_n_hashtags = positive_question[:int(limit)]
        data = BriefQuestionSerializer(top_n_hashtags,context={"request":request}, many=True).data

        response = {
            'message':'Success',
            'body':data,
            'status':HTTP_200_OK
        }
        return Response(response, status=HTTP_200_OK)
    
    
        





        # total=UserVotes.objects.filteraggregate(Sum('upvote_count'))
        # avg=Question.objects.aggregate(Avg('upvote_count'))
        # std_deviation=Question.objects.aggregate(StdDev('upvote_count'))
        # d=Question.objects.all().values_list("author").distinct() 
        # dict1={}
        # for obj_id in d:
        #     ques=Profile.objects.get(id=obj_id[0]).questionAuthor.all()
        #     z_score=[]
        #     for questions in ques:
        #         z.append((questions.upvote_count-avg)//std_deviation)
        #     z_avg=sum(z)//len(z)
        #     dict1[str(obj_id)]=z_avg
        
        # queryset=Profile.objects.filter(id__in=dict1["values"])
        
        

        # # hashtags = Hashtags.objects.all()

        # # if not country and country != 'global' and country != '':
        # #     hashtags = hashtags.filter(country=country)

        # # z_scores = {}
        # # for hashtag in hashtags:
        #     grouped_hashtags = list(Status.objects.filter(hashtags=hashtag).values('created_at').order_by('created_at').annotate()

        #     if grouped_hashtags:
        # date_today = datetime.now(timezone.utc)
        # created_at = hashtag.created_at
        # most_recent_used = grouped_hashtags[-1]['created_at']
        # days_created_before = date_today-created_at
        # days_created_before = int(days_created_before.days)

        #         not_used_days = days_created_before - len(grouped_hashtags)
        #         if days_created_before>0:
        #             avg_trend = hashtag.count/(days_created_before)
        #         else:
        #             avg_trend = hashtag.count

        #         std_deviation = sum(((int(c['count']) - avg_trend) ** 2) for c in grouped_hashtags)
        #         std_deviation += (((0-avg_trend)**2) * (not_used_days))

        #         if days_created_before>0:
        #             standard_deviation = math.sqrt(abs(std_deviation) / (days_created_before))
        #         else:
        #             standard_deviation = math.sqrt(abs(std_deviation))

        #         standard_deviation = -1*standard_deviation if std_deviation<0 else standard_deviation

        #         if most_recent_used-date_today == 0:            
        #             current_trend = grouped_hashtags[-1]['count']
        #         else:
        #             current_trend=0

        #         standard_deviation = 1 if standard_deviation==0 else standard_deviation
        #         z_score = (current_trend-avg_trend)/standard_deviation
        #         z_scores[hashtag] = z_score

        # sorted_hashtags = OrderedDict(sorted(z_scores.items(), key = lambda kv:kv[1], reverse=True))
        
        # positive_hashtags = []
        # for hashtag in sorted_hashtags:
        #     # if sorted_hashtags[hashtag]<0:
        #     #     break
        #     positive_hashtags.append(hashtag)
        
        # top_n_hashtags = positive_hashtags[:int(limit)]
        # data = HashtagsSerializer(top_n_hashtags, many=True).data

        # response = {
        #     'message':'Success',
        #     'body':data,
        #     'status':HTTP_200_OK
        # }
        # return Response(response, status=HTTP_200_OK)
    
    
        




