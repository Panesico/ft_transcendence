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
            return JsonResponse({
                  'status': 'success',
                  'message': 'User found',
                  'username': username,
                  'usernames': [user.username for user in users],
                  'users_id': users_id,
                  'avatar_url': avatar_url
                })
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
        response = JsonResponse({
              'status': 'success',
              'type': 'logout_successful',
              'message': _('Logged out successfully')
            })

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
                    'type': 'login_successful',
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
def createProfile(username, user_id, csrf_token, id_42):
    profileapi_url = 'https://profileapi:9002/api/signup/'
    if id_42:
        profile_data = { 'user_id': user_id, 'username': username, 'id_42': id_42 }
    else:
        profile_data = { 'user_id': user_id, 'username': username }
    
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'HTTP_HOST': 'profileapi',
        'Referer': 'https://authentif:9001',
    }

    cookies = {
    'csrftoken': f'{csrf_token}',
    }

    try:
        response = requests.post(profileapi_url, json=profile_data, headers=headers, cookies=cookies, verify=os.getenv("CERTFILE"))
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
              if not createProfile(username, user.id, csrf_token, False):
                    user.delete()
                    return JsonResponse({
                        'status': 'error', 
                        'message': _('Failed to create profile')
                    }, status=500)
              jwt_token = generate_jwt_token(user)  # Ensure this function is properly implemented
              logger.debug(f"token >>>>>>>>>>>: {jwt_token}")
      
              # Create response object
              response = JsonResponse({
                  'status': 'success',
                  'type': 'login_successful',
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

def api_check_username_exists(request):
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
        logger.debug(f'api_edit_profile > extract user_obj')
        user_obj = User.objects.get(id=user_id)
        #user_obj = User.objects.filter(id=user_id).first()
        logger.debug(f'user_obj username: {user_obj.username}')
        form = EditProfileForm(data, instance=user_obj)
        # logger.debug(f'form: {form}')
      except User.DoesNotExist:
        logger.debug('api_edit_profile > User not found')
        return JsonResponse({'status': 'error', 'message': _('User not found')}, status=404)
      if form.is_valid():
        logger.debug('api_edit_profile > Form is valid')
        form.save()
        return JsonResponse({
              'status': 'success',
              'type': 'profile_updated',
              'message': _('Profile updated'),
              'status': 200
            })
      else:
        logger.debug('api_edit_profile > Form is invalid')
        return JsonResponse({'status': 'error', 'message': _('Invalid profile update')}, status=400)
    except json.JSONDecodeError:
      logger.debug('api_edit_profile > Invalid JSON')
      return JsonResponse({'status': 'error', 'message': _('Invalid JSON')}, status=400)
  else:
    logger.debug('api_edit_profile > Method not allowed')
    return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)

import requests
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import login

import requests
from django.conf import settings

def exchange_code_for_token(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': settings.REDIRECT_URI,
    }
    response = requests.post('https://api.intra.42.fr/oauth/token', data=data)
    return response.json()

def get_42_user_data(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
    return response.json()

from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import SimpleUploadedFile

logger = logging.getLogger(__name__)

import requests
from django.utils.translation import gettext as _

def create_or_get_user(request, user_data):
    """
    Creates a new user or retrieves an existing one based on the 42 API data.
    Logs in the user after creation or retrieval, and calls the profile API to create the profile.
    """
    try:
        # Try to find the user by their 42 login (username)
        user = User.objects.get(username=user_data['login'])
        logger.info(f"User found: {user.username}")
    except User.DoesNotExist:
        # Check if this is a "42 user" by seeing if `id` exists in user_data (or any other identifier for 42 user)
        if 'id' in user_data:  # Assuming `id` from user_data corresponds to 42 ID
            data = {"username": user_data['login'], "id_42": user_data['id']}  # No password needed for 42 users

            # Bypass the password field if user is 42-based
            form = SignUpForm(data=data)
            if form.is_valid():
                user = form.save()
            else:
                logger.error(f"SignUpForm error: {form.errors}")
        else:
            # Create a standard user with a password if not a 42 user
            data = {"username": user_data['login'], "password": "1", "confirm_password": "1"}
            form = SignUpForm(data=data)
            if form.is_valid():
                user = form.save()
            else:
                logger.error(f"SignUpForm error: {form.errors}")
        
        # Create the profile
        createProfile(user_data['login'], user_data['id'], "", 'id' in user_data)  # True if 42 user
        payload = json.dumps({'image_url': user_data['image']['link']})  # Convert the data to a JSON string
        csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies
        jwt_token = request.COOKIES.get('jwt_token')

        headers = {
            'X-CSRFToken': csrf_token,
            'Cookie': f'csrftoken={csrf_token}',
            'Content-Type': 'application/json',
            'Referer': 'https://authentif:9001',
            'Authorization': f'Bearer {jwt_token}',
        }
        
        # Make the POST request to the external authentif service
        response = requests.post("https://gateway:8443/download_42_avatar/", data=payload, headers=headers, verify=os.getenv("CERTFILE"))
        csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies
        jwt_token = request.COOKIES.get('jwt_token')

        headers = {
            'X-CSRFToken': csrf_token,
            'Cookie': f'csrftoken={csrf_token}',
            'Content-Type': f"{response.json()['avatar']['content_type']}",
            'Referer': 'https://authentif:9001',
            'Authorization': f'Bearer {jwt_token}',
        }

        response = requests.post("https://gateway:8443/post_edit_profile_avatar", body=response.text, headers=headers, verify=os.getenv("CERTFILE"))
        
        

        
    if user == None:
        login(request, user)

    return user


@csrf_exempt
def oauth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    # Get the 'code' parameter from the parsed JSON data
    auth_code = data.get('code')
    state = data.get('state')
    
    if not auth_code:
        return JsonResponse({'error': 'Authorization code is missing'}, status=400)

    # Step 2: Exchange authorization code for access token
    try:
        token_data = exchange_code_for_token(auth_code)
    except Exception as e:
        logger.error(f"Error exchanging authorization code: {str(e)}")
        return JsonResponse({'error': 'Failed to retrieve access token'}, status=500)

    if 'access_token' not in token_data:
        return JsonResponse({'error': 'Failed to retrieve access token'}, status=400)

    # Step 3: Retrieve user data from 42 API
    try:
        user_data = get_42_user_data(token_data['access_token'])
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        return JsonResponse({'error': 'Failed to retrieve user data'}, status=500)

    # Step 4: Create or authenticate the user and generate a JWT
    try:
        # Try to find the user by their 42 login (username)
        user = User.objects.get(username=user_data['login'])
        logger.info(f"User found: {user.username}")
        jwt_token = generate_jwt_token(user)  # Ensure this function is properly implemented
        response = JsonResponse({
          'status': 'success',
          'type': 'login_successful',
          'message': _('Login successful'),
          'token': jwt_token,
          'user_id': user.id
        })
        response['Authorization'] = f'Bearer {jwt_token}'
        response.set_cookie(
        key='jwt_token',
        value=jwt_token,
        httponly=True,  # Prevent JavaScript access to the cookie (for security)
        secure=True,  # Only send the cookie over HTTPS (ensure your environment supports this)
        samesite='Lax',  # Control cross-site request behavior
        max_age=60 * 60 * 24 * 7,  # Cookie expiration (optional, e.g., 7 days)
        )
        return response
    except User.DoesNotExist:
        # Check if this is a "42 user" by seeing if `id` exists in user_data (or any other identifier for 42 user)
        if 'id' in user_data:  # Assuming `id` from user_data corresponds to 42 ID
            data = {"username": user_data['login'], "id_42": user_data['id']}  # No password needed for 42 users

            # Bypass the password field if user is 42-based
            form = SignUpForm(data=data)
            if form.is_valid():
                user = form.save()
            else:
                logger.error(f"SignUpForm error: {form.errors}")
        
    csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies

    # Create the profile
    createProfile(user_data['login'], user.id, csrf_token, 'id' in user_data)  # True if 42 user
    if user == None:
        login(request, user)

    jwt_token = generate_jwt_token(user)  # Ensure this function is properly implemented
    payload = json.dumps({'image_url': user_data['image']['link']})  # Convert the data to a JSON string
    

    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://authentif:9001',
        'Authorization': f'Bearer {jwt_token}',
    }
    
    # Make the POST request to the external authentif service
    response = requests.post("https://gateway:8443/download_42_avatar/",cookies=request.COOKIES,data=payload,headers=headers,verify=os.getenv("CERTFILE"))

    # If the response is a file (an image), we need to handle it differently.
    if response.status_code == 200:
        # Get the content type from the response
        content_type = response.headers['Content-Type']
        image_name = response.headers.get('Content-Disposition').split('filename=')[1].strip('"')

        # Prepare the multipart form data for editing the profile avatar
        files = {
            'avatar': (image_name, response.content, content_type)  # Sending the image as a file
        }

        csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies

        headers = {
            'X-CSRFToken': csrf_token,
            'Authorization': f'Bearer {jwt_token}',
            'Referer': 'https://authentif:9001',
        }

        # Send the image to edit_profile_avatar
        edit_response = requests.post(
            "https://gateway:8443/edit_profile_avatar/",
            cookies=request.COOKIES,
            files=files,  # Sending the files parameter for multipart
            headers=headers,
            verify=os.getenv("CERTFILE")
        )

        if edit_response.status_code == 200:
            print("Avatar updated successfully.")
        else:
            print(f"Failed to update avatar: {edit_response.content}")

    else:
        print(f"Failed to download avatar: {response.content}")

    
    headers = {
            'X-CSRFToken': csrf_token,
            'Cookie': f'csrftoken={csrf_token}',
            'Content-Type': 'application/json',
            'Referer': 'https://authentif:9001',
            'Authorization': f'Bearer {jwt_token}',
    }
    
    if user_data['languages_users'][0]['language_id'] == 11:
        language = 'es'
    elif user_data['languages_users'][0]['language_id'] == 1:
        language = 'fr'
    else:
        language = 'en'

    payload = json.dumps({
        "csrfmiddlewaretoken": f"{csrf_token}",
        "display_name": f"{user_data['login']}",
        "country": f"{user_data['campus'][0]['country']}",
        "city": f"{user_data['campus'][0]['city']}",
        "preferred_language": f"{language}"
    })

    response = requests.post("https://gateway:8443/edit_profile_general/",data=payload,headers=headers,verify=os.getenv("CERTFILE"))

    # Create response object
    response = JsonResponse({
        'status': 'success',
        'type': 'login_successful',
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
    response.set_cookie('django_language', language, samesite='Lax', httponly=True, secure=True)
    
    return response
