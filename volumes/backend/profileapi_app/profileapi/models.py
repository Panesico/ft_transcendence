from django.db import models

class Profile(models.Model):
    user_id = models.IntegerField(unique=True) # This is the user_id from the authentif app
    display_name = models.CharField(max_length=16, unique=False, default='MyDisplayName')
    city = models.CharField(max_length=16, blank=True, default='Málaga')
    country = models.CharField(max_length=16, blank=True, default='Spain')
    played_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='media/avatars/', blank=True, null=True, default='media/avatars/default.png')
    friends = models.ManyToManyField('self', blank=True)