from django import forms
from .models import Post,Comment,Story


class PostForm(forms.ModelForm):
    content =forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    caption =forms.CharField(widget=forms.Textarea(attrs={'class': 'input is-medium'}),required=True)

    class Meta:
        model=Post
        fields=['caption','content']

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['body']   

class StoryForm(forms.ModelForm):
    content =forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    text =forms.CharField(widget=forms.Textarea(attrs={'class': 'input is-medium'}))
    class Meta:
        model=Story
        fields=['text','content']
