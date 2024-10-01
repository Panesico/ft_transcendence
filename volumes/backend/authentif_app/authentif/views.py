from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from authentif.forms import SignUpForm, LogInForm, EditProfileForm
from authentif.models import User
from django.contrib.auth.decorators import login_required
import json
import os
import requests
import logging
logger = logging.getLogger(__name__)

def api_logout(request):
    logger.debug("api_logout")
    if request.method == 'GET':
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_login(request):
    logger.debug("api_login")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          # logger.debug(f'Received data: {data}')
          form = LogInForm(request, data=data)
          if form.is_valid():
              user = form.get_user()
              login(request, user)
              logger.debug('api_login > User logged in')
              return JsonResponse({'status': 'success', 'message': 'Login successful'})
          else:
              logger.debug('api_login > Invalid username or password')
              return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=401)
        except json.JSONDecodeError:
            logger.debug('api_login > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    logger.debug('api_login > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# Create a profile linked to user through call to profileapi service
def createProfile(username, user_id, csrf_token):
    profileapi_url = 'https://profileapi:9002/api/signup/'
    profile_data = { 'user_id': user_id, 'username': username }
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'HTTP_HOST': 'profileapi',
        'Referer': 'https://authentif:9001',
    }

    try:
        response = requests.post(
            profileapi_url, json=profile_data, headers=headers, verify=os.getenv("CERTFILE"))
        logger.debug(f'api_signup > createProfile > Response: {response}')
        logger.debug(f'api_signup > createProfile > Response status code: {response.status_code}')
        
        response.raise_for_status()
        if response.status_code == 201:
            logger.debug('api_signup > createProfile > Profile created in profile service')
            return True
        else:
            logger.error(f'api_signup > createProfile > Unexpected status code: {response.status_code}')
            return False
    except requests.RequestException as e:
        logger.error(f'api_signup > createProfile > Failed to create profile: {e}')
        return False

def api_signup(request):
    logger.debug("api_signup")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          # logger.debug(f'Received data: {data}')
          form = SignUpForm(data=data)
          if form.is_valid():
              user = form.save(commit=False)
              user.password = make_password(data['password'])
              user = form.save()

              username = data.get('username')
              password = data.get('password')
              logger.info(f'api_signup > User.username: {user.username}, hased pwd {user.password}')

              try:
                  user_obj = User.objects.get(username=username)
              except User.DoesNotExist:
                  logger.debug(f'api_signup > User not found: {username}')
                  user.delete()
                  return JsonResponse({
                      'status': 'error', 
                      'message': 'User not found'
                  }, status=400)

              # Check if the user is active
              if not user_obj.is_active:
                  logger.debug('api_signup > User is inactive')
                  user.delete()
                  return JsonResponse({
                      'status': 'error', 
                      'message': 'User is inactive'
                  }, status=400)
              
              csrf_token = request.COOKIES.get('csrftoken')
              # Create a profile through call to profileapi service
              if not createProfile(username, user.id, csrf_token):
                    user.delete()
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Failed to create profile'
                    }, status=500)

              user = authenticate(username=username, password=password)
              if user is not None:
                  logger.debug('api_signup > Sign up successful')
                  login(request, user)
                  return JsonResponse({
                      'status': 'success',
                      'message': 'Sign up successful',
                  })
              else:
                  user.delete()
                  logger.debug('api_signup > Authentication failed')
                  return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=401)
          else:
              logger.debug('api_signup > Invalid form')
              errors = json.loads(form.errors.as_json())
              logger.debug(f'Errors: {errors}')
              # message = errors.get('username')[0].get('message')
              message = None
              if errors:
                message = next((error['message'] for field_errors in errors.values() for error in field_errors), None)
              logger.debug(f'message: {message}')
              return JsonResponse({'status': 'error', 'message': message}, status=400)
        except json.JSONDecodeError:
            logger.debug('api_signup > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f'api_signup > Unexpected error: {e}')
            return JsonResponse({
                'status': 'error', 
                'message': 'An unexpected error occurred'
            }, status=500)
    logger.debug('api_signup > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_check_exists(request):
    logger.debug("api_check_exists")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          username = data.get('username')
          if User.objects.filter(username=username).exists():
              logger.debug('api_check_exists > User exists')
              return JsonResponse({'status': 'success', 'message': 'User exists'})
          else:
              logger.debug('api_check_exists > User does not exist')
              return JsonResponse({'status': 'failure', 'message': 'User does not exist'}, status=404)
        except json.JSONDecodeError:
            logger.debug('api_check_exists > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    logger.debug('api_check_exists > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def api_edit_profile(request):
  logger.debug("api_edit_profile")
  if request.method == 'POST':
    try:
      data = json.loads(request.body)
      user_id = data.get('user_id')
      user_id = data.get('user_id')
      logger.debug(f'user_id: {user_id}')
      try :
        logger.debug(f'extract user_obj')
        user_obj = User.objects.get(id=user_id)
        #user_obj = User.objects.filter(id=user_id).first()
        logger.debug(f'user_obj username: {user_obj.username}')
        form = EditProfileForm(data, instance=user_obj)
        logger.debug(f'form: {form}')
      except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
      if form.is_valid():
        logger.debug('api_edit_profile > Form is valid')
        form.save()
        return JsonResponse({'status': 'success', 'message': 'Profile updated', 'status': 200})
      else:
        logger.debug('api_edit_profile > Form is invalid')
        return JsonResponse({'status': 'error', 'message': 'Invalid profile update'}, status=400)
    except json.JSONDecodeError:
      logger.debug('api_edit_profile > Invalid JSON')
      return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
  else:
    logger.debug('api_edit_profile > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)