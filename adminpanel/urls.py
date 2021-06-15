from django.urls import path,include
from . import views	
from django.views.generic import TemplateView


app_name = 'adminpanel'

urlpatterns = [
	path('', views.index, name='index'),
	path('logout', views.logout_view, name='logout'),
	path('login', views.login_page, name='login'),
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
	path('approve_waiting/<int:qid>', views.approve_waiting, name='approve_waiting'),

	path('moderator_profile/<int:id>', views.moderator_profile, name='moderator_profile'),

	path('delete_answer/<int:aid>', views.delete_answer, name='delete_answer'),
	path('retrieve_answer/<int:aid>', views.retrieve_answer, name='retrieve_answer'),

	path('delete_reply/<int:rid>', views.delete_reply, name='delete_reply'),
	path('retrieve_reply/<int:rid>', views.retrieve_reply, name='retrieve_reply'),

	path('answer_page/<int:qid>', views.answer_page, name='answer'),
	path('answers/<int:qid>', views.answers, name='answers'),
	path('replies/<int:aid>', views.replies, name="replies"),
	path('question_detail/<int:qid>', views.question_detail, name='question_detail'),

	path('categories', views.categories, name='categories'),
	path('change_category_status/<int:id>/<int:c_id>', views.change_category_status, name='change_category_status'),
	path('create_category', views.create_category, name='create_category'),
	path('update_category/<int:id>', views.update_category, name='update_category'),

	path('spammed_questions/', views.spammed_questions.as_view(), name="spammed_questions"),
	path('spammed_questions/<int:qid>/<int:action>', views.spammed_questions.as_view(), name="spammed_question_action"),
	path('spammed_answers/', views.spammed_answers.as_view(), name="spammed_answers"),
	path('spammed_answers/<int:aid>/<int:action>', views.spammed_answers.as_view(), name="spammed_answer_action"),
	path('spammed_replies/', views.spammed_replies.as_view(), name="spammed_replies"),
	path('spammed_replies/<int:rid>/<int:action>', views.spammed_replies.as_view(), name="spammed_reply_action"),

	path('settings', views.settings, name='settings'),

	path('issues', views.issues, name='issues'),
	path('issue_action/<int:action>/<int:id>', views.issue_action, name='issue_action'),
]