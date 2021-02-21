from django.shortcuts import render, redirect, get_object_or_404
from questions.models import Question, Options, QuestionMedia, Category
from questions.keywords_models import Keywords
from accounts.models import User
from adminpanel.models import SpammedAnswer, SpammedQuestion, SpammedReply
from answers.models import Answer
from replies.models import Replies
from accounts.models import Profile

from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from questions.forms import QuestionForm, OptionForm
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.formsets import formset_factory

from dynamic_preferences.forms import global_preference_form_builder
from dynamic_preferences.registries import global_preferences_registry

from .forms import CategoryForm
import collectanea.globals as limits
from collectanea.globals import change_qlimit, change_alimit, change_rlimit
from collectanea.global_checks import user_is_active

from django.db.models import Q

# Create your views here.

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def index(request):

	users = Profile.objects.all().order_by('id')

	paginator = Paginator(users, 5)
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
	return render(request, 'adminpanel/index.html', for_front)

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def user_management(request, s_id):

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


def login_view(request):

	if not request.method == 'POST':
		messages.error(request, 'Not a POST request')
		return HttpResponseRedirect(reverse('adminpanel:login'))

	email = request.POST['email']
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
			login(request, user)
			return HttpResponseRedirect(reverse('adminpanel:index'))
		else:
			messages.error(request, 'Invalid password')
			return HttpResponseRedirect(reverse('adminpanel:login'))

	except UserModel.DoesNotExist:
		messages.error(request, 'Invalid email')
		return HttpResponseRedirect(reverse('adminpanel:login'))



def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('adminpanel:login'))	

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def make_moderator(request, u_id):
	profile = Profile.objects.get(id = u_id)
	user = User.objects.get(id = profile.user.id)
	print(user)
	user.is_moderator = True
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(reverse('adminpanel:user_management')) 

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def make_user(request, u_id):
	profile = Profile.objects.get(id = u_id)
	user = User.objects.get(id = profile.user.id)
	print(user)
	user.is_moderator = False
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(reverse('adminpanel:user_management')) 

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_user(request, u_id):
	profile = Profile.objects.get(id = u_id)
	user = User.objects.get(id = profile.user.id)
	print(user)
	user.is_active = False
	user.status = 'Deleted'
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(reverse('adminpanel:user_management')) 

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def block_user(request, u_id):
	profile = Profile.objects.get(id = u_id)
	user = User.objects.get(id = profile.user.id)
	print(user)
	user.is_active = False
	user.status = 'Blocked'
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(reverse('adminpanel:user_management'))
	 
@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def activate_user(request, u_id):
	profile = Profile.objects.get(id = u_id)
	user = User.objects.get(id = profile.user.id)
	user.is_active = True
	user.status = 'Activated'
	user.save()
	#messages (notifications)
	return HttpResponseRedirect(reverse('adminpanel:user_management')) 

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def categories(request):
	categ = Category.objects.all()

	return render(request, 'adminpanel/category.html', {'categories':categ})

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def change_category_status(request, id, c_id):
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
	
	if request.method == 'POST':
		form = CategoryForm(request.POST, request.FILES)
	else:
		form = CategoryForm()

	return save_category_form(request, form, 'adminpanel/create_category.html')

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def update_category(request, id):
	category = get_object_or_404(Category, id=id)
	if request.method == 'POST':
		form = CategoryForm(request.POST, request.FILES, instance=category)
	else:
		form = CategoryForm(instance=category)

	return save_category_form(request, form, 'adminpanel/update_category.html')


@login_required(login_url = 'adminpanel:login')
def getQuestions(request, s_id):

	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('adminpanel:login'))

	if s_id == 0: #for all questions
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status='open')
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})

			# print(questions)

		else:
			questions = Question.objects.filter(Q(status="open") | Q(status='deleted'))
			options = Options.objects.filter(question__id__in = questions.all())

		# print(str(questions[1].keywords_associated).split('.')[1])



		if request.is_ajax():
			# html = render_to_string(
			# 	template_name = "adminpanel/get_questions.html", 
			# 	context = {"questions": questions},
			# )

			# data_dict = {"html_from_view": html}

			data = {
				'questions':questions
			}

			return JsonResponse(data)
		return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})

	if s_id == 1: #for my open questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="open")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})
		# profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(status = 'open')
		options = Options.objects.filter(question__id__in = questions.all())

		return render(request, 'adminpanel/get_questions.html', {'questions':questions, 'options':options})

	if s_id == 2: #for my pending questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="pending")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})
		# profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(status = 'pending')
		options = Options.objects.filter(question__id__in = questions.all())

		return render(request, 'adminpanel/get_questions.html', {'questions':questions, 'options':options})

	if s_id == 3: # for my deleted questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="deleted")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})
		# profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(status = 'deleted')
		options = Options.objects.filter(question__id__in = questions.all())
		
		return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})

	if s_id == 4: #waiting
		user = request.user
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="waiting")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})
		# profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(status = 'waiting')
		options = Options.objects.filter(question__id__in = questions.all())
		
		return render(request, 'adminpanel/get_questions.html', {'questions':questions,'options':options})



