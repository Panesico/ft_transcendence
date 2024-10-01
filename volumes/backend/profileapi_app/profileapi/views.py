from django.http import JsonResponse
from profileapi.forms import InviteFriendForm
from profileapi.models import Profile
from profileapi.forms import EditProfileForm
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

def api_edit_profile(request):
    logger.debug("api_edit_profile")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f'data: {data}')
            user_id = data.get('user_id')
            logger.debug(f'user_id: {user_id}')

            # Use get_object_or_404 to handle the case where the user is not found
            user_obj = Profile.objects.get(user_id=user_id)
            logger.debug('user_obj recovered')

            # Log the current profile data
            logger.debug(f'username: {user_obj.username}')
            logger.debug(f'avatar: {user_obj.avatar}')
            logger.debug(f'country: {user_obj.country}')
            logger.debug(f'city: {user_obj.city}')

            # Ensure data is passed as a dictionary
            form = EditProfileForm(data, instance=user_obj)
            logger.debug(f'form: {form}')
            # Log the current profile data
            logger.debug('------------------------------')
            logger.debug(f'username: {user_obj.username}')
            logger.debug(f'avatar: {user_obj.avatar}')
            logger.debug(f'country: {user_obj.country}')
            logger.debug(f'city: {user_obj.city}')

            if form.is_valid():
                logger.debug('api_edit_profile > Form is valid')
                form.save()
                return JsonResponse({'status': 'success', 'message': 'Profile updated'}, status=200)
            else:
                logger.debug('api_edit_profile > Form is invalid')
                return JsonResponse({'status': 'error', 'message': 'Invalid profile data'}, status=400)
        except json.JSONDecodeError:
            logger.debug('api_edit_profile > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        logger.debug('api_edit_profile > Method not allowed')
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)