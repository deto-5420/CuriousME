from django.shortcuts import render, redirect, get_object_or_404
from questions.models import Question, Options, QuestionMedia, Category, BookmarkQuestion
from questions.keywords_models import Keywords
from accounts.models import User, Profile
from adminpanel.models import SpammedAnswer, SpammedQuestion, SpammedReply
from answers.models import Answer
from replies.models import Replies
from collectanea.globals import MAX_MEDIA_ALLOWED, MAX_MEDIA_SIZE, ALLOWED_FILE_FORMATS
from misc.models import  ReportIssue

from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from questions.forms import QuestionForm, OptionForm, QuestionMediaForm
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.formsets import formset_factory
from django.forms import inlineformset_factory

from dynamic_preferences.forms import global_preference_form_builder
from dynamic_preferences.registries import global_preferences_registry

from .forms import CategoryForm
import collectanea.globals as limits
from collectanea.global_checks import user_is_active

from django.db.models import Q

# Create your views here.

def check_user_active(request):
	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('adminpanel:login'))


def login_page(request):
	if request.user.is_authenticated and (request.user.is_staff or request.user.is_admin):
		return HttpResponseRedirect(reverse('adminpanel:index'))
	return render(request, 'adminpanel/login.html')


def login_view(request):
	if not request.method == 'POST':
		messages.error(request, 'Not a POST request')
		return HttpResponseRedirect(reverse('adminpanel:login'))

	email = request.POST['email'].lower()
	password = request.POST['password']
	UserModel = get_user_model()

	try:
		user = UserModel.objects.get(email=email)
		if not user.is_staff:
			messages.warning(request, 'You are not an Admin')
			return HttpResponseRedirect(reverse('adminpanel:login'))

		if not user.is_active:
			messages.warning(request, 'Your account is deactivated. Contact administrator.')
			return HttpResponseRedirect(reverse('adminpanel:login'))

		if user.check_password(password):
			usr_dict = UserModel.objects.filter(email=email).values().first()
			usr_dict.pop('password')
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			return HttpResponseRedirect(reverse('adminpanel:index'))
		else:
			messages.error(request, 'Invalid password')
			return HttpResponseRedirect(reverse('adminpanel:login'))

	except UserModel.DoesNotExist:
		messages.error(request, 'Invalid email')
		return HttpResponseRedirect(reverse('adminpanel:login'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def index(request):

	check_user_active(request)
	profile = Profile.objects.get(user = request.user)

	total_users = User.objects.filter(is_admin = False, is_staff = False, is_moderator = False).count()
	total_active_users = User.objects.filter(is_active = True, is_admin = False, is_staff = False, is_moderator = False).count()
	total_blocked_users = User.objects.filter(status = 'Blocked', is_admin = False, is_staff = False, is_moderator = False).count()
	total_deleted_users = User.objects.filter(status = 'Deleted', is_admin = False, is_staff = False, is_moderator = False).count()
	total_moderators = User.objects.filter(is_moderator = True, is_active = True).count()
	
	total_open_questions = Question.objects.filter(status = 'open').count()
	total_waiting_questions = Question.objects.filter(status = 'waiting').count()
	total_pending_questions = Question.objects.filter(status = 'pending').count()
	total_deleted_questions = Question.objects.filter(status = 'deleted').count()

	total_categories = Category.objects.filter(status = 'Active').count()

	total_spammed_questions = SpammedQuestion.objects.all().count()
	total_spammed_answers = SpammedAnswer.objects.all().count()
	total_spammed_replies = SpammedReply.objects.all().count()

	for_front = {
		'profile':profile,
		'total_users':total_users,
		'total_active_users':total_active_users,
		'total_blocked_users':total_blocked_users,
		'total_deleted_users':total_deleted_users,
		'total_moderators':total_moderators,

		'total_open_questions':total_open_questions,
		'total_waiting_questions':total_waiting_questions,
		'total_pending_questions':total_pending_questions,
		'total_deleted_questions':total_deleted_questions,

		'total_categories':total_categories,

		'total_spammed_questions':total_spammed_questions,
		'total_spammed_answers':total_spammed_answers,
		'total_spammed_replies':total_spammed_replies,
	}
	return render(request, 'adminpanel/index.html', for_front)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def user_management(request, s_id):

	check_user_active(request)

	if s_id == 1:
		profile = User.objects.filter(status = "Activated")
		users = Profile.objects.filter(user__id__in = profile.all()).order_by('id')

	elif s_id == 2:
		profile = User.objects.filter(status = "Blocked")
		users = Profile.objects.filter(user__id__in = profile.all()).order_by('id')

	elif s_id == 3:
		profile = User.objects.filter(status = "Deleted")
		users = Profile.objects.filter(user__id__in = profile.all()).order_by('id')

	else:
		users = Profile.objects.all().order_by('id')

	paginator = Paginator(users, 10)
	page_number = request.GET.get('page')

	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)


	for_front = {
		'users':page_obj,
	}
	return render(request, 'adminpanel/user_management.html', for_front)


@login_required(login_url = 'adminpanel:login')
def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('adminpanel:login'))	

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def make_moderator(request, u_id):
	check_user_active(request)
	profile = Profile.objects.get(id = u_id)
	user = User.objects.get(id = profile.user.id)
	print(user)
	user.is_moderator = True
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def make_user(request, u_id):
	check_user_active(request)
	profile =  Profile.objects.filter(id=u_id).select_related('user').get()
	user = profile.user
	print(user)
	user.is_moderator = False
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_user(request, u_id):
	check_user_active(request)
	profile =  Profile.objects.filter(id=u_id).select_related('user').get()
	user = profile.user
	print(user)
	user.is_active = False
	user.status = 'Deleted'
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def block_user(request, u_id):
	check_user_active(request)
	profile =  Profile.objects.filter(id=u_id).select_related('user').get()
	user = profile.user
	print(user)
	user.is_active = False
	user.status = 'Blocked'
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	 
@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def activate_user(request, u_id):
	check_user_active(request)
	profile =  Profile.objects.filter(id=u_id).select_related('user').get()
	user = profile.user
	user.is_active = True
	user.status = 'Activated'
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def categories(request):
	check_user_active(request)
	categ = Category.objects.all().order_by('-created_at')

	return render(request, 'adminpanel/category.html', {'categories':categ})

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def change_category_status(request, id, c_id):
	check_user_active(request)
	# 0 to deactivate
	if c_id == 1:
		category = Category.objects.get(id = id)
		category.status = 'Inactive'
		category.save()
		#messages notifs
		return HttpResponseRedirect(reverse('adminpanel:categories'))

	elif c_id == 0:
		category = Category.objects.get(id = id)
		category.status = 'Active'
		category.save()
		#messages notifs
		return HttpResponseRedirect(reverse('adminpanel:categories'))

	else:
		return HttpResponseRedirect(reverse('adminpanel:categories'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def save_category_form(request, form, template_name):
	check_user_active(request)
	data = dict()
	if request.method == 'POST':
		print(form.is_valid())
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True

		else:
			print("not valid")
			data['form_is_valid'] = False

	context = {'form':form}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def create_category(request):
	check_user_active(request)
	if request.method == 'POST':
		form = CategoryForm(request.POST, request.FILES)
	else:
		form = CategoryForm()

	return save_category_form(request, form, 'adminpanel/create_category.html')

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def update_category(request, id):
	check_user_active(request)
	category = get_object_or_404(Category, id=id)
	if request.method == 'POST':
		form = CategoryForm(request.POST, request.FILES, instance=category)
	else:
		form = CategoryForm(instance=category)

	return save_category_form(request, form, 'adminpanel/update_category.html')

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def moderator_profile(request, id):
	check_user_active(request)
	profile =  Profile.objects.filter(id=id).select_related('user').get()
	questions = Question.objects.filter(author=profile).order_by('-created_at')
	options = Options.objects.filter(question__id__in = questions.all())
	for_front = {
		'profile':profile,
		'questions':questions,
		'options':options,
	}
	return render(request, 'adminpanel/moderator_profile.html', for_front)

def MyPaginator(request, questions, obj_count):
	paginator = Paginator(questions, obj_count)
	page_number = request.GET.get('page')

	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	return page_obj

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def getQuestions(request, s_id):

	check_user_active(request)

	if s_id == 0: #for all questions
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status='open').order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})

			# print(questions)

		else:
			questions = Question.objects.filter(status="open").order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)

		return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})

	if s_id == 1: #for open questions
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="open").order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})
		questions = Question.objects.filter(status = 'open').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)

		return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions, 'options':options})

	if s_id == 2: #for pending questions
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="pending").order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})
		questions = Question.objects.filter(status = 'pending').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)
		return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions, 'options':options})

	if s_id == 3: # for deleted questions
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="deleted").order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})
		questions = Question.objects.filter(status = 'deleted').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)
		return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})

	if s_id == 4: #waiting
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="waiting").order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})
		questions = Question.objects.filter(status = 'waiting').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)
		
		return render(request, 'adminpanel/get_questions.html', {'questions':paginated_questions,'options':options})


