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

def post_invite(request):
  logger.debug('post_invite')
  if request.method != 'POST':
    return redirect('405')
  logger.debug('post_invite > POST')
  csrf_token = request.COOKIES.get('csrftoken')
  headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }
  # logger.debug('post_invite > data: %s', data)
  # logger.debug('post_invite > Response: %s', response)
  #status = response.json().get("status")
  #message = response.json().get("message")
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