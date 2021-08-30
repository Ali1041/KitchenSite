from django import forms
from .models import *


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        exclude = ('region', 'street_address')


class UserRegistrationForm(forms.ModelForm):
    password_1 = forms.CharField(max_length=255, widget=forms.PasswordInput(attrs={'required':True}))

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_1')
