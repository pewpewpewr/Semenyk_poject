from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обов\'язково вкажіть діючу електронну адресу.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
