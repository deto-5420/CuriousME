from django.conf import settings
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.db.models import F

from answers.models import Answer
from notifications.signals import notify
from .models import Replies,UserLikes
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from collectanea.globals import sub_domain

@receiver([post_save, post_delete], sender=UserLikes)
def my_handler(sender, instance=None, created=False, **kwargs):
    
    if created:
        if instance.reaction_type in ('like','Like'):
            count=instance.reply.like_count +1
            Replies.objects.filter(id=instance.reply.id).update(like_count=count)
            

        else:
            
            count=instance.reply.dislike_count +1
            Replies.objects.filter(id=instance.reply.id).update(dislike_count=count)
        img=None
        try:
            img=instance.reply.user_id.avatar.url
        except:
            img=""
        data={
            'answerID':instance.reply.answer.id,
            'questionID':instance.reply.answer.question_id.id,
            'userID':instance.reply.user_id.user.id,
            'username':instance.reply.user_id.user.username,
            'profile_image': img,
            'replyID':instance.reply.id
        }
        notify.send(sender=instance.user.user,recipient=instance.reply.user_id.user, verb=' Liked your Reply',data=data)
        # current_user = request.user # Getting current user
        channel_layer = get_channel_layer()
        data = json.dumps(data)
        # Trigger message sent to group
        async_to_sync(channel_layer.group_send)(
            f"{instance.reply.user_id.user.id}", {
                            "type": "user.like",
                            "event": " Reply Liked",
                            "data": json.dumps(data)})  
        
    else:
        if instance.reaction_type in ('like','Like'):
            count=instance.reply.like_count-1
            if count:
                Replies.objects.filter(id=instance.reply.id).update(like_count=count)
            

        else:
            
            count=instance.reply.dislike_count -1
            if count:
                Replies.objects.filter(id=instance.reply.id).update(dislike_count=count)

@receiver([post_save, post_delete], sender=Replies)
def increment_replies_count(sender,instance=None, created=False, **kwargs):
    if created:
        count=instance.answer.replies_count + 1
        Answer.objects.filter(id=instance.answer.id).update(replies_count=count)

        img=None
        try:
            img=instance.user_id.avatar.url
        except:
            img=""
        data={
            'replyID':instance.id,
            'answerID':instance.answer.id,
            'questionID':instance.answer.question_id.id,
            'userID':instance.user_id.user.id,
            'username':instance.user_id.user.username,
            'profile_image': img

        }
        notify.send(sender=instance.user_id.user,recipient=instance.answer.user_id.user, verb=' Replied ',data=data)
        
        channel_layer = get_channel_layer()
        data = json.dumps(data)
        # Trigger message sent to group
        async_to_sync(channel_layer.group_send)(
            f"{instance.user_id.user.id}", {
                            "type": "user.reply",
                            "event": "New_Reply",
                            "text": json.dumps(data)})  
        
    else:
        if instance.answer.replies_count:
            count=instance.answer.replies_count + 1
            Answer.objects.filter(id=instance.answer.id).update(replies_count=count)

