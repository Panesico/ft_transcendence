from django.http import HttpResponse
from django.urls import path
from django.http import JsonResponse
import logging
import json
from .models import Profile
from profileapi import views
logger = logging.getLogger(__name__)

urlpatterns = [
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/inviterequest/', views.api_invite_request, name='api_invite_request'),
    path('api/editprofile/', views.api_edit_profile, name='api_edit_profile'),
]