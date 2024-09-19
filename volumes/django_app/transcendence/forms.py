from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

class SignUpForm(forms.ModelForm):    
    # username = forms.CharField(label="Username", max_length=20)
    # email = forms.EmailField(label="Email", max_length=50)
    # password = forms.CharField(widget=forms.PasswordInput)
    # confirm_password = forms.CharField(widget=forms.PasswordInput)

    # logger.debug("")
    # logger.debug("SignUpForm")
    # logger.debug("")
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords do not match")