@login_required(login_url = "adminpanel:login")
def delete_question(request, qid):
	# if request.method == 'POST' and request.user.is_authenticated and request.user.is_moderator:
	question = Question.objects.get(id = qid)
	if question is None:
		print("question is none")
		# message.error('Wrong question ID')
		return HttpResponseRedirect(reverse('adminpanel:index'))
	else:
		question.status = 'deleted'
		question.save()
		print("question status changed to pending")
		# current_url = request.resolver_match.url_name

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		# return HttpResponseRedirect(reverse("adminpanel:get_questions", args=[0]))
	# else:
	# 	# messages.error('Error')
	# 	return HttpResponseRedirect(reverse('moderator:moderator_panel'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def retrieve_question(request, qid):
	question = Question.objects.get(id=qid)
	question.status = 'open'
	question.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:get_questions', args=[2]))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_answer(request, aid):
	answer = Answer.objects.get(id = aid)
	answer.status = 'deleted'
	answer.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def retrieve_answer(request, aid):
	answer = Answer.objects.get(id = aid)
	answer.status = 'open'
	answer.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def delete_reply(request, rid):
	reply = Replies.objects.get(id = rid)
	reply.status = 'deleted'
	reply.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))

@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def retrieve_reply(request, rid):
	reply = Replies.objects.get(id = rid)
	reply.status = 'open'
	reply.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# return HttpResponseRedirect(reverse('adminpanel:index'))


@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def getQuestionsByCategory(request,c_id):
	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))
	questions = Question.objects.filter(category = c_id)
	options = Options.objects.filter(question__id__in = questions.all())
	return render(request, 'adminpanel/get_questions.html', {'questions': questions, 'options':options})


def answer(request, qid):

	question = Question.objects.get(id = qid)
	answers = Answer.objects.filter(question_id = qid)
	replies = Replies.objects.filter(answer__id__in = answers.all())

	answer_paginator = Paginator(answers, 2)
	ans_page_number = request.GET.get('page')

	try:
		ans_obj = answer_paginator.page(ans_page_number)
	except PageNotAnInteger:
		ans_obj = answer_paginator.page(1)
	except EmptyPage:
		ans_obj = answer_paginator.page(paginator.num_pages)

	replies_paginator = Paginator(replies, 2)
	replies_page_number = request.GET.get('page')

	try:
		replies_obj = replies_paginator.page(replies_page_number)
	except PageNotAnInteger:
		replies_obj = replies_paginator.page(1)
	except EmptyPage:
		replies_obj = replies_paginator.page(paginator.num_pages)

	for_front = {
		'question':question,
		'answers':answers,
		'replies':replies,
		'ans_obj':ans_obj,
		'replies_obj':replies_obj,
	}
	return render(request, 'adminpanel/answer.html', for_front)


class spam_question(View):
	def get(self, request):
		questions = SpammedQuestion.objects.all()
		for_front = {
			'questions': questions,
		}
		return render(request, 'adminpanel/spammed.html', for_front)
	
	def post(self, request, qid):
		question = Question.objects.get(id = qid)
		question.status = 'spammed'
		question.save()
		SpammedQuestion.objects.delete(question = question)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



	# if request.method == 'GET':
	# 	return render(request, 'adminpanel/spammed.html')
	
	# if request.method == 'POST':
	# 	pass

class spam_answer(View):
	def get(self, request):
		answers = SpammedAnswer.objects.all()
		for_front = {
			'answers': answers,
		}
		return render(request, 'adminpanel/spammed.html', for_front)
	
	def post(self, request, aid):
		answer = Answer.objects.get(id = aid)
		answer.status = 'spammed'
		answer.save()
		SpammedAnswer.objects.delete(qanswer = answer)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class spam_reply(View):
	def get(self, request):
		return render(request, 'adminpanel/spammed.html')
	
	def post(self, request, rid):
		reply = Replies.objects.get(id = rid)
		reply.status = 'spammed'
		reply.save()
		SpammedReply.objects.delete(reply = reply)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
@user_passes_test(lambda u: u.is_superuser)
def settings(request):
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


@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def save_question_form(request, form, template_name):
	data = dict()
	if request.method == 'POST':
		# print(form.is_valid())
		# if form.is_valid():
		# 	form.save()
		# 	data['form_is_valid'] = True

		# else:
		# 	print("not valid")
		# 	data['form_is_valid'] = False
		pass
	context = form
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@login_required(login_url = 'adminpanel:login')
@staff_member_required(login_url = 'adminpanel:login')
def edit_question(request, qid):
	question = get_object_or_404(Question, id=qid)
	if request.method == 'POST':
		# form = CategoryForm(request.POST, request.FILES, instance=category)
		pass
	else:
		form = QuestionForm(instance=question)
		OptionFormset = formset_factory(OptionForm, extra=2, min_num=2, validate_min=True)
		options = Options.objects.filter(question=question)
		# option = OptionFormset(question=question)
		context = {
			'form':form,
			'option':options,
		}

	return save_question_form(request, context, 'adminpanel/edit_question.html')