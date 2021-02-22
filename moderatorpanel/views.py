from django.shortcuts import render, redirect, get_object_or_404
from questions.models import Question, Options, QuestionMedia, Category
from questions.keywords_models import Keywords
from accounts.models import User
# from adminpanel.models import QuestionChangeRequest
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

from collectanea.global_checks import user_is_active
from collectanea.globals import ALLOWED_FILE_FORMATS, MAX_MEDIA_ALLOWED, MAX_MEDIA_SIZE

from questions.forms import QuestionForm, OptionForm, QuestionMediaForm
from django.forms.formsets import formset_factory
from django.template.loader import render_to_string
 
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
# Create your views here.

def login_view(request):

	if not request.method == 'POST':
		messages.error(request, 'Not a POST request')
		return HttpResponseRedirect(reverse('moderator:login'))

	email = request.POST['email']
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
			login(request, user)
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


# @user_is_active
@login_required(login_url = 'moderator:login')
def getQuestions(request, s_id):

	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))

	if s_id == 0: #for all questions
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status='open')
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})

			# print(questions)

		else:
			questions = Question.objects.filter(status="open")
			options = Options.objects.filter(question__id__in = questions.all())

		# print(str(questions[1].keywords_associated).split('.')[1])



		if request.is_ajax():
			# html = render_to_string(
			# 	template_name = "moderatorpanel/get_questions.html", 
			# 	context = {"questions": questions},
			# )

			# data_dict = {"html_from_view": html}

			data = {
				'questions':questions
			}

			return JsonResponse(data)
		return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})

	if s_id == 1: #for my open questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="open")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(author = profile, status = 'open')
		options = Options.objects.filter(question__id__in = questions.all())

		return render(request, 'moderatorpanel/get_questions.html', {'questions':questions, 'options':options})

	if s_id == 2: #for my pending questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="pending")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(author = profile, status = 'pending')
		options = Options.objects.filter(question__id__in = questions.all())

		return render(request, 'moderatorpanel/get_questions.html', {'questions':questions, 'options':options})

	if s_id == 3: # for my deleted questions
		user = request.user
		# print(user)
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="deleted")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(author = profile, status = 'deleted')
		options = Options.objects.filter(question__id__in = questions.all())
		
		return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})

	if s_id == 4: #waiting
		user = request.user
		search_text = request.GET.get('search')
		if search_text:
			questions = Question.objects.filter( Q(content__icontains=search_text) | Q(author__fullname__icontains=search_text) | Q(author__user__username__icontains=search_text), status="waiting")
			options = Options.objects.filter(question__id__in = questions.all())
			return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})
		profile = Profile.objects.get(user = user)
		questions = Question.objects.filter(author = profile, status = 'waiting')
		options = Options.objects.filter(question__id__in = questions.all())
		
		return render(request, 'moderatorpanel/get_questions.html', {'questions':questions,'options':options})


@login_required(login_url = 'moderator:login')
def index(request):

	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))

	user = request.user
	profile = Profile.objects.get(user = user)
	recent_questions = Question.objects.filter(author = profile, status = 'open').order_by('-created_at')
	recent_options = Options.objects.filter(question__id__in = recent_questions.all())

	keywords = Keywords.objects.all()

	all_questions = Question.objects.filter(author = profile).order_by('created_at')

	questions = Question.objects.filter(author = profile, status='open')
	options = Options.objects.filter(question__id__in = recent_questions.all())
	question_count = questions.count()
	answers = Answer.objects.filter(question_id__id__in=questions.all())
	answer_count = answers.count()
	replies = Replies.objects.filter(answer__id__in = answers.all())
	replies_count = replies.count()

	paginator = Paginator(all_questions, 5)
	page_number = request.GET.get('page')

	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	# print(question_count)
	for_front = {
		'recent_questions':recent_questions,
		'recent_options':recent_options,
		'questions':questions,
		'options':options,
		'question_count':question_count,
		'answer_count':answer_count,
		'replies_count':replies_count,
		'page_obj':page_obj,
		'keywords':keywords,
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
		key, created = Keywords.objects.get_or_create(name=k)
		if created:
			return JsonResponse({'Success':'Created'})



@login_required(login_url = 'moderator:login')	
def question_form(request):

	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))

	if request.ajax() or request.method == 'GET':
		print("Request is ajax")
		q = request.GET('q')
		p = request.GET('p')
		print(q)

		if q:
			questions = Question.objects.filter(status="open", question_type = "normal")

			for question in questions:
				X = question.content.lower()
				Y = q.lower()

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
				if cosine > 0.3:
					data = {
						'question':"<li>"+question.content+'<li>'
					}
					return JsonResponse(data)

		if p:
			polls = Question.objects.filter(status = "open", question_type = "poll")

			for question in polls:
				X = question.content.lower()
				Y = q.lower()

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
				if cosine > 0.3:
					data = {
						'question':"<li>" + question.content + "<li>"
					}
					return JsonResponse(data)

	question_form = QuestionForm(auto_id = 'id_question_%s')
	option_form = OptionForm(auto_id = 'id_poll_%s')
	question = Question.objects.filter(author = Profile.objects.get(user = request.user)).order_by('-created_at').first()
	options = Options.objects.filter(question = question)
	# keywords = Keywords.objects.all()
	categories = Category.objects.all()
	media_form = QuestionMediaForm(question = question)

	# # print(keywords)
	for_front = {
		# 'keywords':keywords,
		'categories':categories,
		'question_form':question_form,
		'option_form':option_form,
		'question':question,
		'options':options,
		'media_form':media_form,
	}
	return render(request, 'moderatorpanel/question_form.html', for_front)

