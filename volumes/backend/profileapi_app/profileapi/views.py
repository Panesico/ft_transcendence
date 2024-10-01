from django.http import JsonResponse
from profileapi.forms import InviteFriendForm
import json
import os
import requests
import logging
logger = logging.getLogger(__name__)

def api_signup(request):
    logger.debug("--> hello from api_signup")
    if (request.method != 'POST'):
        logger.debug("Method not allowed")
        return HttpResponse('Method not allowed', status=405)
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'HTTP_HOST': 'profileapi',
    }
    logger.debug("--> POST method")
    data = json.loads(request.body)
    logger.debug(f"data : {data['user_id']}")
    logger.debug(f"data : {data['username']}")
    try:
      profile = Profile(
      user_id=data['user_id'],
      username=data['username'],
      )
      profile.save()
      logger.debug("--> profile created")
      return JsonResponse({'message': 'Signup successful'}, status=201)
    except Exception as e:
      return JsonResponse({'error': str(e)}, status=400)
    else:
      return JsonResponse({'error': 'Method not allowed'}, status=405)


def api_invite_request(request):
  logger.debug("api_invite_request")
  if request.method == 'POST':
    try:
      data = json.loads(request.body)
      form = InviteFriendForm(data)
      if form.is_valid():
        logger.debug('api_invite_request > Form is valid')         
        return JsonResponse({'status': 'success', 'message': 'Invite request sent', 'status': 200})
      else:
        logger.debug('api_invite_request > Form is invalid')
        return JsonResponse({'status': 'error', 'message': 'Invalid invite request'}, status=400)
    except json.JSONDecodeError:
      logger.debug('api_invite_request > Invalid JSON')
      return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
  else:
    logger.debug('api_invite_request > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