@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_question(request, qid):
	check_user_active(request)
	# if request.method == 'POST' and request.user.is_authenticated and request.user.is_moderator:
	question = Question.objects.get(id = qid)
	if question is None:
		print("question is none")
		# message.error('Wrong question ID')
		return HttpResponseRedirect(reverse('adminpanel:index'))
	else:
		question.status = 'deleted'
		BookmarkQuestion.objects.filter(question_id = question.id).delete()
		question.save()
		print("question status changed to deleted")
		# current_url = request.resolver_match.url_name

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		# return HttpResponseRedirect(reverse("adminpanel:get_questions", args=[0]))
	# else:
	# 	# messages.error('Error')
	# 	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def retrieve_question(request, qid):
	check_user_active(request)
	question = Question.objects.get(id=qid)
	question.status = 'open'
	question.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:get_questions', args=[2]))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_answer(request, aid):
	check_user_active(request)
	answer = Answer.objects.get(id = aid)
	answer.status = 'deleted'
	answer.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def retrieve_answer(request, aid):
	check_user_active(request)
	answer = Answer.objects.get(id = aid)
	answer.status = 'open'
	answer.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_reply(request, rid):
	check_user_active(request)
	reply = Replies.objects.get(id = rid)
	reply.status = 'deleted'
	reply.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def retrieve_reply(request, rid):
	check_user_active(request) 
	reply = Replies.objects.get(id = rid)
	reply.status = 'open'
	reply.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def approve_waiting(request, qid):
	check_user_active(request)
	question = Question.objects.get(id = qid)
	question.status = 'open'
	question.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def getQuestionsByCategory(request,c_id):
	check_user_active(request)
	search_text = request.GET.get('search')
	if search_text:
		questions = Question.objects.filter(Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="open", category = c_id).order_by('-created_at')
		options = Options.objects.filter(question__id__in = questions.all())
		return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})
	questions = Question.objects.filter(category = c_id, status='open').order_by('-created_at')
	paginated_questions = MyPaginator(request, questions, 21)
	options = Options.objects.filter(question__id__in = paginated_questions.object_list)
	return render(request, 'adminpanel/get_questions.html', {'questions': questions, 'options':options})

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def answer_page(request, qid):
	check_user_active(request)
	question = Question.objects.get(id = qid)
	answers = Answer.objects.filter(question_id = qid).order_by('-created_at')[:5]
	replies = Replies.objects.filter(answer__id__in = answers.all()).order_by('-created_at')[:5]
	files = QuestionMedia.objects.filter(question = question)
	
	for_front = {
		'question':question,
		'answers':answers,
		'replies':replies,
		'files':files,
	}
	return render(request, 'adminpanel/answer.html', for_front)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def replies(request, aid):
	check_user_active(request)
	replies = Replies.objects.filter(answer__id = aid).order_by("-created_at")

	replies_paginator = Paginator(replies, 5)
	replies_page_number = request.GET.get('page')
	print(replies_page_number, replies_paginator.num_pages)
	try:
		replies_obj = replies_paginator.page(replies_page_number)
	except PageNotAnInteger:
		replies_obj = replies_paginator.page(1)
	except EmptyPage:
		replies_obj = replies_paginator.page(replies_paginator.num_pages)

	reply_html = render_to_string('adminpanel/reply.html', {'replies_obj': replies_obj})

	data = {
		'reply_html': reply_html,
		'has_next': replies_obj.has_next(),
	}
	# print(reply_html)
	return JsonResponse(data)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def answers(request, qid):

	check_user_active(request)
	answers = Answer.objects.filter(question_id = qid).order_by('-created_at')
	replies = Replies.objects.filter(answer__id__in = answers.all()).order_by('-created_at')[:2]
	answer_paginator = Paginator(answers, 5)
	ans_page_number = request.GET.get('page')
	print(ans_page_number)
	try:
		ans_obj = answer_paginator.page(ans_page_number)
	except PageNotAnInteger:
		ans_obj = answer_paginator.page(1)
	except EmptyPage:
		ans_obj = answer_paginator.page(answer_paginator.num_pages)

	ans_html = render_to_string('adminpanel/more_answers.html', {'answers': ans_obj, 'replies':replies})

	data = {
		'ans_html': ans_html,
		'has_next': ans_obj.has_next(),
	}
	# print(reply_html)
	return JsonResponse(data) 

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def question_detail(request, qid):
	check_user_active(request)
	question = Question.objects.get(id = qid)
	answers = Answer.objects.filter(question_id = qid).order_by('-created_at')
	replies = Replies.objects.filter(answer__id__in = answers.all()).order_by('-created_at')
	files = QuestionMedia.objects.filter(question = question)

	for_front = {
		'question':question,
		'answers':answers,
		'replies':replies,
		'files':files,
	}
	return render(request, 'adminpanel/question_detail.html', for_front)


