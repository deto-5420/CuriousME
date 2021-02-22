from django.urls import path,include
from django.views.generic import TemplateView
from . import views

app_name = 'moderator'
urlpatterns = [

	path('', views.index, name='moderator_panel'),
	path('question_form', views.add_question, name='question_form'),
	path('add_question', views.add_question, name='add_question'),
	path('add_poll', views.add_poll, name='add_poll'),
	# path('add_question', views.add_question, name='add_question'),
	path('edit_question/<int:qid>', views.edit_question, name='edit_question'),
	path('get_questions/<int:s_id>', views.getQuestions, name='get_questions'),

	path('category', views.categorypage, name='category'),
	path('get_questions_by_category/<int:c_id>', views.getQuestionsByCategory, name='get_questions_by_category'),

	path('nothing_here', TemplateView.as_view(template_name='moderatorpanel/nothing.html'), name='nothing_here'),

	path('login', TemplateView.as_view(template_name='moderatorpanel/login.html'), name='login'),
	path('login_view', views.login_view, name='login_view'),

	path('logout', views.logout_view, name='logout'),

	path('add_keyword', views.add_keyword, name = 'add_keyword'),

	path('delete_question/<int:qid>', views.delete_question, name = 'delete_question'),
	path('edit_question/<int:qid>', views.edit_question, name = 'edit_question'),

	path('answer_page/<int:qid>', views.answer_page, name='answer_page'),
	path('replies/<int:aid>', views.replies, name="replies"),

	path('return_keyword', views.return_keyword, name='return_keyword'),
]