import os, json, logging, requests
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .forms import InviteFriendFormFrontend, EditProfileFormFrontend, LogInFormFrontend
from django.contrib import messages
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
logger = logging.getLogger(__name__)

def get_profileapi_variables(request):
  user_id = request.user.id
  profile_api_url = 'https://profileapi:9002/api/profile/' + str(user_id)
  logger.debug(f"get_profileapi_variables > profile_api_url: {profile_api_url}")
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
  if response.status_code == 200:
    logger.debug(f"-------> get_edit_profile > Response: {response.json()}")
    return response.json()
  else:
    logger.debug(f"-------> get_edit_profile > Response: {response.status_code}")
    return {'avatar': '/media/avatars/default.png',#Need to be handled better
            'country': 'Spain',
            'city': 'Málaga',
            'display_name': 'MyDisplayName',
            'preferred_language': 'en',
            }

@login_required
def get_profile(request):
    logger.debug("")
    logger.debug("get_profile")
    if request.method != 'GET':
      return redirect('405')
    form = InviteFriendFormFrontend()

    # GET profile user's variables
    profile_data = get_profileapi_variables(request=request)
    logger.debug(f"get_profile > profile_data: {profile_data}")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_profile XMLHttpRequest")
        html = render_to_string('fragments/profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
        return JsonResponse({'html': html, 'status': 'success'})
    return render(request, 'partials/profile.html', {'form': form, 'profile_data': profile_data})

@login_required
def get_edit_profile(request):
    logger.debug("")
    logger.debug("get_edit_profile called")
    if request.method != 'GET':
        return redirect('405')

    # GET profile user's variables
    profile_data = get_profileapi_variables(request=request)
    logger.debug(f"get_edit_profile > profile_data: {profile_data}")

    form = EditProfileFormFrontend()
    # logger.debug(f"get_edit_profile > form: {form}")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_edit_profile > XMLHttpRequest")
        html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/edit_profile.html', {'form': form, 'profile_data': profile_data})

@login_required
def get_match_history(request):
    if request.method != 'GET':
        return redirect('405')
    logger.debug("get_match_history")
    user_id = request.user.id
    get_history_url = 'https://play:9003/api/getGames/' + str(user_id)
    response = requests.get(get_history_url, verify=os.getenv("CERTFILE"))
    if response.status_code == 200:
        games_data = response.json().get('games_data')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
          html = render_to_string('fragments/match_history_fragment.html', {'games_data' : games_data, 'user_id' : user_id}, request=request)
          return JsonResponse({'html': html, 'status': 'success'})
        return render(request, 'partials/match_history.html', {'games_data': games_data, 'user_id' : user_id})
    else:
        logger.debug(f"-------> get_match_history > Response: {response.status_code}")
        return JsonResponse({'status': 'error', 'message': 'Error retrieving match history'})

@login_required
def post_edit_profile_security(request):
    if request.method != 'POST':
        return redirect('405')
    logger.debug("")
    logger.debug("post_edit_profile_security")

    # Cookies & headers
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }

    # Recover data from the form
    data = json.loads(request.body)
    data['user_id'] = request.user.id
    logger.debug(f"data : {data['user_id']}")
    logger.debug(f"post_edit_profile > data: {data}")

    # Send and recover response from the profileapi service
    authentif_url = 'https://authentif:9001/api/editprofile/' 
    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_edit_profile > Response: {response.json()}")
    
     # Redirection usage
    form = LogInFormFrontend()
    profile_data = get_profileapi_variables(request=request)

    if response.ok:
      logger.debug('post_edit_profile > Response OK')
      html = render_to_string('fragments/login_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
      user_response =  JsonResponse({'html': html, 'status': status, 'message': message})
      for cookie in response.cookies:
        user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
      return user_response

    #handle wrong confirmation password
    else:
      profile_data = get_profileapi_variables(request=request)
      data = json.loads(request.body)
      form = EditProfileFormFrontend(data)
      form.add_error(None, message)
      logger.debug('post_edit_profile_general > Response KO')

      html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
      return JsonResponse({'html': html, 'status': status, 'message': message}, status=response.status_code)
      #return render(request, 'partials/edit_profile.html', {'status': status, 'message': message, 'form': form, 'profile_data': profile_data})#change this line to return only the fragment
      
@login_required
def post_edit_profile_general(request):
    logger.debug("")
    logger.debug("post_edit_profile_general")
    if request.method != 'POST':
        return redirect('405')

    # Cookies & headers
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }


    # Recover data from the form
    data = json.loads(request.body)
    logger.debug(f"post data : {data}")
    data['user_id'] = request.user.id
    logger.debug(f"user_id : {data['user_id']}")
    logger.debug(f"post_edit_profile > data: {data}")

    # Send and recover response from the profileapi service
    authentif_url = 'https://profileapi:9002/api/editprofile/' 
    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_edit_profile_general > Response: {response.json()}")

    # Redirection usage
    form = EditProfileFormFrontend()
    profile_data = get_profileapi_variables(request=request)
    if response.ok:
        logger.debug('post_edit_profile_general > Response OK')      
            #construct html to return
        preferred_language = profile_data.get('preferred_language')
        logger.debug(f"post_edit_profile > preferred_language: {preferred_language}")
        html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data, 'preferred_language': preferred_language}, request=request)
        user_response =  JsonResponse({'html': html, 'status': status, 'message': message, 'preferred_language': preferred_language})
        #for cookie in response.cookies:
        #    user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
        user_response.set_cookie('django_language', preferred_language, domain='localhost', httponly=True, secure=True)
        return user_response
        
    #handle displayName already taken
    else:
      profile_data = get_profileapi_variables(request=request)
      logger.debug('profile_data: %s', profile_data)
      data = json.loads(request.body)
      form = EditProfileFormFrontend(data)
      form.add_error(None, message)
      logger.debug('post_edit_profile_general > Response KO')
      logger.debug(f"post_edit_profile > data: {data}")
      logger.debug(f"post_edit_profile > response: {response.json()}")
      html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
      return JsonResponse({'html': html, 'status': status, 'message': message}, status=response.status_code)

