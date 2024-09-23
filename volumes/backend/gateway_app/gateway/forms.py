from django import forms

class LogInFormFrontend(forms.Form):
  username = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'loginUsername'
          }),
        label='Username', 
        required=True,
        )
  password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'loginPassword'
          }), 
        label='Password', 
        required=True
        )

class SignUpFormFrontend(forms.Form):
  username = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'signupUsername'
          }),
        label='Username', 
        required=True,
        )
  password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'signupPassword'
          }), 
        label='Password', 
        required=True
        )
  confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'signupConfirmPassword'
          }), 
        label='Confirm Password', 
        required=True
        )
