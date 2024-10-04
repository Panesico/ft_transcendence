from django.db import models
from django import forms

class Profile(models.Model):
    user_id = models.IntegerField(unique=True) # This is the user_id from the authentif app
    display_name = models.CharField(max_length=16, unique=True)
    city = models.CharField(max_length=16, blank=True, default='Málaga')
    country = models.CharField(max_length=16, blank=True, default='Spain')
    played_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)
    friends = models.ManyToManyField('self', blank=True)
    preferred_language = models.CharField(max_length=2,choices=[('en', 'English'),('fr', 'French'),('es', 'Spanish')],default='en')

    # This method is used to display the object in the admin panel
    def __str__(self):
        return f'{self.display_name} from {self.city}, {self.country}'