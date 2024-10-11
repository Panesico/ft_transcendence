import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .forms import InviteFriendFormFrontend
from django.contrib import messages
import json
import logging
import requests
logger = logging.getLogger(__name__)

def get_authentif_variables(user_id):
  profile_api_url = 'https://authentif:9001/api/getUserInfo/' + str(user_id)
  logger.debug(f"get_authentif_variables > profile_api_url: {profile_api_url}")
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
  if response.status_code == 200:
    return response.json()
  else:
    logger.debug(f"-------> get_edit_profile > Response: {response}")
    return None

def post_invite(request):
  logger.debug("")
  logger.debug('post_invite')
  if request.method != 'POST':
    return redirect('405')
  csrf_token = request.COOKIES.get('csrftoken')

  # Cookies & headers
  headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }

  # Recover data from the form
#  data = json.loads(request.body)
  data = request.POST.dict()
  data['user_id'] = request.user.id
  logger.debug(f"post_edit_profile > data: {data}")
  form = InviteFriendFormFrontend(request.POST)

  # Send and recover response from authentif service
  user_data = get_authentif_variables(request.user.id)
  logger.debug(f"post_invite > User data: {user_data}")
  usernames = user_data.get('usernames')
  users_id = user_data.get('users_id')

  # Check if username exists
  if data['username'] not in usernames:
    status = 'error'
    message = 'Username does not exist'
    form.add_error(None, 'Username does not exist')
    html = render_to_string('fragments/profile_fragment.html', {'form': form}, request=request)
    user_response =  JsonResponse({'html': html, 'status': status, 'message': message})
    return user_response
  else:
    status = 'success'
    message = 'Invitation sent!'
    html = render_to_string('fragments/profile_fragment.html', {'form': form}, request=request)
    user_id = users_id[usernames.index(data['username'])]
    logger.debug(f"post_invite > user_id: {user_id}")
    user_response =  JsonResponse({'html': html, 'status': status, 'message': message, 'username': data['username'], 'user_id': user_id}) 
    return user_response




  form = InviteFriendFormFrontend(request.POST)
  html = render_to_string('fragments/profile_fragment.html', {}, request=request)
  return render(request, 'partials//profile.html', {'status': 'success', 'form': form})
  # if response.ok:
  #   user_response =  JsonResponse({'status': status, 'message': message})
  #   for cookie in response.cookies:
  #     user_response.set_cookie(cookie.key, cookie.value)
  #   return user_response
  # else:
  #   logger.debug('post_invite > Response NOT OK')
  #   logger.debug(message)
  #   html = render_to_string('fragments/profile_fragment.html', {}, request=request)
  #   return JsonResponse({'html': html, 'status': status, 'message': message})