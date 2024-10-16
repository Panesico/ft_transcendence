import json
import os
import requests
import logging
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from authentif.forms import SignUpForm, LogInForm, EditProfileForm
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from authentif.models import User
import jwt
from datetime import datetime, timedelta, timezone
from .authmiddleware import login_required, generate_guest_token, JWTAuthenticationMiddleware
logger = logging.getLogger(__name__)

def generate_jwt_token(user):
    secret_key = os.environ.get('DJANGO_SECRET_KEY')  # Load the secret key from env variable
    if not secret_key:
        raise Exception("JWT_SECRET_KEY environment variable is missing")
    
    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),  # Token expiration time
        'iat': datetime.now(timezone.utc),  # Issued at time
    }

    # Ensure you're using a secure algorithm, like HS256
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    return token


def api_get_user_info(request, user_id):
    logger.debug("api_get_user_info")
    try:
        users = User.objects.all()
        users_id = [user.id for user in users]
        user = User.objects.get(id=user_id)
        if user:
            username = user.username
            avatar_url = user.avatar.url if user.avatar else None
            return JsonResponse({'status': 'success', 'message': 'User found', 'username': username, 'usernames': [user.username for user in users], 'users_id': users_id, 'avatar_url': avatar_url})
        else:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        
@login_required
def api_logout(request):
    """Logs out the user by blacklisting their JWT token and sending a guest token."""
    token = request.COOKIES.get('jwt_token')

    if token:
        # Blacklist the current JWT token
        JWTAuthenticationMiddleware.blacklist_token(token)

        # Generate a new guest token
        guest_token = generate_guest_token()

        # Create a response indicating logout success
        response = JsonResponse({'status': 'success', 'message': _('Logged out successfully')})

        # Set the new guest JWT token as a cookie in the response
        response.set_cookie('jwt_token', guest_token, httponly=True, secure=True, samesite='Lax')

        return response
    else:
        return JsonResponse({'error': 'No active session found.'}, status=400)
    
def api_login(request):
    logger.debug("api_login")

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = LogInForm(request, data=data)

            if form.is_valid():
                user = form.get_user()
                login(request, user)
                logger.debug(f"api_login > User.id: {user.id}")

                # Generate a JWT token for the authenticated user
                jwt_token = generate_jwt_token(user)  # Ensure this function is properly implemented
                logger.debug(f"token >>>>>>>>>>>: {jwt_token}")
				
                # Create response object
                response = JsonResponse({
                    'status': 'success',
                    'message': _('Login successful'),
                    'token': jwt_token,
                    'user_id': user.id
                })

                # Set the JWT token in the headers
                response['Authorization'] = f'Bearer {jwt_token}'

                # Set the JWT token in a cookie (with security options)
                response.set_cookie(
                    key='jwt_token',
                    value=jwt_token,
                    httponly=True,  # Prevent JavaScript access to the cookie (for security)
                    secure=True,  # Only send the cookie over HTTPS (ensure your environment supports this)
                    samesite='Lax',  # Control cross-site request behavior
                    max_age=60 * 60 * 24 * 7,  # Cookie expiration (optional, e.g., 7 days)
                )
                
                return response

            else:
                logger.debug('api_login > Invalid username or password')
                return JsonResponse({'status': 'error', 'message': _('Invalid username or password')}, status=401)

        except json.JSONDecodeError:
            logger.debug('api_login > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': _('Invalid JSON')}, status=400)

    logger.debug('api_login > Method not allowed')
    return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)

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
                      'message': _('User not found')
                  }, status=400)

              # Check if the user is active
              if not user_obj.is_active:
                  logger.debug('api_signup > User is inactive')
                  user.delete()
                  return JsonResponse({
                      'status': 'error', 
                      'message': _('User is inactive')
                  }, status=400)
              
              csrf_token = request.COOKIES.get('csrftoken')
              # Create a profile through call to profileapi service
              if not createProfile(username, user.id, csrf_token):
                    user.delete()
                    return JsonResponse({
                        'status': 'error', 
                        'message': _('Failed to create profile')
                    }, status=500)

              user = authenticate(username=username, password=password)
              if user is not None:
                  logger.debug('api_signup > Sign up successful')
                  login(request, user)
                  return JsonResponse({
                      'status': 'success',
                      'message': _('Sign up successful'),
                  })
              else:
                  user.delete()
                  logger.debug('api_signup > Authentication failed')
                  return JsonResponse({'status': 'error', 'message': _('Authentication failed')}, status=401)
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
            return JsonResponse({'status': 'error', 'message': _('Invalid JSON')}, status=400)
        except Exception as e:
            logger.error(f'api_signup > Unexpected error: {e}')
            return JsonResponse({
                'status': 'error', 
                'message': _('An unexpected error occurred')
            }, status=500)
    logger.debug('api_signup > Method not allowed')
    return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)

def api_check_exists(request):
    logger.debug("api_check_exists")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          username = data.get('username')
          if User.objects.filter(username=username).exists():
              logger.debug('api_check_exists > User exists')
              return JsonResponse({'status': 'success', 'message': _('User exists')})
          else:
              logger.debug('api_check_exists > User does not exist')
              return JsonResponse({'status': 'failure', 'message': _('User does not exist')}, status=404)
        except json.JSONDecodeError:
            logger.debug('api_check_exists > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': _('Invalid JSON')}, status=400)
    logger.debug('api_check_exists > Method not allowed')
    return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)


def api_edit_profile(request):
  logger.debug("api_edit_profile")
  if request.method == 'POST':
    try:
      data = json.loads(request.body)
      logger.debug(f'data: {data}')
      user_id = data.get('user_id')
      logger.debug(f'user_id: {user_id}')
      try :
        logger.debug(f'extract user_obj')
        try:
          user_obj = User.objects.get(id=user_id)
        except User.DoesNotExist:
          return JsonResponse({'status': 'error', 'message': _('User not found')}, status=404)
        #user_obj = User.objects.filter(id=user_id).first()
        logger.debug(f'user_obj username: {user_obj.username}')
        form = EditProfileForm(data, instance=user_obj)
        logger.debug(f'form: {form}')
      except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('User not found')}, status=404)
      if form.is_valid():
        logger.debug('api_edit_profile > Form is valid')
        form.save()
        return JsonResponse({'status': 'success', 'message': _('Profile updated'), 'status': 200})
      else:
        logger.debug('api_edit_profile > Form is invalid')
        return JsonResponse({'status': 'error', 'message': _('Invalid profile update')}, status=400)
    except json.JSONDecodeError:
      logger.debug('api_edit_profile > Invalid JSON')
      return JsonResponse({'status': 'error', 'message': _('Invalid JSON')}, status=400)
  else:
    logger.debug('api_edit_profile > Method not allowed')
    return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)