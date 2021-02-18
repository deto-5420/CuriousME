from django.contrib import admin
from .models import Category, Question, BookmarkQuestion, Like, UserVotes, Options, OptionVotes, QuestionMedia
from .keywords_models import Keywords
from import_export.admin import ImportExportModelAdmin


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'name')
	
@admin.register(Keywords)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'name')
admin.site.register(BookmarkQuestion)
admin.site.register(UserVotes)
admin.site.register(Like)

@admin.register(Options)
class OptionsAdmin(ImportExportModelAdmin):
	pass

admin.site.register(OptionVotes)
admin.site.register(QuestionMedia)

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'content','question_type', 'author', 'created_at', 'status')
    ordering = ('-created_at',)

