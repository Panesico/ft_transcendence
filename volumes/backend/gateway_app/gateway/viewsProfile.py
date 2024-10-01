import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .forms import InviteFriendFormFrontend, EditProfileFormFrontend
from django.contrib import messages
import json
import logging
import requests
logger = logging.getLogger(__name__)

def get_profile(request):
    logger.debug("")
    logger.debug("get_profile")
    if request.user.is_authenticated == False:
      return redirect('login')
    if request.method != 'GET':
      return redirect('405')
    form = InviteFriendFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_profile XMLHttpRequest")
        html = render_to_string('fragments/profile_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/profile.html', {'form': form})

def edit_profile(request):
    if request.user.is_authenticated == False:
      return redirect('login')
    logger.debug("")
    logger.debug("edit_profile")
    if request.method == 'GET': 
        return get_edit_profile(request=request)
    elif request.method == 'POST':
        return post_edit_profile(request=request)
    return render('partials/edit_profile.html')
  
def get_edit_profile(request):
    if request.user.is_authenticated == False:
      return redirect('login')
    if request.method != 'GET':
      return redirect('405')
    logger.debug("")
    logger.debug("get_edit_profile")
    initial_data = {'username': request.user.username,
                    'avatar': request.user.avatar,
                    'country': request.user.country,
                    'city': request.user.city,
                    }
    form = EditProfileFormFrontend(initial=initial_data)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("edit_profile XMLHttpRequest")
        html = render_to_string('fragments/edit_profile_fragment.html', {'form': form}, context={}, request=request)
        return JsonResponse({'html': html},request=request)
    return render(request, 'partials/edit_profile.html', {'form': form})
  
def post_edit_profile(request):
    if request.user.is_authenticated == False:
      return redirect('login')
    if request.method != 'POST':
        return redirect('405')
    logger.debug("")
    logger.debug("post_edit_profile")
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }

    data = json.loads(request.body)
    data['user_id'] = request.user.id
    logger.debug(f"data : {data['user_id']}")
    logger.debug(f"post_edit_profile > data: {data}")
    authentif_url = 'https://authentif:9001/api/editprofile/' 

    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))

    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_edit_profile > Response: {response.json()}")
    if response.ok:
        logger.debug('post_edit_profile > Response OK')
        user_response =  JsonResponse({'status': status, 'message': message})
        for cookie in response.cookies:
            user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
        return user_response
    else:
      logger.debug('post_edit_profile > Response KO')
      data = json.loads(request.body)
      form = EditProfileFormFrontend(data)
      form.add_error(None, message)
      html = render_to_string('fragments/edit_profile_fragment.html', {'form': form}, request=request)
      return JsonResponse({'html': html, 'status': status, 'message': message}, status=response.status_code)