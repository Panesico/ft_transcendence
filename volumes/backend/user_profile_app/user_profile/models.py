from django.db import models

class Profile(models.Model):
    user_id = models.IntegerField(max_length=30) # This is the user_id from the authentif app
    city = models.CharField(max_length=100, blank=True, default='Málaga')
    country = models.CharField(max_length=100, blank=True, default='Spain')
    played_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png')
    friends = models.ManyToManyField('self', blank=True)