def file_upload(request, files, question):
	if len(files) > MAX_MEDIA_ALLOWED:
		messages.error(request, "Max 10 files allowed")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	for file in files:
		file_type = file.content_type 
		print(file_type) 
		if file and file.size > MAX_MEDIA_SIZE:
			if file_type in ALLOWED_FILE_FORMATS:
				f = QuestionMedia(file=file, question=question, file_type=file_type)
				print(f)
				f.save()
			else:
				messages.error(request, "File Size Error. Max 10MB Allowed")
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			messages.error(request, "File type not supported")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_question(request):
	if request.method == 'POST':
		request.POST._mutable = True
		post = request.POST.copy()
		for keyword in post.getlist('keywords_associated'):
			print(keyword)
			try:
				get_object_or_404(Keywords, pk=keyword)
			except:
				key = Keywords.objects.create(name = keyword)
				post.getlist('keywords_associated').remove(keyword)
				print('Keyword removed:', keyword)
				post.setlist('keywords_associated', key.id)
				# post.setlist('keywords_associated', key.id).append('keywords_associated', key.id)
				print(post)
				print("keyword created and added to request obj, ID: ", key.id )
		request.POST = post
		request.POST._mutable = False
			
		print(request.POST)
		form = QuestionForm(request.POST)
		fform = QuestionMediaForm(request.POST, request.FILES)
		print(form.is_valid(), fform.is_valid())
		print(form.errors)
		if form.is_valid() and fform.is_valid():
			question = form.save(commit=False)
			question.question_type = 'normal'
			question.status = 'waiting'
			user = User.objects.get(id = request.user.id)
			profile = Profile.objects.get(user = user)
			question.author = profile
			print("Form valid pass")
			question.save()
			form.save_m2m()
			# print("Keyword for loop pass")

			files = request.FILES.getlist('file')
			print(files)
			file_upload(request, files, question)

			return HttpResponseRedirect(reverse('moderator:moderator_panel'))
		else:
			messages.error(request, "There is some error there in normal question")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
	else:
		OptionFormset = formset_factory(OptionForm, extra=2, min_num=2, validate_min=True)
		qform = QuestionForm()
		cformset = OptionFormset()
		fform = QuestionMediaForm()
		context = {
			'question_form':qform,
			'option_form':cformset,
			'file_form':fform,
		}
		return render(request, 'moderatorpanel/question_form.html', context)

		
def add_poll(request):
	OptionFormset = formset_factory(OptionForm, extra=2, min_num=2, validate_min=True)
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		oformset = OptionFormset(request.POST)
		fform = QuestionMediaForm(request.POST, request.FILES)
		if all([form.is_valid(), oformset.is_valid(), fform.is_valid()]):
			poll = form.save(commit=False)
			poll.question_type = "poll"
			user = User.objects.get(id = request.user.id)
			profile = Profile.objects.get(user = user)
			poll.author = profile
			poll.save()
			form.save_m2m()

			
			for inline_form in oformset:
				choice = inline_form.save(commit=False)
				choice.question = poll
				choice.save()

			files = request.FILES.getlist('file')
			print(files)
			file_upload(request, files, poll)
			return HttpResponseRedirect(reverse('moderator:moderator_panel'))
		else:
			return redirect('moderator:question_form')
	


@login_required(login_url = 'moderator:login')	
def add_keyword(request):
	if request.method == 'POST':
		addkeyword = request.POST['addkeyword']
		# print(addkeyword)
		Keywords.objects.create(name = addkeyword)
		current_url = request.resolver_match.url_name
		# print(current_url)
		return redirect(current_url)
	else:
		return HttpResponse("Not a post request")

@login_required(login_url = "moderator:login")
def delete_question(request, qid):
	# if request.method == 'POST' and request.user.is_authenticated and request.user.is_moderator:
	question = Question.objects.get(id = qid)
	if question is None:
		print("question is none")
		# message.error('Wrong question ID')
		return HttpResponseRedirect(reverse('moderator:moderator_panel'))
	else:
		question.status = 'pending'
		question.save()
		print("question status changed to pending")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	# else:
	# 	# messages.error('Error')
	# 	return HttpResponseRedirect(reverse('moderator:moderator_panel'))

# def post_question(request):
# 	if request.method == 'POST' and request.user.is_authenticated and request.user.is_moderator:
		
