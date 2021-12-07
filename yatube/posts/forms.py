# posts/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_text(self):
        text = self.cleaned_data['text']
        if text:
            return text
        raise ValidationError('This field is required')

    def clean_group(self):
        group = self.cleaned_data['group']
        return group
