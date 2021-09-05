from django import forms
from .models import *
from django.core.exceptions import ValidationError


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        exclude = ('region', 'street_address')


class UserRegistrationForm(forms.ModelForm):
    password_1 = forms.CharField(label='Password again', max_length=255,
                                 widget=forms.PasswordInput(attrs={'required': True, 'placeholder': 'Password again'}))

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_1')
        widgets = {
            'password': forms.PasswordInput(attrs={'required': True})
        }

    def clean(self):
        clean_data = self.cleaned_data

        pass1 = clean_data.get('password')
        pass2 = clean_data.get('password_1')

        if pass2 != pass1:
            raise ValidationError('Passwords do not match')
        else:
            return super(UserRegistrationForm, self).clean()
