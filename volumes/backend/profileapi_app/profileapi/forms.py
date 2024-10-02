from django.http import JsonResponse
from django import forms
from profileapi.models import Profile
from django.core.exceptions import ValidationError
import json
import os
import logging
logger = logging.getLogger(__name__)

class InviteFriendForm(forms.ModelForm):
    friendName = forms.CharField(
          max_length=20, 
          widget=forms.TextInput(attrs={
              'type': 'text',
              'class': 'form-control',
              'id': 'login-name'
            }),
          label="Friend's Name",
          required=True,
          )
    class Meta:
          model = Profile  # Specify the model if needed
          fields = ['friendName']

    def clean_friendName(self):
          friend_name = self.cleaned_data.get('friendName')
          print('must check database if friend_name: ', friend_name)
          try:
            profile = Profile.objects.get(username=friend_name)
            print('User ID:', profile.user_id)
            print('City:', profile.city)
            print('Country:', profile.country)
            print('Played Games:', profile.played_games)
            print('Wins:', profile.wins)
            print('Defeats:', profile.defeats)
            print('Avatar:', profile.avatar)
            print('Friends:', profile.friends.all())
          except Profile.DoesNotExist:
            print('Profile not found')
            raise ValidationError("This username does not exist.")
          # if not Profile.objects.filter(username=friend_name).exists():
          #     raise ValidationError("This username does not exist.")
          return friend_name

class EditProfileForm(forms.ModelForm):

  avatar = forms.ImageField(
    widget=forms.FileInput(attrs={
        'class': 'form-control',
        'id': 'editProfileAvatar'
      }),
    label='Upload avatar',
    required=False,
    errors='Upload a valid image'
    )
  username = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileUsername'
          }),
        label='Username', 
        required=True,
        errors='Invalid username'
        )
  country = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileCountry'
          }),
        label='Country', 
        required=True,
        errors='Invalid country'
        )
  city = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'editProfileCity'
          }),
        label='City', 
        required=True,
        errors='Invalid city'
        )
  user_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True,
        errors='Invalid user_id'
        )

  class Meta:
        model = Profile  # Specify the model if needed
        logger.debug(f"model: {model}")
        fields = ['username', 'avatar', 'country', 'city', 'user_id']
        logger.debug(f"fields: {fields}")

  def clean(self):
        cleaned_data = super().clean() # call the clean method of the parent class
        username = cleaned_data.get('username')
        logger.debug(f'username: {username}')
        avatar = cleaned_data.get('avatar')
        logger.debug(f'avatar: {avatar}')
        country = cleaned_data.get('country')
        logger.debug(f'country: {country}')
        city = cleaned_data.get('city')
        logger.debug(f'city: {city}')
        user_id = cleaned_data.get('user_id')
        logger.debug(f'user_id: {user_id}')
        try:
          profile = Profile.objects.get(user_id=user_id)
          print('User ID:', profile.user_id)
          if username:
            profile.username = username
          if avatar:
            profile.avatar = avatar
          if country:
            profile.country = country
          if city:
            profile.city = city
          profile.save()
          logger.debug('forms.py > Profile updated')
        except Profile.DoesNotExist:
          print('Profile not found')
          raise ValidationError("This username does not exist.")
        return cleaned_data
# body{
#     margin-top:20px;
#     background:#f5f5f5;
# }
# /**
#  * Panels
#  */
# /*** General styles ***/
# .panel {
#   box-shadow: none;
# }
# .panel-heading {
#   border-bottom: 0;
# }
# .panel-title {
#   font-size: 17px;
# }
# .panel-title > small {
#   font-size: .75em;
#   color: #999999;
# }
# .panel-body *:first-child {
#   margin-top: 0;
# }
# .panel-footer {
#   border-top: 0;
# }

# .panel-default > .panel-heading {
#     color: #333333;
#     background-color: transparent;
#     border-color: rgba(0, 0, 0, 0.07);
# }

# form label {
#     color: #999999;
#     font-weight: 400;
# }

# .form-horizontal .form-group {
#   margin-left: -15px;
#   margin-left: -15px;
# }
# @media (min-width: 768px) {
#   .form-horizontal .control-label {
#     text-align: right;
#     margin-bottom: 0;
#     padding-top: 7px;
#   }
# }

# .profile__contact-info-icon {
#     float: left;
#     font-size: 18px;
#     color: #999999;
# }
# .profile__contact-info-body {
#     overflow: hidden;
#     padding-left: 20px;
#     color: #999999;
# }
# .profile-avatar {
#   width: 200px;
#   position: relative;
#   margin: 0px auto;
#   margin-top: 196px;
#   border: 4px solid #f3f3f3;
# }