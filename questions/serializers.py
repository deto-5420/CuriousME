from datetime import datetime 

from rest_framework import serializers

from .models import Question, BookmarkQuestion ,UserVotes, Category, Options,QuestionMedia, Like
from .keywords_serializers import KeyWordsSerializer, CategorySerializer
from answers.serializers import AnsSerializer
from answers.models import *
from accounts.models import UserFollowing
from replies.models import Replies
from replies.serializers import BriefReplySerializer
from collectanea.globals import sub_domain

class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    includes upvotes and responses
    """

    keywords = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()
    Options=serializers.SerializerMethodField()
    Answer=serializers.SerializerMethodField()
    Attachment=serializers.SerializerMethodField()
    is_bookmarked=serializers.SerializerMethodField()
    reaction=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields =[  
                    'id',
                    'content', 
                    'question_type',
                    'created_at', 
                    'status', 
                    'category', 
                    # 'payment',
                    'keywords',
                    'upvote_count',
                    'Attachment',
                    'downvote_count',
                    'answer_count',
                    'is_upvoted',
                    'Options',
                    'Answer',
                    'is_bookmarked',
                    'reaction',
                    'like_count',
                    'is_liked'
                ]

    # def get_payment(self, obj):
    #     if obj.public:
    #         payment_obj = obj.questionPayment.all()
    #         return PaymentStatusSerializer(payment_obj, many=True).data
        
    def get_keywords(self, obj):
        return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data
    def get_category(self,obj):
        return CategorySerializer(obj.category).data
    
    # def get_upvotes(self, obj):
    #     return obj.questionUpvoted.all().count()
    def get_Attachment(self,obj):
        objs=obj.questionFiles.all()
        data=MediaSerializer(objs,many=True).data
        return data
    def get_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserVotes.objects.filter(user=user,question=obj)
            if a.exists():
                return a.first().vote_type
            return " "
        except:
            return None 
    def get_is_upvoted(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if UserVotes.objects.filter(user=user,question=obj,vote_type__in=("Upvote","upvote")).exists():
                return "True"
            return "False"
        except:
            return None 
    def get_is_liked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if Like.objects.filter(user_id=profile,question_id=obj).exists():
                return "True"
            return "False"
        except:
            return None 
    def get_Options(self,obj):
        return OptionSerializer(Options.objects.filter(question=obj),many=True).data
        # if is_upvoted is None:
        #     return False
        # return True
    def get_Answer(self,obj):
        try:
            user = self.context['request'].user
            profile=user.userAssociated
            following=profile.following.all()
            if following.exists():
                all_answer=Answer.objects.filter(question_id=obj)
                following_answer=all_answer.filter(user_id__in=following)
                ids=[]
                for var in following_answer:
                    if var.reply_permission:
                        ids.append(var.id)
                all_reply=Replies.objects.filter(user_id__in=following,answer__in=all_answer)
                reply_only=all_reply.exclude(answer__id__in=ids).values_list("answer")
                reply_only_answer=Answer.objects.filter(id__in=reply_only)

                if following_answer or reply_only_answer:
                    data1=AnsSerializer(following_answer,many=True,context=self.context).data
                    data2=AnsSerializer(reply_only_answer,many=True,context=self.context).data
                    data=data1 +data2
                    return data
        except:
            
            objs=obj.questionAnswer.all().order_by("-like_count")
            obj=objs.first()
            return AnsSerializer(obj,context=self.context).data
    
    def get_is_bookmarked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if BookmarkQuestion.objects.filter(user_id=profile,question_id=obj).exists():
                return "True"
            return "False"
        except:
            return None 


class BookmarksSerializer(serializers.ModelSerializer):
    """
    using question deatil serializer. 
    """

    question = serializers.SerializerMethodField()
    # is_liked = serializers.SerializerMethodField()

    class Meta:
        model = BookmarkQuestion
        fields = ['question','created_at']

    def get_question(self, obj):
        
        context=self.context
        print(context,context['request'].user,type(obj.question_id),type(obj.question_id.category))
        ser=OtherQuestionsSerializer(obj.question_id, context=context).data
        # print(ser.is_valid())
        return  ser
            
        
        
    
    # def get_is_upvoted(self, obj):
    #     user = self.context['request'].user
    #     profile = user.userAssociated
    #     if UserVotes.objects.filter(user=user,question=obj.question_id,vote_type__in=("Upvote","upvote")).exists():
    #         return "True"
    #     return "False"
    

class OtherQuestionsSerializer(serializers.ModelSerializer):
    """
    includes is_upvoted.
    """

    # payment = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()
    Options=serializers.SerializerMethodField()
    Answer=serializers.SerializerMethodField()
    Attachment=serializers.SerializerMethodField()
    is_bookmarked=serializers.SerializerMethodField()
    reaction=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
                'id',
                'content', 
                'created_at', 
                'status', 
                'question_type',
                'category', 
                # 'payment',
                'keywords',
                'upvote_count',
                'Attachment',
                'downvote_count',
                'answer_count',
                'is_upvoted',
                'Options',
                'Answer',
                'is_bookmarked',
                'reaction',
                'like_count',
                'is_liked'
            ]

    # def get_payment(self, obj):
    #     if obj.public:
    #         payment_obj = obj.questionPayment.all()
    #         return PaymentStatusSerializer(payment_obj, many=True).data
        
    def get_keywords(self, obj):
        return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data
    def get_category(self,obj):
        return CategorySerializer(obj.category).data
    
    # def get_upvotes(self, obj):
    #     return obj.questionUpvoted.all().count()
    def get_Attachment(self,obj):
        objs=obj.questionFiles.all()
        data=MediaSerializer(objs,many=True).data
        return data
    def get_reaction(self,obj):
        try:
            user = self.context['request'].user
            a=UserVotes.objects.filter(user=user,question=obj)

            if a.exists():
                return a.first().vote_type
            return " "
        except:
            return None 
    def get_is_upvoted(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if UserVotes.objects.filter(user=user,question=obj,vote_type__in=("Upvote","upvote")).exists():
                return "True"
            return "False"
        except:
            return None
    def get_is_liked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if Like.objects.filter(user_id=profile,question_id=obj).exists():
                return "True"
            return "False"
        except:
            return None
    def get_Options(self,obj):
        return OptionSerializer(Options.objects.filter(question=obj),many=True).data
        # if is_upvoted is None:
        #     return False
        # return True
    def get_Answer(self,obj):
        
        if obj.question_type in ('normal', 'Normal'):
            user = self.context['request'].user
            profile=user.userAssociated
            following=profile.following.all().values_list('following_user_id')
            if following.exists():
                all_answer=Answer.objects.filter(question_id=obj)
                following_answer=all_answer.filter(user_id__in=following).order_by("-like_count","-id")
                ids=[]
                for var in following_answer:

                    if var.reply_permission:
                        ids.append(var.id)
                all_reply=Replies.objects.filter(user_id__in=following,answer__in=all_answer)
                reply_only=all_reply.exclude(answer__id__in=ids).values_list("answer")
                reply_only_answer=Answer.objects.filter(id__in=reply_only).order_by("-like_count","-id")

                if following_answer or reply_only_answer:
                    data=[]
                    data1=AnsSerializer(following_answer.first(),context=self.context).data
                    if data1:
                        data.append(data1)
                    data2=AnsSerializer(reply_only_answer.first(),context=self.context).data
                    if data2:
                        data.append(data2)
                    return data
                
            objs=obj.questionAnswer.all().order_by("-like_count")
            obj=objs.first()
            return AnsSerializer(obj,context=self.context).data
        else:
            return None 

    def get_is_bookmarked(self, obj):
        user = self.context['request'].user
        profile = user.userAssociated
        if BookmarkQuestion.objects.filter(user_id=profile,question_id=obj).exists():
            return "True"
        return "False"

class AnonQuestionsSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    Options=serializers.SerializerMethodField()
    Answer=serializers.SerializerMethodField()
    Attachment=serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = [  
                    'id',
                    'content', 
                    'created_at', 
                    'status',
                    'question_type',
                    'category', 
                    # 'payment',
                    'keywords',
                    'upvote_count',
                    'Attachment',
                    'downvote_count',
                    'answer_count',
                    'Options',
                    'Answer',
                    'like_count']

    # def get_payment(self, obj):
    #     if obj.public:
    #         payment_obj = obj.questionPayment.all()
    #         return PaymentStatusSerializer(payment_obj, many=True).data
        
    def get_keywords(self, obj):
        return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data
    def get_category(self,obj):
        return CategorySerializer(obj.category).data
    
    # def get_upvotes(self, obj):
    #     return obj.questionUpvoted.all().count()
    def get_Attachment(self,obj):
        objs=obj.questionFiles.all()
        data=MediaSerializer(objs,many=True).data
        return data

    
    def get_Options(self,obj):
        return OptionSerializer(Options.objects.filter(question=obj),many=True).data
        # if is_upvoted is None:
        #     return False
        # return True
    def get_Answer(self,obj):
        
        objs=obj.questionAnswer.all().order_by("-like_count")
        obj=objs.first()
        return AnsSerializer(obj).data

    

class BriefQuestionSerializer(serializers.ModelSerializer):
    """
    only id and content
    """

    class Meta:
        model = Question
        fields = ['pk', 'content']


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Category
#         fields=["id","name","category_svg"]
#     def get_id(self,obj):
#         return obj.id
class OptionSerializer(serializers.Serializer):
    id= serializers.SerializerMethodField()
    option_name=serializers.SerializerMethodField()
    option_percentage=serializers.SerializerMethodField()
    def get_id(self,obj):
        return obj.id
    def get_option_name(self,obj):
        return obj.choice
    def get_option_percentage(self,obj):
        return obj.vote_percent


class MediaSerializer(serializers.Serializer):
    ID=serializers.SerializerMethodField()
    file_type=serializers.SerializerMethodField()
    URL=serializers.SerializerMethodField()
    def get_ID(self,obj):
        return obj.id
    def get_URL(self,obj):
        try:
            return obj.file.url
        except:
            return " "
    def get_file_type(self,obj):
        return obj.file_type


class LikedAnswerSerializer(serializers.Serializer):
    keywords = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()
    Options=serializers.SerializerMethodField()
    Answer=serializers.SerializerMethodField()
    Attachment=serializers.SerializerMethodField()
    is_bookmarked=serializers.SerializerMethodField()
    reaction=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    upvote_count=serializers.SerializerMethodField()
    like_count=serializers.SerializerMethodField()
    downvote_count=serializers.SerializerMethodField()
    answer_count=serializers.SerializerMethodField()
   
    def get_upvote_count(self,obj):
        return obj.question_id.upvote_count
    def get_downvote_count(self,obj):
        return obj.question_id.downvote_count
    def get_answer_count(self,obj):
        return obj.question_id.answer_count
    
    def get_like_count(self,obj):
        return obj.question_id.like_count
    def get_keywords(self, obj):
        return KeyWordsSerializer(obj.question_id.keywords_associated.all(), many=True).data
    def get_category(self,obj):
        return CategorySerializer(obj.question_id.category).data
    
    # def get_upvotes(self, obj):
    #     return obj.questionUpvoted.all().count()
    def get_Attachment(self,obj):
        objs=obj.question_id.questionFiles.all()
        data=MediaSerializer(objs,many=True).data
        return data
    def get_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserVotes.objects.filter(user=user,question=obj.question_id)
            if a.exists():
                return a.first().vote_type
            return " "
        except:
            return None
    def get_is_upvoted(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if UserVotes.objects.filter(user=user,question=obj.question_id,vote_type__in=("Upvote","upvote")).exists():
                return "True"
            return "False"
        except:
            return None 
    def get_is_liked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if Like.objects.filter(user_id=profile,question_id=obj.question_id).exists():
                return "True"
            return "False"
        except:
            return None 
    def get_Options(self,obj):
        return OptionSerializer(Options.objects.filter(question=obj.question_id),many=True).data
        # if is_upvoted is None:
        #     return False
        # return True
    def get_Answer(self,obj):

        if obj.question_id.question_type in ('normal', 'Normal'):
            return AnsSerializer(obj,context=self.context).data
        else:
            return None 

    def get_is_bookmarked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if BookmarkQuestion.objects.filter(user_id=profile,question_id=obj.question_id).exists():
                return "True"
            return "False"
        except:
            return None 

class LikedReplySerializer(serializers.Serializer):
    keywords = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()
    Options=serializers.SerializerMethodField()
    Answer=serializers.SerializerMethodField()
    Attachment=serializers.SerializerMethodField()
    is_bookmarked=serializers.SerializerMethodField()
    reaction=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    upvote_count=serializers.SerializerMethodField()
    like_count=serializers.SerializerMethodField()
    downvote_count=serializers.SerializerMethodField()
    answer_count=serializers.SerializerMethodField()
    reply=serializers.SerializerMethodField()
    def get_upvote_count(self,obj):
        return obj.answer.question_id.upvote_count
    def get_downvote_count(self,obj):
        return obj.answer.question_id.downvote_count
    def get_answer_count(self,obj):
        return obj.answer.question_id.answer_count
    
    def get_like_count(self,obj):
        return obj.answer.question_id.like_count
    def get_keywords(self, obj):
        return KeyWordsSerializer(obj.answer.question_id.keywords_associated.all(), many=True).data
    def get_category(self,obj):
        return CategorySerializer(obj.answer.question_id.category).data
    
    # def get_upvotes(self, obj):
    #     return obj.questionUpvoted.all().count()
    def get_Attachment(self,obj):
        objs=obj.answer.question_id.questionFiles.all()
        data=MediaSerializer(objs,many=True).data
        return data
    def get_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserVotes.objects.filter(user=user,question=obj.answer.question_id)
            if a.exists():
                return a.first().vote_type
            return " "
        except:
            return None
    def get_is_upvoted(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if UserVotes.objects.filter(user=user,question=obj.answer.question_id,vote_type__in=("Upvote","upvote")).exists():
                return "True"
            return "False"
        except:
            return None 
    def get_is_liked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if Like.objects.filter(user_id=profile,question_id=obj.answer.question_id).exists():
                return "True"
            return "False"
        except:
            return None 
    def get_Options(self,obj):
        return OptionSerializer(Options.objects.filter(question=obj.answer.question_id),many=True).data
        # if is_upvoted is None:
        #     return False
        # return True
    def get_Answer(self,obj):

        if obj.answer.question_id.question_type in ('normal', 'Normal'):
            return AnsSerializer(obj.answer,context=self.context).data
        else:
            return None 

    def get_is_bookmarked(self, obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            if BookmarkQuestion.objects.filter(user_id=profile,question_id=obj.answer.question_id).exists():
                return "True"
            return "False"
        except:
            return None    
    def get_reply(self,obj):
        return BriefReplySerializer(obj,context=self.context).data
# class QuestionSerializer(serializers.ModelSerializer):
#     """
#     question serializer + payment status
#     """

