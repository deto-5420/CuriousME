from django.forms import ModelForm, Select, ClearableFileInput, Textarea, SelectMultiple, TextInput
from .models import Question, QuestionMedia, Options

class QuestionForm(ModelForm):
	class Meta:
		model = Question
		fields = ('content', 'category', 'keywords_associated')
		widgets = {
			'category': Select(attrs={'class':'select'}),
			'content': Textarea(),
			'keywords_associated': SelectMultiple(attrs={'class':'mySelect'})
		}

	# def __init__(self, post_data=None):
	# 	if post_data:
	# 		self.fields.pop('keywords_associated')
	# 		super(QuestionForm, self).__init__(post_data)
	# 	else:
	# 		super(QuestionForm, self).__init__()
	
class OptionForm(ModelForm):
	class Meta:
		model = Options
		fields = ('choice',)
		widgets = {
			'choice': TextInput(attrs={'required':'False'})
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['choice'].required = False

	# def clean(self):
	# 	cleaned_data = super().clean()
		# if cleaned_data.get('choice').count() != 4:
		# 	raise ValidationError('You have to choose exactly 3 answers for the field Other Answers!')

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

	# def __init__(self,question, *args, **kwargs):
	# 	super(QuestionMediaForm, self).__init__(*args, **kwargs)
	# 	self.question = question