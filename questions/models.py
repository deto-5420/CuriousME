from django.db import models
from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator

from collectanea.globals import ( 
                                MAX_QUESTION_SIZE, 
                                CATEGORY_STATUS, QUESTION_STATUS, VOTE_CHOICES, REQUEST_TYPE                            
                            )

from .keywords_models import Keywords

from datetime import datetime
import pytz 

# from misc.models import Choices

class Category(models.Model):
    """
    category of questions.
    """

    name = models.CharField(max_length=250, unique=True)
    status = models.CharField(max_length=100, choices=CATEGORY_STATUS)
    category_svg = models.FileField(upload_to='Categories/', blank=True, null=True)
    details = models.CharField(max_length=200)
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    total_questions = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(pytz.utc)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



class Question(models.Model):
    """
    questions table for paid and unpaid both.
    """

    author = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name="questionAuthor")
    content = models.CharField(max_length=MAX_QUESTION_SIZE) 
    status = models.CharField(max_length=50, choices=QUESTION_STATUS, default='waiting')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="questionCategory", null=True, blank=True)
    keywords_associated = models.ManyToManyField(Keywords, related_name="associatedKeywords", blank=True)

    like_count = models.PositiveIntegerField(default=0)
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)
    answer_count = models.PositiveIntegerField(default=0)

    question_type = models.CharField(max_length=10, default='Normal', choices=(('normal', 'Normal'), ('poll', 'Poll')))

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name_plural = 'Questions'


    def upvote(self, user):
        try:
            self.user_votes.create(user=user, question=self, vote_type="up")
            self.upvote_count += 1
            self.save()                
        except IntegrityError:
            return 'already_upvoted'
        return 'ok'


    def downvote(self, user):
        try:
            self.user_votes.create(user=user, question=self, vote_type="down")
            self.downvote_count -= 1
            self.save()                
        except IntegrityError:
            return 'already_downvoted'
        return 'ok'



    def __str__(self):
        return f'{self.author.fullname} - {self.content}'

    

class Options(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=50)
    vote = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    vote_percent = models.FloatField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
    
    class Meta:
        verbose_name_plural = "Options"

    def __str__(self):
        return self.choice 



class UserVotes(models.Model):
    user = models.ForeignKey('accounts.User', related_name="user_votes", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="question_votes", on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add = True)


    class Meta:
        verbose_name_plural = 'Votes'
        unique_together = ('user', 'question', 'vote_type')


class BookmarkQuestion(models.Model):
    """
    bookmark a question
    """

    user_id = models.ForeignKey('accounts.Profile', related_name="userBookmarked", on_delete=models.CASCADE)
    question_id = models.ForeignKey(Question, related_name="questionBookmarked", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name_plural = 'Bookmarked questions'

    def __str__(self):
        return f'{self.user_id.fullname} - {self.question_id.content}'


class Like(models.Model):
    """
    only Like and remove from Like allowed.
    NOTE: No Dislike allowed
    """

    user_id = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name="userLikes")
    question_id = models.ForeignKey(Question, related_name="questionLiked", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Like questions'

    def __str__(self):
        return f'{self.user_id.fullname} - {self.question_id.content}'


class OptionVotes(models.Model):
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Options, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question', 'option']

    def __str__(self):
        return f'{self.user.fullname} - {self.question.content} - {self.option.choice}'

def file_upload_path(instance, filename):
    return f'Question/{instance.question.pk}/{filename}'


class QuestionMedia(models.Model):
    """
    media files associated with the question.
    """

    file = models.FileField(upload_to = file_upload_path )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="questionFiles")
    file_type = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Question Medias'

    def __str__(self):
        return self.question.content