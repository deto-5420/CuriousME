from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password

from .models import Answer, AnswerMedia, UserLikes

from accounts.profile_serializer import ProfileSerializer
from collectanea.globals import sub_domain
# class AnswerPaymentSerializer(serializers.ModelSerializer):
#     """
#     serializer for payment object
#     """

#     class Meta:
#         model = AnswerPayments
#         fields = ['share', 'currency', 'created_date', 'payment_status']

  
    
    
class AnswerMediaSerializer(serializers.ModelSerializer):
    """
    Answer media serializer for files.
    """
    files=serializers.SerializerMethodField()
    class Meta:
        model = AnswerMedia
        fields = ['id','files', 'file_type']
    def get_files(self,obj):
        try:
            return obj.file.url
        except:
            return ""
class AnswerSerializer(serializers.ModelSerializer):
    """
    serializer for answer object
    including payments
    """

    # payment = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    user_id=serializers.SerializerMethodField()
    username=serializers.SerializerMethodField()
    userprofile=serializers.SerializerMethodField()
    question_id = serializers.SerializerMethodField()
    answer_id = serializers.SerializerMethodField()
    content=serializers.SerializerMethodField()
    replies_count=serializers.SerializerMethodField()
    my_reaction=serializers.SerializerMethodField()
    class Meta:
        model = Answer
        fields = [  
                    'user_id',
                    'username',
                    'userprofile',
                    'question_id', 
                    'content', 
                    'answer_id', 
                    'media', 
                    # 'payment', 
                    'status', 
                    'created_at',
                    'like_count',
                    'dislike_count',
                    'replies_count',
                    'my_reaction'
                ]
    
    # def get_payment(self, obj):
    #     pay_obj = obj.answerPayments.all()
    #     return AnswerPaymentSerializer(pay_obj, many=True).data
    def get_replies_count(self,obj):
        if obj.reply_permission:
            return obj.replies_count
        else:
            return 0
        return obj.user_id.user.id
    def get_user_id(self,obj):
        return obj.user_id.user.id
    def get_username(self,obj):
        return obj.user_id.user.username
    def get_userprofile(self,obj):
        try:
            return obj.user_id.avatar.url
        except:
            return ""
    def get_media(self, obj):
        all_media = obj.answerFiles.all()
        return AnswerMediaSerializer(all_media, many=True).data
    
    def get_question_id(self, obj):
        return obj.question_id.pk
    
    def get_answer_id(self, obj):
        return obj.pk
    def get_content(self,obj):
        if obj.status in ('Deleted',"deleted"):
            return "Deleted Answer"
        return obj.content
    def get_my_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserLikes.objects.filter(user=user.userAssociated,answer=obj)
            if a.exists():
                return a.first().reaction_type
        except :
            return None

    # def get_reactions(self, obj):
    #     total_reactions = obj.questionReactions.all()
    #     total_likes = total_reactions.filter(reaction_type='Like').count()
    #     total_dislikes = total_reactions.filter(reaction_type='Dislike').count()

    #     user_profile = self.context['request'].user.userAssociated.all().first()
    #     my_reaction = total_reactions.filter(user_id=user_profile).first()

    #     if my_reaction is not None:
    #         my_react = my_reaction.status
    #     else:
    #         my_react= ""

    #     return {
    #             'total_likes': total_likes,
    #             'total_dislikes': total_dislikes,
    #             'my_reaction': my_react
    #         }
class AnsSerializer(serializers.Serializer):
    media = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    username= serializers.SerializerMethodField()
    AnswerId = serializers.SerializerMethodField()
    Answer=serializers.SerializerMethodField()
    profileURL=serializers.SerializerMethodField()
    replies_count=serializers.SerializerMethodField()
    my_reaction=serializers.SerializerMethodField()
    like_count=serializers.SerializerMethodField()
    dislike_count=serializers.SerializerMethodField()
    def get_dislike_count(self,obj):
        return obj.dislike_count
    def get_like_count(self,obj):
        return obj.like_count
    def get_profileURL(self,obj):
        try:
            return  obj.user_id.avatar.url
        except:
            return "None"
    def get_user_id(self,obj):
        return obj.user_id.user.id
    def get_username(self,obj):
        return obj.user_id.user.username
    def get_AnswerId(self,obj):
        return obj.id
    def get_Answer(self,obj):
        return obj.content 
    def get_media(self, obj):
        all_media = obj.answerFiles.all()
        return AnswerMediaSerializer(all_media, many=True).data
    def get_replies_count(self,obj):
        if obj.reply_permission:
            return obj.replies_count
        else:
            return 0
    def get_my_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserLikes.objects.filter(user=user.userAssociated,answer=obj)
            if a.exists():
                return a.first().reaction_type

        except:
            return None 
