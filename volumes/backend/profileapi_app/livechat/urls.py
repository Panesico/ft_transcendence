from django.http import HttpResponse
from django.urls import path
from django.http import JsonResponse
import logging
import json
from .models import Message
from livechat import views
logger = logging.getLogger(__name__)

urlpatterns = [
    # Save chat message
    path('api/saveChatMessage/', views.saveChatMessage, name='save_chat_message'),
]