from django.utils.decorators import method_decorator
decorators = [login_required(login_url = 'adminpanel:login'), staff_member_required(login_url = 'adminpanel:login')]

@method_decorator(decorators, name='get')
class spammed_questions(View):

	def get(self, request, *args, **kwargs):
		check_user_active(request)
		questions = Question.objects.filter(status = 'spammed').order_by('-created_at')
		for_front = {
			'questions': questions,
		}
		return render(request, 'adminpanel/spammed.html', for_front)
	
	def post(self, request, qid, action):
		if action == 0: # for approve
			question = Question.objects.get(id = qid)
			question.status = 'spammed'
			question.save()
			SpammedQuestion.objects.get(question = question).delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
		elif action == 1: # reject
			question = Question.objects.get(id = qid)
			question.status = 'open'
			question.save()
			SpammedQuestion.objects.get(question = question).delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@method_decorator(decorators, name='get')
class spammed_answers(View):
	def get(self, request):
		check_user_active(request)
		answers = Answer.objects.filter(status = 'spammed').select_related('question_id').order_by('-created_at')
		for_front = {
			'answers': answers,
		}
		return render(request, 'adminpanel/spammed.html', for_front)
	
	def post(self, request, aid, action):
		if action == 0: # for approve
			answer = Answer.objects.get(id = aid)
			answer.status = 'spammed'
			answer.save()
			SpammedAnswer.objects.get(answer = answer).delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
		elif action == 1: # reject
			answer = Answer.objects.get(id = aid)
			answer.status = 'open'
			answer.save()
			SpammedAnswer.objects.get(answer = answer).delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
