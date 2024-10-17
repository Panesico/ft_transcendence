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
	
def getSentChatMessages(request, user_id):
	id = int(user_id)
	if request.method == 'GET':
		try:
			user = Profile.objects.get(user_id=id)
			messages = Message.objects.filter(send_user=user)
			data = []
			for message in messages:
				data.append({
					'send_user': message.send_user.user_id,
					'dest_user': message.dest_user.user_id,
					'message': message.message,
					'timestamp': message.timestamp,
					'read': message.read
				})
			return JsonResponse(data, safe=False)
		except DatabaseError as e:
			return JsonResponse({'message': 'Error getting messages'}, status=400)
	else:
		return JsonResponse({'message': 'Method not allowed'}, status=405)
	
def getReceivedChatMessages(request, user_id):
	id = int(user_id)
	if request.method == 'GET':
		try:
			user = Profile.objects.get(user_id=id)
			messages = Message.objects.filter(dest_user=user)
			data = []
			for message in messages:
				data.append({
					'send_user': message.send_user.user_id,
					'dest_user': message.dest_user.user_id,
					'message': message.message,
					'timestamp': message.timestamp,
					'read': message.read
				})
			return JsonResponse(data, safe=False)
		except DatabaseError as e:
			return JsonResponse({'message': 'Error getting messages'}, status=400)
	else:
		return JsonResponse({'message': 'Method not allowed'}, status=405)
	
def markChatAsRead(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		logger.debug(f'data: {data}')
		try:
			message = Message.objects.get(id=data['message_id'])
			message.read = True
			message.save()
			return JsonResponse({'message': 'Message marked as read'}, status=201)
		except DatabaseError as e:
			return JsonResponse({'message': 'Error marking message as read'}, status=400)
	else:
		return JsonResponse({'message': 'Method not allowed'}, status=405)