"""
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "label": False,
                "rows": 3,
                "placeholder": "Write your thoughts here!",
                "class": "form-control mb-1",
            }
        )
    )
"""