@method_decorator(decorators, name='get')
class spammed_replies(View):
	def get(self, request):
		check_user_active(request)
		replies = Replies.objects.filter(status = 'spammed').prefetch_related('answer', 'answer__question_id').order_by('-created_at')
		for_front = {
			'replies': replies,
		}
		return render(request, 'adminpanel/spammed.html', for_front)
	
	def post(self, request, rid, action):
		if action == 0: # for approve
			reply = Replies.objects.get(id = rid)
			reply.status = 'open'
			reply.save()
			SpammedReply.objects.get(reply = reply).delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
		elif action == 1: # reject
			reply = Replies.objects.get(id = rid)
			reply.status = 'open'
			reply.save()
			SpammedReply.objects.get(reply = reply).delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def settings(request):
	check_user_active(request)
	if request.method == 'POST':
		# We instantiate a manager for our global preferences
		global_preferences = global_preferences_registry.manager()

		# now, we can use it to retrieve our preferences
		# the lookup for a preference has the following form: <section>__<name>
		try:
   			global_preferences['open__QUESTION_LIMIT'] = int(request.POST['open__QUESTION_LIMIT'])
		except Exception as e:
			print (str(e))

		try:
   			global_preferences['open__REPLY_LIMIT'] = int(request.POST['open__REPLY_LIMIT'])
		except Exception as e:
			print (str(e))

		try:
   			global_preferences['open__ANSWER_LIMIT'] = int(request.POST['open__ANSWER_LIMIT'])
		except Exception as e:
			print (str(e))

		return HttpResponseRedirect(reverse('adminpanel:settings'))
	else:
		# get a form for global preferences of the 'general' section
		form_class = global_preference_form_builder(section='open')
		context = {
			'form':form_class
		}
		return render(request, 'adminpanel/settings.html', context)

