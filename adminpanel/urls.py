from django.urls import path,include
from . import views	
from django.views.generic import TemplateView


app_name = 'adminpanel'

urlpatterns = [
	path('', views.index, name='index'),
	path('logout', views.logout_view, name='logout'),
	path('login', TemplateView.as_view(template_name='adminpanel/login.html'), name='login'),
	path('login_view', views.login_view, name='login_view'),
	path('user_management/<int:s_id>', views.user_management, name='user_management'),
	path('make_moderator/<int:u_id>', views.make_moderator, name='make_moderator'),
	path('make_user/<int:u_id>', views.make_user, name='make_user'),
	path('delete_user/<int:u_id>', views.delete_user, name='delete_user'),
	path('block_user/<int:u_id>', views.block_user, name='block_user'),
	path('activate_user/<int:u_id>', views.activate_user, name='activate_user'),

	path('get_questions/<int:s_id>', views.getQuestions, name='get_questions'),
	path('get_questions_by_category/<int:c_id>', views.getQuestionsByCategory, name="get_questions_by_category"),
	path('delete_question/<int:qid>', views.delete_question, name='delete_question'),
	path('retrieve_question/<int:qid>', views.retrieve_question, name='retrieve_question'),
	path('edit_question/<int:qid>', views.edit_question, name='edit_question'),

	path('delete_answer/<int:aid>', views.delete_answer, name='delete_answer'),
	path('retrieve_answer/<int:aid>', views.retrieve_answer, name='retrieve_answer'),

	path('delete_reply/<int:rid>', views.delete_reply, name='delete_reply'),
	path('retrieve_reply/<int:rid>', views.retrieve_reply, name='retrieve_reply'),

	path('answer/<int:qid>', views.answer, name='answer'),

	path('categories', views.categories, name='categories'),
	path('change_category_status/<int:id>/<int:c_id>', views.change_category_status, name='change_category_status'),
	path('create_category', views.create_category, name='create_category'),
	path('update_category/<int:id>', views.update_category, name='update_category'),

	path('spam_question', views.spam_question.as_view(), name="spam_question"),
	# path('spam_answer/<int:aid>', views.spam_answer, name="spam_answer"),
	# path('spam_reply/<int:rid>', views.spam_reply, name="spam_reply"),

	path('settings', views.settings, name='settings'),
]