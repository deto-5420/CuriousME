from django.contrib import admin
from .models import Replies,UserLikes, ReplyMedia
from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(Replies)
class RepliesAdmin(ImportExportModelAdmin):
	pass
admin.site.register(UserLikes)
admin.site.register(ReplyMedia)