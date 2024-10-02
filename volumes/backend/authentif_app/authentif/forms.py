from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
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

class EditProfileForm(UserChangeForm):

    # current_password = forms.CharField(widget=forms.PasswordInput(attrs={
    #     'class': 'form-control', 'id': 'currentPassword'
    # }), label='Current Password')
    new_username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'id': 'newUsername'
    }), label='New Username', required=False)

    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'id': 'newPassword'
    }), label='New Password', required=False)

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'id': 'signupConfirmPassword'
    }), label='Confirm Password', required=False)

    def __init__(self, *args, **kwargs):
        logger.debug("EditProfileForm > __init__")
        super(EditProfileForm, self).__init__(*args, **kwargs)
        logger.debug(f"self.fields: {self.fields}")
        del self.fields['password']
        logger.debug("Password field deleted")

    class Meta:
        logger.debug("EditProfileForm > Meta")
        model = User
        logger.debug(f"model: {model}")
        fields = ('username','city','country', 'avatar')
        logger.debug(f"fields: {fields}")



    def clean(self):
        logger.debug("EditProfileForm > clean")
        logger.debug(f"new_password: {self.cleaned_data.get('new_password')}")
        logger.debug(f"confirm_password: {self.cleaned_data.get('confirm_password')}")
        logger.debug(f"new_username: {self.cleaned_data.get('username')}")
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        new_username = cleaned_data.get('username')
        # current_password = cleaned_data.get('current_password')

        # Validate current password
        if new_password and confirm_password:
            logger.debug("EditProfileForm > clean > if password and confirm_password")
            if new_password != confirm_password:
                logger.debug("EditProfileForm > clean > if password != confirm_password")
                raise ValidationError("Passwords do not match")
            else:
              self.instance.set_password(new_password)
              if new_username:
                self.instance.username = new_username
        logger.debug("EditProfileForm > clean > return cleaned_data")
        return cleaned_data
