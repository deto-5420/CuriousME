from django.shortcuts import render, redirect, get_object_or_404
from questions.models import Question, Options, QuestionMedia, Category, BookmarkQuestion
from questions.keywords_models import Keywords
from accounts.models import User
from adminpanel.models import SpammedQuestion, SpammedAnswer, SpammedReply
from answers.models import Answer
from replies.models import Replies
from accounts.models import Profile

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.forms import inlineformset_factory, modelformset_factory

from collectanea.global_checks import user_is_active
from collectanea.globals import ALLOWED_FILE_FORMATS, MAX_MEDIA_ALLOWED, MAX_MEDIA_SIZE

from questions.forms import QuestionForm, OptionForm, QuestionMediaForm
from django.forms.formsets import formset_factory
from django.template.loader import render_to_string
 
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
# Create your views here.

def check_user_active(request):
	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))

def login_page(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('moderator:moderator_panel'))
	
	return render(request, 'moderatorpanel/login.html')

	
def login_view(request):
	
	if not request.method == 'POST':
		messages.error(request, 'Not a POST request')
		return HttpResponseRedirect(reverse('moderator:login'))

	email = request.POST['email'].lower()
	password = request.POST['password']
	UserModel = get_user_model()

	try:
		user = UserModel.objects.get(email=email)
		if not user.is_moderator:
			messages.warning(request, 'You are not a moderator')
			return HttpResponseRedirect(reverse('moderator:login'))

		if not user.is_active:
			messages.warning(request, 'Your account is deactivated. Contact administrator.')
			return HttpResponseRedirect(reverse('moderator:login'))

		if user.check_password(password):
			usr_dict = UserModel.objects.filter(email=email).values().first()
			usr_dict.pop('password')
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			return HttpResponseRedirect(reverse('moderator:moderator_panel'))
		else:
			messages.error(request, 'Invalid password')
			return HttpResponseRedirect(reverse('moderator:login'))

	except UserModel.DoesNotExist:
		messages.error(request, 'Invalid email')
		return HttpResponseRedirect(reverse('moderator:login'))

def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('moderator:login'))	

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

@login_required(login_url = 'moderator:login')
def getQuestions(request, s_id):

	check_user_active(request)

	if s_id == 0: #for all questions
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status='open').order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'moderatorpanel/get_questions.html', {'questions':paginated_questions,'options':options})
			
		else:
			questions = Question.objects.filter(status="open").order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
		return render(request, 'moderatorpanel/get_questions.html', {'questions':paginated_questions,'options':options})

	if s_id == 1: #for my open questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		profile = Profile.objects.get(user = user)
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="open", author = profile).order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		questions = Question.objects.filter(author = profile, status = 'open').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)

		return render(request, 'moderatorpanel/get_questions.html', {'questions':paginated_questions, 'options':options})

	if s_id == 2: #for my pending questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		profile = Profile.objects.get(user = user)
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="pending", author = profile).order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		questions = Question.objects.filter(author = profile, status = 'pending').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)

		return render(request, 'moderatorpanel/get_questions.html', {'questions':paginated_questions, 'options':options})

	if s_id == 3: # for my deleted questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		profile = Profile.objects.get(user = user)
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="deleted", author = profile).order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		questions = Question.objects.filter(author = profile, status = 'deleted').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)
		
		return render(request, 'moderatorpanel/get_questions.html', {'questions':paginated_questions,'options':options})

	if s_id == 4: #waiting
		user = request.user
		search_text = request.GET.get('search')
		profile = Profile.objects.get(user = user)
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="waiting", author = profile).order_by('-created_at')
			paginated_questions = MyPaginator(request, questions, 21)
			options = Options.objects.filter(question__id__in = paginated_questions.object_list)
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		questions = Question.objects.filter(author = profile, status = 'waiting').order_by('-created_at')
		paginated_questions = MyPaginator(request, questions, 21)
		options = Options.objects.filter(question__id__in = paginated_questions.object_list)
		
		return render(request, 'moderatorpanel/get_questions.html', {'questions':paginated_questions,'options':options})


