from rest_framework import serializers

from .models import Replies,ReplyMedia ,UserLikes
from answers.serializers import AnswerSerializer
from accounts.profile_serializer import UserSerializer 
from collectanea.globals import sub_domain

class ReplyMediaSerializer(serializers.ModelSerializer):
    """
    Answer media serializer for files.
    """
    files=serializers.SerializerMethodField()

    class Meta:
        model = ReplyMedia
        fields = ['id','files', 'file_type']
    def get_files(self,obj):
        try:
            return obj.file.url
        except:
            return ""

class ReplySerializer(serializers.ModelSerializer):
    question_id=serializers.SerializerMethodField()
    user_id=serializers.SerializerMethodField()
    username=serializers.SerializerMethodField()
    userprofile=serializers.SerializerMethodField()
    media=serializers.SerializerMethodField()
    my_reaction=serializers.SerializerMethodField()
    content=serializers.SerializerMethodField()
    class Meta:
        model=Replies
        fields = [  
                    'id',
                    'content', 
                    'created_at', 
                    'status',
                    'question_id',
                    'like_count',
                    'dislike_count',
                    'user_id',
                    'username',
                    'userprofile',
                    'answer_id',
                    'media',
                    'my_reaction'
                    ]
    
    def get_question_id(self,obj):
        return obj.answer.question_id.id
    def get_user_id(self,obj):
        return obj.user_id.user.id
    def get_username(self,obj):
        return obj.user_id.user.username
    def get_userprofile(self,obj):
        try:
            return obj.user_id.avatar.url
        except:
            return ""
    def get_content(self,obj):
        if obj.status.lower()=='deleted':
            return "Deleted Reply"
        return obj.content
    def get_media(self,obj):
        all_media = obj.replyFiles.all()
        return ReplyMediaSerializer(all_media, many=True).data
    def get_my_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserLikes.objects.filter(user=user.userAssociated,reply=obj)
            if a.exists():
              
                return a.first().reaction_type
        except Exception as E:
            print(E)
            return None 

class BriefReplySerializer(serializers.ModelSerializer):
    my_reaction=serializers.SerializerMethodField()
    
    class Meta:
        model=Replies
        fields = [  
                    'id',
                    'content', 
                    'created_at', 
                    'status',
                    'like_count',
                    'dislike_count',
                    'my_reaction']
    def get_my_reaction(self,obj):
        try:
            user = self.context['request'].user
            profile = user.userAssociated
            a=UserLikes.objects.filter(user=user.userAssociated,reply=obj)
            if a.exists():
                return a.first().reaction_type

        except :
            return None 
