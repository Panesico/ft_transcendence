from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

# class SignUpForm(forms.ModelForm):    
#     # username = forms.CharField(label="Username", max_length=20)
#     # email = forms.EmailField(label="Email", max_length=50)
#     # password = forms.CharField(widget=forms.PasswordInput)
#     # confirm_password = forms.CharField(widget=forms.PasswordInput)

#     # logger.debug("")
#     # logger.debug("SignUpForm")
#     # logger.debug("")
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password')
#         confirm_password = cleaned_data.get('confirm_password')

#         if password != confirm_password:
#             raise ValidationError("Passwords do not match")

class SignUpForm(forms.ModelForm):
    # username = forms.CharField(max_length=20)
    # password = forms.CharField(label='Password')

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'id': 'signupConfirmPassword'
    }), label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'signupUsername'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'id': 'signupEmail'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control', 'id': 'signupPassword'
            }),
        }

    def clean(self):
        logger.debug("")
        logger.debug("SignUpForm > clean")
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            logger.debug("SignUpForm > clean > if password and confirm_password")
            if password != confirm_password:
                logger.debug("SignUpForm > clean > if password != confirm_password")
                raise ValidationError("Passwords do not match")