@login_required(login_url = 'moderator:login')
def index(request):

	check_user_active(request)
	if not request.user.is_moderator:
		messages.error(request, 'You are not a moderator')
		return HttpResponseRedirect(reverse('moderator:login'))
	profile = Profile.objects.get(user = request.user)
	recent_questions = Question.objects.filter(author = profile, status = 'open').order_by('-created_at')[:6]
	recent_options = Options.objects.filter(question__id__in = recent_questions.all())

	all_questions = Question.objects.filter(author = profile).order_by('-created_at')

	questions = Question.objects.filter(author = profile, status='open')
	options = Options.objects.filter(question__id__in = recent_questions.all())
	question_count = questions.count()
	answers = Answer.objects.filter(question_id__id__in=questions.all())
	answer_count = answers.count()
	replies = Replies.objects.filter(answer__id__in = answers.all())
	replies_count = replies.count()

	paginator = Paginator(all_questions, 10)
	page_number = request.GET.get('page')

	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	# print(question_count)
	for_front = {
		'profile':profile,
		'recent_questions':recent_questions,
		'recent_options':recent_options,
		'questions':questions,
		'options':options,
		'question_count':question_count,
		'answer_count':answer_count,
		'replies_count':replies_count,
		'page_obj':page_obj,
	}
	return render(request, 'moderatorpanel/index.html', for_front)

@csrf_exempt
def return_keyword(request):
	if request.is_ajax():
		keyw = request.GET.get('k')
		print(keyw)
		if keyw:
			keywords = Keywords.objects.filter(name__icontains = keyw)
			if keywords is None:
				Keywords.objects.create(name = keyw)
				print("created")
			keyword = list(keywords.values('id', 'name'))
			print(keyword)
			# data = {
			# 	'results':keyword
			# }
			return JsonResponse(keyword, safe=False)
	if request.method == 'POST':
		k = request.POST['keyword']
		# key={}
		if len(k) > 20:
			return JsonResponse({'Error':'Key could not be more than 20 chars'})
		key, created = Keywords.objects.get_or_create(name=k)
		if created:
			return JsonResponse({'Success':'Created', 'id':key.id})
		else:
			return JsonResponse({'Success':'Already there'})

def suggestions(questions, q):
	print(questions)
	for question in questions:
		X = question['content'].lower()
		print("X", X)
		Y = q.lower()
		print('Y', Y)

		#tokenization
		X_list = word_tokenize(X)
		Y_list = word_tokenize(Y)

		#sw contains the stopwords
		sw = stopwords.words('english')
		l1=[]; l2=[]

		#removing stopwords from the string
		X_set = {w for w in X_list if not w in sw}
		Y_set = {w for w in Y_list if not w in sw}

		#form a set containing keywords of both string
		rvector = X_set.union(Y_set)
		for w in rvector:
			if w in X_set: l1.append(1) #create a vector
			else: l1.append(0)
			if w in Y_set: l2.append(1)
			else: l2.append(0)
		c=0 

		#cosine formula
		for i in range(len(rvector)):
			c += l1[i]*l2[i]
		cosine = c / float((sum(l1)*sum(l2))**0.5)
		print('similarity', cosine)
		if cosine > 0.5:
			data = {
				'question':str("<a href='{}' target='_blank'>".format(reverse('moderator:answer_page', kwargs={'qid':question['id']})))+"<li>"+question['content']+"<li>"+"</a>",
				'id':question['id']
			}
			return JsonResponse(data)
		else:
			pass

