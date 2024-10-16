from django.shortcuts import render
from django.http import JsonResponse
from livechat.models import Message
from django.db import DatabaseError
import json
import os
import requests
import logging

# Create your views here.
def saveChatMessage(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		logger.debug(f'data: {data}')
		try:
			message = Message(
				sender_id=data['sender_id'],
				receiver_id=data['receiver_id'],
				message=data['message'],
				date=data['date']
			)
			message.save()
			return JsonResponse({'message': 'Message saved'}, status=201)
		except DatabaseError as e:
			return JsonResponse({'message': 'Error saving message'}, status=400)
	else:
		return JsonResponse({'message': 'Method not allowed'}, status=405)