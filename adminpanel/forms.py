from django import forms
from questions.models import Category
from django.forms.widgets import TextInput, Textarea

class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ('name', 'status', 'category_svg', 'details', 'color')
		widgets = {
			'color': TextInput(attrs={'type':'color'}),
			'details': Textarea(),
		}