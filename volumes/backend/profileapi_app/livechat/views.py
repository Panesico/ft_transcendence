from django.shortcuts import render
from django.http import JsonResponse
from livechat.models import Message
from django.db import DatabaseError
from profileapi.models import Profile
import json
import os
import requests
import logging
logger = logging.getLogger(__name__)

# Create your views here.
def saveChatMessage(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		logger.debug(f'data: {data}')
		sender = Profile.objects.get(user_id=data['sender_id'])
		receiver = Profile.objects.get(user_id=data['receiver_id'])
		try:
			message = Message(
				send_user=sender,
				dest_user=receiver,
				message=data['message'],
				timestamp=data['date']
			)
			message.save()
			return JsonResponse({'message': 'Message saved'}, status=201)
		except DatabaseError as e:
			return JsonResponse({'message': 'Error saving message'}, status=400)
	else:
		return JsonResponse({'message': 'Method not allowed'}, status=405)