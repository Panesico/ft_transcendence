from django.http import HttpResponse
from django.urls import path
from django.http import JsonResponse
import logging
import json
from .models import Profile
from profileapi import views
logger = logging.getLogger(__name__)

urlpatterns = [
    # Signup
    path('api/signup/', views.api_signup, name='api_signup'),

    # Edit profile
    path('api/editprofile/', views.api_edit_profile, name='api_edit_profile'),

    # Getter
    path('api/profile/<str:user_id>/', views.get_profile_api, name='profile_api'),

    # Notifications
    path('api/createnotif/', views.create_notifications, name='create_notifications'),
    path('api/getnotif/<str:user_id>/', views.get_notifications, name='get_notifications'),
    path('api/setnotifasread/<str:sender_id>/<str:receiver_id>/<str:type>/', views.set_notif_as_readen, name='set_notif_as_readen'),
]