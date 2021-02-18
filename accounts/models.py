from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from collectanea.globals import USER_STATUS

from questions.keywords_models import Keywords
from .validators import username_validator, bio_validator, avatar_validator

import requests

class UserManager(BaseUserManager):
    """
    Custom UserManager class
    """

    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, username, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(PermissionsMixin, AbstractBaseUser):
    """
    Custom user model.
    """

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(validators=[username_validator],max_length=1500)
    
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    # Permission fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_admin = models.BooleanField(default=False) # a superuser
    is_moderator = models.BooleanField(default=False) #access for server admin panel
    status = models.CharField(max_length=50, default="Activated", choices=USER_STATUS)

    # notice the absence of a "Password field", that's built in.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',] # Email & Password are required by default.


    def get_fullname(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def if_staff(self):
        "Is the user a member of staff?"
        return self.is_staff

    @property
    def if_admin(self):
        "Is the user a admin member?"
        return self.is_admin

    @property
    def if_active(self):
        "Is the user active?"
        return self.is_active

    @property
    def if_moderator(self):
        return self.is_moderator

    objects = UserManager()

class Websites(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=20)
    pair = models.URLField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = ['user_id', 'key', 'pair']
        verbose_name_plural = 'Websites'

    def __str__(self):
        return self.pair

class ProfessionList(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name 
     

class Profile(models.Model):
    """
    User Profile, linked to the User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userAssociated")
    fullname = models.CharField(max_length=2000, blank=True, null=True)
    avatar = models.ImageField(upload_to = 'Profiles/', blank=True, null=True, validators=[avatar_validator])  # User Profile Picture
    slug = models.SlugField(blank=True, null=True)
    bio = models.CharField(max_length=140, blank=True, null=True, validators=[bio_validator]) 
    MyInterest = models.ManyToManyField(Keywords, related_name="userInterests", blank=True)
    websites = models.ManyToManyField(Websites, related_name="userWebsites", blank=True)
    profession = models.ForeignKey(ProfessionList, on_delete=models.CASCADE, related_name='userProfession', null=True)
    followers_count = models.PositiveIntegerField(default=0)
    followings_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    

    class Meta:
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.fullname} - {self.user.email}' 

    def save(self, *args, **kwargs):
        self.slug = slugify( str(self.user.username) + self.fullname )
        # self.websites.user_id  = self.user.id
        super(Profile,self).save(*args,**kwargs)


class UserFollowing(models.Model):

    user_id = models.ForeignKey(Profile, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(Profile, related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("user_id", "following_user_id")
        ordering = ["-created"]

    def __str__(self):
        f"{self.user_id} follows {self.following_user_id}"