#     # payment = serializers.SerializerMethodField()
#     keywords = serializers.SerializerMethodField()
#     category = serializers.SerializerMethodField()
#     Attachment=serializers.SerializerMethodField()
#     Options=serializers.SerializerMethodField()
#     Answer=serializers.SerializerMethodField()
#     is_bookmarked=serializers.SerializerMethodField()
#     class Meta:
#         model = Question
#         fields = [
#                     'content', 
#                     'created_at', 
#                     'status', 
#                     'Attachment',
#                     'category', 
#                     'keywords',
#                     'Options',
#                     'Answer',
#                     'is_bookmarked'
#                 ]

#     # def get_payment(self, obj):
#     #     if obj.public:
#     #         payment_obj = obj.questionPayment.all()
#     #         return PaymentStatusSerializer(payment_obj, many=True).data
#     # def get_created_date(self,obj):
#     #     return datetime.now()    
#     def get_keywords(self, obj):
#         return KeyWordsSerializer(obj.keywords_associated.all(), many=True).data
    
#     def get_category(self,obj):
#         return CategorySerializer(obj.category).data
#     def get_Attachment(self,obj):
#         objs=obj.questionFiles.all()
#         data=MediaSerializer(objs,many=True).data
#         return data
#     def get_Options(self,obj):
#         return OptionSerializer(Options.objects.filter(question=obj),many=True).data
#         # if is_upvoted is None:
#         #     return False
#         # return True
#     def get_Answer(self,obj):
#         objs=obj.questionAnswer.all().order_by("-like_count")
#         obj=objs.first()
#         return AnsSerializer(obj).data
#     def get_is_bookmarked(self, obj):
#         user = self.context['request'].user
#         profile = user.userAssociated
#         if BookmarkQuestion.objects.filter(user_id=profile,question_id=obj).exists():
#             return True
#         return False