# 		f = QuestionForm(request.POST)
# 		question = f.save(commit=False)
# 		question.author = Profile.objects.get(user = request.user)
# 		question.question_type = 'normal'
# 		question.save()
# 		f.save_m2m()

# 		# question = request.POST['question']
# 		# category = request.POST['category']
# 		# c_id = Category.objects.get(name=category)
# 		# # keywords = request.POST['keyword']
# 		# file = request.POST['file']
# 		# qid = Question.objects.create(question = question, category = c_id, )
# 		# if file:
# 		# 	QuestionMedia.objects.create(file = file, question = qid, )
# 		return HttpResponseRedirect(reverse('moderator:moderator_panel'))
# 	else:
# 		messages.error(request, 'Error')
# 		return HttpResponseRedirect(reverse('moderator:moderator_panel'))


# def post_poll(request):
# 	if request.method == 'POST' and request.user.is_authenticated and request.user.is_moderator:
		
# 		f = QuestionForm(request.POST)
# 		question = f.save(commit=False)
# 		question.author = Profile.objects.get(user = request.user)
# 		question.question_type = 'poll'
# 		question.save()
# 		f.save_m2m()

# 		# question = request.POST['question']
# 		# category = request.POST['category']
# 		# c_id = Category.objects.get(name=category)
# 		# # keywords = request.POST['keyword']
# 		# file = request.POST['file']
# 		# qid = Question.objects.create(question = question, category = c_id, )
# 		# if file:
# 		# 	QuestionMedia.objects.create(file = file, question = qid, )
# 		return HttpResponseRedirect(reverse('moderator:moderator_panel'))
# 	else:
# 		messages.error(request, 'Error')
# 		return HttpResponseRedirect(reverse('moderator:moderator_panel'))

# def post_option(request):
# 	question = Question.objects.filter(author = Profile.objects.get(user = request.user)).order_by('-created_at').first()
# 	Options.objects.create(question = question, choice = request.POST['choice'])
# 	return	HttpResponseRedirect(reverse('moderator:moderator_panel'))
#current_url = request.resolver_match.url_name for geting current url

# def edit_question(request, qid):
# 	if request.method == 'POST' and request.user.is_authenticated and request.user.is_moderator:
# 		q_id = Question.objects.get(id = qid)
# 		question = request.POST['question']
# 		category = request.POST['category']
# 		keywords = request.POST['keywords']
# 		file = request.POST['file']
# 		# QuestionChangeRequest.objects.create(quesiton = qid, user = request.user, )


def getQuestionsByCategory(request,c_id):
	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))
	questions = Question.objects.filter(category = c_id)
	return render(request, 'moderatorpanel/questioncategory.html', {'questions': questions})

def categorypage(request):
	if not user_is_active(request):
		messages.error(request, 'Your account is deactivated. Contact administrator.')
		return HttpResponseRedirect(reverse('moderator:login'))
	category = Category.objects.all()
	return render(request, 'moderatorpanel/category.html', {'category':category})

def answer_page(request, qid):
	question = Question.objects.get(id = qid)
	answers = Answer.objects.filter(question_id = qid)[:2]
	replies = Replies.objects.filter(answer__id__in = answers.all())[:2]
	files = QuestionMedia(question = question)
	print(files)
	for_front = {
		'question':question,
		'answers':answers,
		'replies':replies,
		'files':files,
	}
	return render(request, 'moderatorpanel/answer.html', for_front)


def replies(request, aid):

	# question = Question.objects.get(id = qid)
	# answers = Answer.objects.filter(question_id = qid)
	replies = Replies.objects.filter(answer__id = aid).order_by("id")

	# answer_paginator = Paginator(answers, 2)
	# ans_page_number = request.GET.get('page')

	# try:
	# 	ans_obj = answer_paginator.page(ans_page_number)
	# except PageNotAnInteger:
	# 	ans_obj = answer_paginator.page(1)
	# except EmptyPage:
	# 	ans_obj = answer_paginator.page(paginator.num_pages)

	replies_paginator = Paginator(replies, 2)
	replies_page_number = request.GET.get('page')

	try:
		replies_obj = replies_paginator.page(replies_page_number)
	except PageNotAnInteger:
		replies_obj = replies_paginator.page(1)
	except EmptyPage:
		replies_obj = replies_paginator.page(Paginator.num_pages)

	reply_html = render_to_string('moderatorpanel/reply.html', {'replies_obj': replies_obj})

	data = {
		'reply_html': reply_html,
		'has_next': replies_obj.has_next(),
	}
	print(reply_html)
	return JsonResponse(data)


@login_required(login_url = 'moderator:login')
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

	context = {'form':form}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

@login_required(login_url = 'moderator:login')
def edit_question(request, qid):
	question = get_object_or_404(Question, id=qid)
	if request.method == 'POST':
		# form = CategoryForm(request.POST, request.FILES, instance=category)
		pass
	else:
		form = QuestionForm(instance=question)

	return save_question_form(request, form, 'moderatorpanel/edit_question.html')



