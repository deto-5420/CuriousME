import random
import string
from django.conf import settings
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.db.models import F

from rest_framework.authtoken.models import Token

from answers.models import Answer
from accounts.models import Profile,UserFollowing
from questions.models import Question, Category

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

#         if instance.is_active:
#             profile = Profile.objects.filter(user=instance).first()
    
#     if instance.status == 'Deleted' and instance.username[:7] != 'deleted':
#         deleted_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 4))    
#         deleted_suffix = deleted_suffix.join(random.choices(string.ascii_lowercase, k=2))
#         deleted_suffix += str(instance.pk)

#         instance.username = 'deleted<{}>'.format(deleted_suffix)
#         instance.save()


@receiver([post_save, post_delete], sender=UserFollowing)
def increment_follow_count(instance, created=False, **kwargs):
    if created:
        instance.user_id.followings_count += 1
        instance.following_user_id.followers_count += 1
        instance.user_id.save()
        instance.following_user_id.save()
        # Profile.objects.filter(
        #     user=instance.following_user_id
        # ).update(
        #     followers_count=F('followers_count') + 1
        # )
    else:
        instance.user_id.followings_count -= 1
        instance.following_user_id.followers_count -= 1
        instance.user_id.save()
        instance.following_user_id.save()
        # Profile.objects.filter(
        #     user=instance.user_id
        # ).update(
        #     followings_count=F('followings_count') -1
        # )
        # Profile.objects.filter(
        #     user=instance.following_user_id
        # ).update(
        #     followers_count=F('followers_count') -1
        # )

# @receiver(post_save, sender=Question)
# def update_total_questions(sender, instance=None, created=False, **kwargs):
#     """
#     total_questions count for a user will be increased whenever a new 
#     question object is created, and will be decreased when status of 
#     question is changed to 'Deleted'.
#     NOTE: we are also updating the processing_rate whenever status is
#           changed to 'processed' or 'admin_processed'
#     formula for processing_rate = (total_processed)/(total_processed + total_admin_processed)
#     Category count will also be increased.
#     """

#     profile = instance.author

#     if created:
#         profile.total_questions += 1
#         instance.category.total_questions += 1
#         instance.category.save()

#     else:
#         if instance.status == 'deleted':
#             profile.total_questions -= 1
#             instance.category.total_questions -= 1
#             instance.category.save()

#         elif instance.status == 'processed' or instance.status == 'admin_processed':
#             all_questions = profile.questionAuthor
#             total_processed = all_questions.filter(status='processed')
#             total_admin_processed = all_questions.filter(status='admin_processed')

#             processing_rate = total_processed/(total_processed + total_admin_processed)
#             profile.processing_rate = processing_rate
    
#     profile.save()

