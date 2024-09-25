from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
from authentif.models import User
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

class SignUpForm(forms.ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'id': 'signupConfirmPassword'
    }), label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'signupUsername'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control', 'id': 'signupPassword'
            }),
        }

    def clean(self):
        logger.debug("SignUpForm > clean")
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            logger.debug("SignUpForm > clean > if password and confirm_password")
            if password != confirm_password:
                logger.debug("SignUpForm > clean > if password != confirm_password")
                raise ValidationError("Passwords do not match")
        return cleaned_data

    
class LogInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'id': 'loginUsername'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'id': 'loginPassword'
    }))