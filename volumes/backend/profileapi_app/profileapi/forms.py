from django.http import JsonResponse
from django import forms
from profileapi.models import Profile
import json
import os

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
            print('Profile found:', profile)
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