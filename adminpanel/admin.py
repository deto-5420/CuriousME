from django.contrib import admin
from .models import SpammedQuestion, SpammedAnswer, SpammedReply
# Register your models here.

admin.site.register(SpammedQuestion)
admin.site.register(SpammedAnswer)
admin.site.register(SpammedReply)
