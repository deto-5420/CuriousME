from django.db import models
from accounts.models import Profile
from questions.models import Question, Options
from answers.models import Answer
from replies.models import Replies
from collectanea.globals import MAX_QUESTION_SIZE, REQUEST_TYPE


class SpammedQuestion(models.Model):
    by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)

class SpammedAnswer(models.Model):
    by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)

class SpammedReply(models.Model):
    by = models.ForeignKey(Profile, on_delete=models.CASCADE)
    reply = models.ForeignKey(Replies, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)