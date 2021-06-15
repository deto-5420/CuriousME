from django.db import models
from answers.models import Answer
from accounts.models import Profile
from collectanea.globals import SPAMMED_STATUS, ANSWER_STATUS,REACTION_TYPE

def file_upload_path(instance, filename):
    return f'Replies/Public/{instance.reply.pk}/{filename}'

class Replies(models.Model):

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="AnswerReplies")
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="UserReplied")
    content = models.TextField()
    # file = models.FileField(upload_to = file_upload_path)
    status = models.CharField(max_length=150, choices=ANSWER_STATUS, default='open')

    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = 'Replies'

    def like(self, user):
        try:
            self.Replies_like_count.create(user=user, answer=self, vote_type="Like")
            self.like_count += 1
            self.save()                
        except IntegrityError:
            return 'already_liked'
        return 'ok'


    def dislike(self, user):
        try:
            self.Replies_dislike_count.create(user=user, answer=self, vote_type="Dislike")
            self.dislike_count -= 1
            self.save()                
        except IntegrityError:
            return 'already_disliked'
        return 'ok'

    def __str__(self):
        return f'{self.user_id.fullname}'

class ReplyMedia(models.Model):
    """
    media files associated with the reply.
    """

    file = models.FileField(upload_to = file_upload_path )
    reply = models.ForeignKey(Replies, on_delete=models.CASCADE, related_name="replyFiles")
    file_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Reply Medias'

    def __str__(self):
        return self.reply.answer_id.content

class UserLikes(models.Model):
    user = models.ForeignKey(Profile, related_name="user_Likes_replies", on_delete=models.CASCADE)
    reply = models.ForeignKey(Replies, related_name="replies_Likes", on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPE)
        
    class Meta:
        verbose_name_plural = 'Likes'
