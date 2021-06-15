from django.forms import ModelForm, Select, ClearableFileInput, Textarea, SelectMultiple, TextInput
from .models import Question, QuestionMedia, Options, Category

class QuestionForm(ModelForm):
	class Meta:
		model = Question
		fields = ('question_type','content', 'category', 'keywords_associated')
		widgets = {
			'category': Select(attrs={'class':'select'}),
			'content': Textarea(),
			'question_type': Select(attrs={"onchange":"showChoice()"})
			# 'keywords_associated': SelectMultiple(attrs={'class':"mySelect"})
		}

	def __init__(self, *args, **kwargs):
		super(QuestionForm, self).__init__(*args, **kwargs)
		self.fields['category'].empty_label = None
		self.fields['category'].queryset = Category.objects.filter(status = 'Active')
		self.fields['keywords_associated'].widget.attrs = {'class':'class-keywords'}
	
class OptionForm(ModelForm):
	class Meta:
		model = Options
		fields = ('choice',)
		widgets = {
			'choice': TextInput(attrs={'required':False})
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['choice'].required = False
	
class QuestionMediaForm(ModelForm):
	class Meta:
		model = QuestionMedia
		fields = ('file',)
		widgets = {
			'file': ClearableFileInput(attrs={'multiple':True, 'required':False}),
		}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['file'].required = False