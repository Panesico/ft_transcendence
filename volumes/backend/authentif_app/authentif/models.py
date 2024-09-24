
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(UserManager):
    def _create_user(self, password=None, **extra_fields):        
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(password, **extra_fields)
    
    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(blank=True, default='', unique=True, max_length=20)
    password = models.CharField(max_length=128)

    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    played_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    defeats = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # elo = models.IntegerField(default=1000)
    # wins = models.IntegerField(default=0)
    # loses = models.IntegerField(default=0)
    # ties = models.IntegerField(default=0)
    # token = models.CharField(max_length=128, default='')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # friends = models.ManyToManyField('self', blank=True, related_name='friends_with')
    friends = models.ManyToManyField('self', blank=True)

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['username', 'password']
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.name


