from django.contrib import admin
from .models import Answer, AnswerMedia, UserLikes
from import_export.admin import ImportExportModelAdmin

@admin.register(Answer)
class AnswerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'content')
	
admin.site.register(AnswerMedia)
admin.site.register(UserLikes)
