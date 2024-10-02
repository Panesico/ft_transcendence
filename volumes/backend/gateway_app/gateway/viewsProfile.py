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

def get_edit_profile(request):
    if request.user.is_authenticated == False:
        return redirect('login')
    logger.debug("")
    if request.method != 'GET':
        return redirect('405')
    user_id = request.user.id
    profile_api_url = 'https://profileapi:9002/api/profile/' + str(user_id)
    logger.debug(f"get_edit_profile > profile_api_url: {profile_api_url}")
    response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
    if response.status_code == 200:
      logger.debug(f"-------> get_edit_profile > Response: {response.json()}")
    else:
      logger.debug(f"-------> get_edit_profile > Response: {response.status_code}")
    initial_data = {'username': request.user.username,
                    'avatar': request.user.avatar,
                    'country': request.user.country,
                    'city': request.user.city,
                    }
    form = EditProfileFormFrontend(initial=initial_data)
    logger.debug(f"get_edit_profile > form: {form}")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_edit_profile > XMLHttpRequest")
        html = render_to_string('fragments/edit_profile_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/edit_profile.html', {'form': form})

def post_edit_profile_security(request):
    if request.user.is_authenticated == False:
      return redirect('login')
    if request.method != 'POST':
        return redirect('405')
    logger.debug("")
    logger.debug("post_edit_profile_security")
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }
#    data = json.loads(request.body)
    data = request.POST.copy()
    logger.debug(f"post data : {data}")
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
      # logger.debug('post_edit_profile > Response OK')
      # html = render_to_string('partials/login.html', context={}, request=request)
      # user_response =  JsonResponse({'html': html, 'status': status, 'message': message})
      # for cookie in response.cookies:
      #   user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
      # return user_response
      return render(request, 'partials/home.html', {'status': status, 'message': message})#create a page to redirect to login page
    #handle wrong confirmation password
    else:
      logger.debug('post_edit_profile > Response KO')
      #data = json.loads(request.body)
      #form = EditProfileFormFrontend(data)
      #form.add_error(None, message)
      #html = render_to_string('fragments/edit_profile_fragment.html', request=request)
      #return JsonResponse({'html': html, 'status': status, 'message': message}, status=response.status_code)
      return render(request, 'partials/edit_profile.html', {'status': status, 'message': message})#change this line to return only the fragment
      

def post_edit_profile_general(request):
    if request.user.is_authenticated == False:
      return redirect('login')
    if request.method != 'POST':
        return redirect('405')
    logger.debug("")
    logger.debug("post_edit_profile_general")
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }
    #data = json.loads(request.body)
    data = request.POST.copy()
    logger.debug(f"post data : {data}")
    data['user_id'] = request.user.id
    logger.debug(f"user_id : {data['user_id']}")
    logger.debug(f"post_edit_profile > data: {data}")
    authentif_url = 'https://profileapi:9002/api/editprofile/' 

    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))

    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_edit_profile_general > Response: {response.json()}")
    if response.ok:
        logger.debug('post_edit_profile_general > Response OK')      
        # user_response =  JsonResponse({'status': status, 'message': message})
        # for cookie in response.cookies:
        #     user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
        # return user_response
        return render(request, 'partials/home.html', {'status': status, 'message': message})#change this line to return only the fragment
    #handle wrong confirmation password
    else:
      logger.debug('post_edit_profile_general > Response KO')
      #data = json.loads(request.body)
#      html = render_to_string('fragments/edit_profile_fragment.html', {'form': form}, request=request)
      return render(request, 'partials/edit_profile.html', {'status': status, 'message': message})

def get_test_profileapi(request):
    if request.user.is_authenticated == False:
        return redirect('login')
    logger.debug("")
    logger.debug("get_test_profileapi")
    if request.method != 'GET':
        return redirect('405')
    user_id = request.user.id
    profile_api_url = 'https://profileapi:9002/api/profile/' + str(user_id)
    logger.debug(f"get_edit_profile > profile_api_url: {profile_api_url}")
    response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
    data = response.json()
    if response.status_code == 200:
      logger.debug(f"-------> get_edit_profile > Response: {response.json()}")
    else:
      logger.debug(f"-------> get_edit_profile > Response: {response.status_code}")
    return render(request, 'partials/test_profileapi.html', data)