@login_required(login_url = 'moderator:login')
def question_suggestion(request):

	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))
	# print("hello")
	if request.method == 'GET':
		print("Request is ajax")
		q = request.GET.get('q')
		p = request.GET.get('p')
		print(q)

		if q:
			# questions = Question.objects.filter(status="open", question_type = "normal").values('id', 'content')
			# print("this is q")
			# data = suggestions(questions, q)
			# return data
			data = []
			questions = Question.objects.filter(status='open', question_type='normal', content__icontains=q).values('id', 'content').order_by('-created_at')
			for question in questions:
				# data['question_{}'.format(question['id'])] = str("<a href='{}' target='_blank'>".format(reverse('moderator:answer_page', kwargs={'qid':question['id']})))+"<li>"+question['content']+"<li>"+"</a>"
				data.append(str("<li>"+"<a href='{}' target='_blank'>".format(reverse('moderator:answer_page', kwargs={'qid':question['id']})))+question['content']+"</a>"+"<li>")
				print(data)
			return JsonResponse(data, safe=False)

		elif p:
			# questions = Question.objects.filter(status="open", question_type = "poll").values('id', 'content')
			# print("this is p")
			# data = suggestions(questions, p)
			# return data
			data = []
			questions = Question.objects.filter(status='open', question_type='poll', content__icontains=p).values('id', 'content').order_by('-created_at')
			for question in questions:
				# data['question_{}'.format(question['id'])] = str("<a href='{}' target='_blank'>".format(reverse('moderator:answer_page', kwargs={'qid':question['id']})))+"<li>"+question['content']+"<li>"+"</a>"
				data.append(str("<li>"+"<a href='/moderator/get_questions/1#poll_{}' target='_blank'>".format(question['id']))+question['content']+"</a>"+"<li>")
				print(data)
			return JsonResponse(data, safe=False)
		else:
			pass

		return JsonResponse("None", safe=False)
	return JsonResponse("None", safe=False)


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

@login_required(login_url = 'moderator:login')
def add_question(request):
	check_user_active(request)
	if request.method == 'POST':
		post = request.POST.copy()
		# print("Copied POST", post._mutable)
		# print("Keywords list", post.getlist('keywords_associated'))
		keylist = post.getlist('keywords_associated')
		print("keylist", keylist)
		for keyword in keylist:
			print(keyword)
			try:
				keyword = int(keyword)
				print(keyword, "an int")
				pass
			except:
				print(keyword, "is a string")
				key = Keywords.objects.get(name = keyword)
				index = keylist.index(keyword)
				keylist.remove(keyword)
				keylist.insert(index, key.id)
				print("updated keylist", keylist)
		post.setlist('keywords_associated', keylist)
		# print("Updated Keywords list", post.getlist('keywords_associated'))

		
		# print("Original POST", request.POST)
		form = QuestionForm(post)
		fform = QuestionMediaForm(post, request.FILES)
		# print(form.is_valid(), fform.is_valid())
		# print(form.errors)
		if form.is_valid() and fform.is_valid():
			question = form.save(commit=False)
			question.status = 'waiting'
			# user = User.objects.get(id = request.user.id)
			profile = Profile.objects.get(user = request.user.id)
			question.author = profile
			# print("Form valid pass")
			question.save()
			form.save_m2m()
			# print("Keyword for loop pass")

			if form.cleaned_data['question_type'] == 'poll':
				OptionFormset = inlineformset_factory(Question, Options, fields=('choice',), max_num=4, min_num=2, validate_min=True, validate_max=True)
				oformset = OptionFormset(post)
				if oformset.is_valid():
					for inline_form in oformset:
						if inline_form.cleaned_data != {}:
							choice = inline_form.save(commit=False)
							choice.question = question
							choice.save()

			files = request.FILES.getlist('file')
			# print(files)
			file_upload(request, files, question)

			return HttpResponseRedirect(reverse('moderator:moderator_panel'))
		else:
			messages.error(request, "There is some error there in normal question")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
	else:
		OptionFormset = inlineformset_factory(Question, Options, fields=('choice',), max_num=4, min_num=2, validate_min=True, validate_max=True, can_delete=False)
		qform = QuestionForm()
		cformset = OptionFormset(auto_id=False)
		fform = QuestionMediaForm()
		context = {
			'question_form':qform,
			'option_form':cformset,
			'file_form':fform,
		}
		return render(request, 'moderatorpanel/question_form.html', context)
	
