from .models import Post
from django.forms import ModelForm
from django import forms

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    extra_field = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "extra_field", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.extra_field = self.cleaned_data["extra_field"]
        if commit:
            user.save()
        return user

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super(PostForm, self).save(commit=False)
        inst.user = self._user
        if commit:
            inst.save()
            self.save_m2m()
        return inst
     
