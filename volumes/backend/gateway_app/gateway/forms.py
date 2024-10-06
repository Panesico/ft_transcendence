from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class LogInFormFrontend(forms.Form):
  username = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'loginUsername'
          }),
        label=_('Username'), 
        required=True,
  )
  password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'loginPassword'
          }), 
        label=_('Password'), 
        required=True
  )

class SignUpFormFrontend(forms.Form):
  username = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'signupUsername'
          }),
        label=_('Username'), 
        required=True,
        )
  password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'signupPassword'
          }), 
        label=_('Password'), 
        required=True
        )
  confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'signupConfirmPassword'
          }), 
        label=_('Confirm Password'), 
        required=True
        )

class InviteFriendFormFrontend(forms.Form):
  friendName = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
						'type': 'text',
            'class': 'form-control',
            'id': 'login-name'
          }),
        label=_("Friend's Name"),
        required=True,
        )

class EditProfileFormFrontend(forms.Form):
  avatar = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'editProfileAvatar'
          }),
        label=_('Upload avatar'),
        required=False,
        )
  username = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileUsername'
          }),
        label=_('Username'), 
        required=False,
        )
  display_name = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileDisplayName'
          }),
        label=_('DisplayName'), 
        required=False,
        )
  country = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileCountry'
          }),
        label=_('Country'), 
        required=False,
        )
  city = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileCity'
          }),
        label=_('City'), 
        required=False,
        )

  new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'editProfilePassword'
          }), 
        label=_('New password'), 
        required=False
        )
  confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
          'class': 'form-control',
          'id': 'editProfileConfirmPassword'
          }), 
        label=_('Confirm new Password'), 
        required=False
        )

  
class TournamentFormFrontend(forms.Form):
  player1 = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'value': 'Name1',
            'class': 'form-control',
            'id': 'namePlayer1'
          }),
        label=_("Player 1"),
        required=True,
        )
  player2 = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'value': 'Name2',
            'class': 'form-control',
            'id': 'namePlayer2'
          }),
        label=_("Player 2"),
        required=True,
        )
  player3 = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'value': 'Name3',
            'class': 'form-control',
            'id': 'namePlayer3'
          }),
        label=_("Player 3"),
        required=True,
        )
  player4 = forms.CharField(
        max_length=16, 
        widget=forms.TextInput(attrs={
            'value': 'Name4',
            'class': 'form-control',
            'id': 'namePlayer4'
          }),
        label=_("Player 4"),
        required=True,
        )
  
  player1_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
  
  def clean(self):
      cleaned_data = super().clean()
      player1 = cleaned_data.get("player1")
      player2 = cleaned_data.get("player2")
      player3 = cleaned_data.get("player3")
      player4 = cleaned_data.get("player4")

      players = [player1, player2, player3, player4]
      if len(players) != len(set(players)):
          raise ValidationError(_("Player names must be unique."))

      return cleaned_data
  