@login_required(login_url = "moderator:login")
def delete_question(request, qid):
	check_user_active(request)
	if request.user.is_moderator:
		question = Question.objects.get(id = qid)
		if question is None:
			print("question is none")
			# message.error('Wrong question ID')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			question.status = 'deleted'
			BookmarkQuestion.objects.filter(question_id = question).delete()
			question.save()
			print("question status changed to deleted")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		# messages.error('Error')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url = 'moderator:login')
def getQuestionsByCategory(request,c_id):
	check_user_active(request)
	search_text = request.GET.get('search')
	if search_text:
		questions = Question.objects.filter(Q(content__icontains=search_text) | Q(keywords_associated__name__icontains=search_text), status="open", category = c_id).order_by('-created_at')
		options = Options.objects.filter(question__id__in = questions.all())
		return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
	questions = Question.objects.filter(category = c_id, status='open').order_by('-created_at')
	paginated_questions = MyPaginator(request, questions, 21)
	options = Options.objects.filter(question__id__in = paginated_questions.object_list)
	return render(request, 'moderatorpanel/get_questions.html', {'questions': paginated_questions, 'options':options})

@login_required(login_url = 'moderator:login')
def categorypage(request):
	check_user_active(request)
	category = Category.objects.filter(status = "Active").order_by('-created_at')
	return render(request, 'moderatorpanel/category.html', {'category':category})

@login_required(login_url = 'moderator:login')
def answer_page(request, qid):
	check_user_active(request)
	question = Question.objects.get(id = qid)
	answers = Answer.objects.filter(question_id = qid).order_by('-created_at')[:5]
	replies = Replies.objects.filter(answer__id__in = answers.all()).order_by('-created_at')[:5]
	files = QuestionMedia.objects.filter(question = question)
	# print('files' ,files)
	for_front = {
		'question':question,
		'answers':answers,
		'replies':replies,
		'files':files,
	}
	return render(request, 'moderatorpanel/answer.html', for_front)


@login_required(login_url = 'moderator:login')
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

	reply_html = render_to_string('moderatorpanel/reply.html', {'replies_obj': replies_obj})

	data = {
		'reply_html': reply_html,
		'has_next': replies_obj.has_next(),
	}
	# print(reply_html)
	return JsonResponse(data)

@login_required(login_url = 'moderator:login')
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

	ans_html = render_to_string('moderatorpanel/more_answers.html', {'answers': ans_obj, 'replies':replies})

	data = {
		'ans_html': ans_html,
		'has_next': ans_obj.has_next(),
	}
	# print(reply_html)
	return JsonResponse(data) 


@login_required(login_url = 'moderator:login')
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
		data['html_form'] = render_to_string('moderatorpanel/edit_question.html', context, request=request)
		# messages.error(request, 'The question is edited and has been sent to admin for confirmation. You can find it under "Pending Questions".')
		return JsonResponse(data)
	
	context = form
	data['html_form'] = render_to_string(template_name, context, request=request)
	
	return JsonResponse(data)

@login_required(login_url = 'moderator:login')
def edit_question(request, qid):
	check_user_active(request)
	question = get_object_or_404(Question, id=qid)
	# print(question.content)
	if request.user.id is not question.author.user.id:
		messages.error(request, "You don't have rights to edit this question")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
	return save_question_form(request, form, 'moderatorpanel/edit_question.html')

def spam_answer(request, aid):
	answer = Answer.objects.filter(id = aid).first()
	SpammedAnswer.objects.create(answer = answer, by = Profile.objects.get(user = request.user.id))
	answer.status = 'spammed'
	print(answer)
	print(answer.status)
	answer.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def spam_reply(request, rid):
	reply = Replies.objects.filter(id = rid).first()
	SpammedReply.objects.create(reply = reply, by = Profile.objects.get(user = request.user.id))
	reply.status = 'spammed'
	reply.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))