def file_upload(request, files, question):
	if len(files) > MAX_MEDIA_ALLOWED:
		messages.error(request, "Max 10 files allowed")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	for file in files:
		file_type = file.content_type
		if file.size < MAX_MEDIA_SIZE:
			if file_type in ALLOWED_FILE_FORMATS:
				f = QuestionMedia(file=file, question=question, file_type=file_type)
				f.save()
			else:
				messages.error(request, "File type not supported")
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			messages.error(request, "File Size Error. Max 10MB Allowed")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def save_question_form(request, form, template_name):
	check_user_active(request)
	data = dict()
	if request.method == 'POST':
		post = request.POST.copy()
		# print("Copied POST", post._mutable)
		# print("Keywords list", post.getlist('keywords_associated'))
		keylist = post.getlist('keywords_associated')
		for keyword in keylist:
			try:
				keyword = int(keyword)
				print(keyword, "an int")
			except:
				print(keyword, "is a string")
				key = Keywords.objects.filter(name = keyword).first()
				keylist.remove(keyword)
				keylist.append(key.id)
				print("keylist", keylist)
		post.setlist('keywords_associated', keylist)
		# print("Updated Keywords list", post.getlist('keywords_associated'))

		
		# print("Original POST", request.POST)
		qform = QuestionForm(post, instance=form['question'])
		# print(form['question'])
		fform = QuestionMediaForm(post, request.FILES, instance=form['question'])
		# print(form.is_valid(), fform.is_valid())
		# print(form.errors)
		if qform.is_valid() and fform.is_valid():
			question = qform.save(commit=False)
			question.status = 'pending'
			# user = User.objects.get(id = request.user.id)
			profile = Profile.objects.get(user = request.user.id)
			question.author = profile
			# print("Form valid pass")
			question.save()
			qform.save_m2m()
			# print("Keyword for loop pass")

			if qform.cleaned_data['question_type'] == 'poll':
				OptionFormset = inlineformset_factory(Question, Options, fields=('choice',), max_num=4, min_num=2, validate_min=True, validate_max=True)
				oformset = OptionFormset(post, instance=form['question'])
				if oformset.is_valid():
					deleted_choice = oformset.deleted_forms
					for inline_form in oformset:
						if inline_form.cleaned_data != {} and inline_form not in deleted_choice:
							choice = inline_form.save(commit=False)
							choice.question = question
							choice.save()
						else:
							choice = inline_form.save(commit=False)
							choice.delete()

			files = request.FILES.getlist('file')
			# print(files)
			file_upload(request, files, question)
			data['form_is_valid'] = True
			
		else:
			data['form_is_valid'] = False
		form['question_form']=qform
		context = form
		data['html_form'] = render_to_string('adminpanel/edit_question.html', context, request=request)
		return JsonResponse(data)
	
	context = form
	data['html_form'] = render_to_string(template_name, context, request=request)
	
	return JsonResponse(data)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def edit_question(request, qid):
	check_user_active(request)
	question = get_object_or_404(Question, id=qid)
	# print(question.content)
	OptionFormset = inlineformset_factory(Question, Options, fields=('choice',), max_num=4, min_num=2, validate_min=True, validate_max=True)
	if request.method == 'POST':
		# print(request.POST)
		form = {
			'question':Question.objects.filter(id=qid).first(),
		}		
	else:
		qform = QuestionForm(instance = question)
		cformset = OptionFormset(instance = question)
		files_instance = QuestionMedia.objects.filter(question = question)
		fform = QuestionMediaForm(instance = question)
		form = {
			'question_form':qform,
			'option_form':cformset,
			'file_form':fform,
			'files':files_instance,
		}
	return save_question_form(request, form, 'adminpanel/edit_question.html')

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def issues(request):
	check_user_active(request)
	all_issues = ReportIssue.objects.filter(status='pending').order_by('-created_at')

	paginator = Paginator(all_issues, 10)
	page_number = request.GET.get('page')

	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	
	for_front = {
		'issues': page_obj,
	}

	return render(request, 'adminpanel/issues.html', for_front)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def issue_action(request, action, id):
	check_user_active(request)
	if action == 0: #resolved
		try:
			issue = ReportIssue.objects.get(id=id)
			issue.status = 'resolved'
			issue.save()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		except:
			messages.error("Wrong url/ wrong id")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	elif action == 1: #discarded
		try:
			issue = ReportIssue.objects.get(id=id)
			issue.status = 'discarded'
			issue.save()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		except:
			messages.error("Wrong url/ wrong id")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	else:
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