@login_required
def post_edit_profile_avatar(request):
  if request.method != 'POST':
      return redirect('405')

  # Cookies & headers
  logger.debug("")
  logger.debug("post_edit_profile_avatar")
  csrf_token = request.COOKIES.get('csrftoken')
  headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }

  # Redirection usage
  form = EditProfileFormFrontend()
  profile_data = get_profileapi_variables(request=request)

  # Recover data from the form
  data = request.POST.copy()
  logger.debug("request.FILES: %s", request.FILES)
  logger.debug(f"post data : {data}")

  # Check if the avatar file is empty
  if request.FILES.get('avatar') is not None:
      
    # Get the uploaded file   
    uploaded_file = request.FILES['avatar']

    # Save the uploaded file
    avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
    fs = FileSystemStorage(location=avatar_dir)
    filename = fs.save(uploaded_file.name, uploaded_file)

    # Construct the data to send to the profileapi service
    data['user_id'] = request.user.id
    data['avatar'] = '/avatars/' + filename
    logger.debug(f"post_edit_profile_avatar > data: {data}")
    authentif_url = 'https://authentif:9001/api/editprofile/' 
    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_edit_profile > Response: {response.json()}")
    html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)

    if  response.ok:
        logger.debug('post_edit_profile_avatar > Response OK')
        user_response =  JsonResponse({'html': html, 'status': 'success', 'message': 'Avatar updated successfully'})
        for cookie in response.cookies:
          user_response.set_cookie(cookie.key, cookie.value, domain='localhost', httponly=True, secure=True)
        return user_response
    else:
      form = EditProfileFormFrontend()
      profile_data = get_profileapi_variables(request=request)
      logger.debug('post_edit_profile > Response KO')
      html = render_to_string('fragments/edit_profile_fragment.html', {'status': status, 'message': message, 'form': form, 'profile_data': profile_data}, request=request)
      return JsonResponse({'html': html, 'status': status, 'message': message})
  
  # Handle the case where no file is uploaded
  else:
    logger.debug('post_edit_profile_avatar > No file uploaded')
    profile_data = get_profileapi_variables(request=request)
    logger.debug('profile_data: %s', profile_data)
    form = EditProfileFormFrontend(data)
    form.add_error(None, 'Please select a file to upload')
    html = render_to_string('fragments/edit_profile_fragment.html', {'form': form, 'profile_data': profile_data}, request=request)
    return JsonResponse({'html': html, 'status': 'error'}, status=400)

