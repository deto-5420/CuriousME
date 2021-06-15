from answers.models import Answer, UserLikes
from django.conf import settings
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.db.models import F
# from .serializers import AnonAnsSerializer
from notifications.signals import notify
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from collectanea.globals import sub_domain

@receiver(post_save, sender=Answer)
def update_total_response(sender, instance=None, created=False, **kwargs):
    """
    total_answers count for a user will be increased whenever a new 
    answer object is created, and will be decreased when admin deletes
    the answer.
    Category count will also be increased.
    """

    if created:
        # profile.total_responses += 1
        try:
            instance.question_id.category.answer_count += 1
            instance.question_id.category.save()
        except :
            pass
        
        instance.question_id.answer_count += 1
        instance.question_id.save()
        


    else:
        if instance.status == 'deleted':
            # profile.total_responses -= 1
            try:
                instance.question_id.category.answer_count -= 1
                instance.question_id.category.save()
            except :
                pass
            if instance.question_id.answer_count :
                instance.question_id.answer_count -= 1
                instance.question_id.save()


@receiver([post_save, post_delete], sender=UserLikes)
def answerLike(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.reaction_type in ('like','Like'):
            count=instance.answer.like_count +1
            Answer.objects.filter(id=instance.answer.id).update(like_count=count)
            

        else:
            
            count=instance.answer.dislike_count +1
            Answer.objects.filter(id=instance.answer.id).update(dislike_count=count)
            
        img=None
        try:
            img=instance.answer.user_id.avatar.url
        except:
            img=""
        data={
            'answerID':instance.answer.id,
            'questionID':instance.answer.question_id.id,
            'userID':instance.user.user.id,
            'username':instance.user.user.username,
            'profile_image': img
        }
        notify.send(sender=instance.user.user,recipient=instance.answer.user_id.user, verb=' Liked your Answer',data=data)
        # current_user = request.user # Getting current user
        channel_layer = get_channel_layer()
        data = json.dumps(data)
        # Trigger message sent to group
        async_to_sync(channel_layer.group_send)(
            f"{instance.answer.user_id.user.id}", {
                            "type": "user.answerlike",
                            "event": "Answer Liked",
                            "data": json.dumps(data)})  
        # print(data,notify)

    else:
        if instance.reaction_type in ('like','Like'):
            count=instance.answer.like_count -1
            Answer.objects.filter(id=instance.answer.id).update(like_count=count)
            

        else:
            
            count=instance.answer.dislike_count -1
            Answer.objects.filter(id=instance.answer.id).update(dislike_count=count)