from django.db import models
from questions.models import Question
from accounts.models import Profile
from collectanea.globals import ANSWER_STATUS, REACTION_TYPE, SPAMMED_STATUS

class Answer(models.Model):
   
    
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="allAnswers")
    question_id = models.ForeignKey(Question, related_name="questionAnswer", on_delete=models.CASCADE)
    content = models.TextField()
    status = models.CharField(max_length=150, choices=ANSWER_STATUS, default='open')

    replies_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    reply_permission=models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = 'Answers'


    def like(self, user):
        try:
            self.Answer_like_count.create(user=user, question=self, vote_type="Like")
            self.like_count += 1
            self.save()                
        except IntegrityError:
            return 'already_liked'
        return 'ok'


    def dislike(self, user):
        try:
            self.Answer_dislike_count.create(user=user, question=self, vote_type="Dislike")
            self.dislike_count -= 1
            self.save()                
        except IntegrityError:
            return 'already_disliked'
        return 'ok'


    def __str__(self):
        return f'{self.user_id.fullname}'

class UserLikes(models.Model):
    user = models.ForeignKey(Profile, related_name="user_Likes_answers", on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name="answer_Likes", on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPE)
    created_at=models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name_plural = 'Likes'
        unique_together = ('user', 'answer', 'reaction_type')


def file_upload_path(instance, filename):
    return f'Answer/{instance.answer.pk}/{filename}'

class AnswerMedia(models.Model):
    """
    media files associated with the answer.
    """

    file = models.FileField(upload_to = file_upload_path )
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="answerFiles")
    file_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Answer Medias'

    def __str__(self):
        return self.answer.content


