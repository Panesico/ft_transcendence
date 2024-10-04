import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .forms import InviteFriendFormFrontend, EditProfileFormFrontend
from django.contrib import messages
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import json
import logging
import requests
logger = logging.getLogger(__name__)

def get_profileapi_variables(request):
  user_id = request.user.id
  profile_api_url = 'https://profileapi:9002/api/profile/' + str(user_id)
  logger.debug(f"get_edit_profile > profile_api_url: {profile_api_url}")
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
  if response.status_code == 200:
    logger.debug(f"-------> get_edit_profile > Response: {response.json()}")
    return response.json()
  else:
    logger.debug(f"-------> get_edit_profile > Response: {response.status_code}")
    return {'avatar': '/media/avatars/default.png',
            'country': 'Spain',
            'city': 'Málaga'}

def get_profile(request):
    logger.debug("")
    logger.debug("get_profile")
    if request.user.is_authenticated == False:
      return redirect('login')
    if request.method != 'GET':
      return redirect('405')
    form = InviteFriendFormFrontend()

    # GET profile user's variables
    profile_data = get_profileapi_variables(request=request)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_profile XMLHttpRequest")
        html = render_to_string('fragments/profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/profile.html', {'form': form, 'profile_data': profile_data})
    #return render(request, 'partials/my_template.html', {'my_avatar': my_avatar})

def get_edit_profile(request):
    if request.user.is_authenticated == False:
        return redirect('login')
    logger.debug("")
    if request.method != 'GET':
        return redirect('405')

    # GET profile user's variables
    profile_data = get_profileapi_variables(request=request)

    form = EditProfileFormFrontend()
    logger.debug(f"get_edit_profile > form: {form}")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_edit_profile > XMLHttpRequest")
        html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/edit_profile.html', {'form': form, 'profile_data': profile_data})

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
        user_response =  JsonResponse({'status': status, 'message': message})
        for cookie in response.cookies:
            user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
        return user_response
        #return render(request, 'partials/home.html', {'status': status, 'message': message})#change this line to return only the fragment
    #handle wrong confirmation password
    else:
      logger.debug('post_edit_profile_general > Response KO')
      #data = json.loads(request.body)
#      html = render_to_string('fragments/edit_profile_fragment.html', {'form': form}, request=request)
      return render(request, 'partials/edit_profile.html', {'status': status, 'message': message})


def post_edit_profile_avatar(request):
  if request.user.is_authenticated == False:
    return redirect('login')
  if request.method != 'POST':
      return redirect('405')
  logger.debug("")
  logger.debug("post_edit_profile_avatar")
  authentif_url = 'https://profileapi:9002/api/editprofile/'
  csrf_token = request.COOKIES.get('csrftoken')
  headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }
  data = request.POST.copy()
  uploaded_file = request.FILES['avatar']
  # Save the uploaded file
  avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
  fs = FileSystemStorage(location=avatar_dir)
  filename = fs.save(uploaded_file.name, uploaded_file)

  data['user_id'] = request.user.id
  data['avatar'] = '/media/avatars/' + filename
  logger.debug(f"post_edit_profile_avatar > data: {data}")

  # send the file path to the profile api
  response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
  if response.ok:
    logger.debug('post_edit_profile_avatar > Response OK')
    user_response =  JsonResponse({'status': 'success', 'message': 'Avatar updated successfully'})
    for cookie in response.cookies:
      user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
    return user_response
    #return render(request, 'partials/home.html')
  else:
    logger.debug('post_edit_profile_avatar > Response KO')
    return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the avatar'}, status=response.status_code)
 
def upload_file(request):
  if request.method == 'POST' and request.FILES['myfile']:
      print('request.FILES: ', request.FILES)
      myfile = request.FILES['myfile']
      fs = FileSystemStorage()
      filename = fs.save(myfile.name, myfile)
      uploaded_file_url = fs.url(filename)
      return render(request, 'partials/upload.html', {
          'uploaded_file_url': uploaded_file_url
      })
  return render(request, 'partials/upload.html')
