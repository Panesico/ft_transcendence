import os, json, requests, logging
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .forms import SignUpFormFrontend, LogInFormFrontend
from .viewsProfile import get_profileapi_variables
import jwt
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.contrib.auth import get_user_model
logger = logging.getLogger(__name__)

# Logout

@login_required
def get_logout(request):
    authentif_url = 'https://authentif:9001/api/logout/' 
    
    # Only allow GET requests
    if request.method != 'GET':
        return redirect('405')  # Redirect to a 405 page for incorrect methods

    try:
        # Make the external request to the authentif service
        response = requests.get(authentif_url, cookies=request.COOKIES, verify=os.getenv("CERTFILE"))
        
        json_response = JsonResponse({'status': 'success', 'message': _('Logged out successfully')})

        # Set cookies from the response into the JsonResponse
        for cookie_name, cookie_value in response.cookies.items():
            json_response.set_cookie(cookie_name, cookie_value)
        
        # Set headers from response
        for header_name, header_value in response.headers.items():
            # Avoid overwriting 'Content-Type' or 'Content-Length' as they are set by JsonResponse
            if header_name.lower() not in ['content-type', 'content-length']:
                json_response[header_name] = header_value
        
        # Return the response
        return json_response
        
    except requests.exceptions.RequestException as e:
        # If the external request fails, handle the error gracefully
        return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)

# Login
def view_login(request):
    logger.debug('view_login')
    if request.user.is_authenticated:
      return redirect('home')
    if request.method == 'GET': 
       return get_login(request)      
    elif request.method == 'POST':
       return post_login(request=request)
    else:
      return redirect('405')

def get_login(request):
    logger.debug('get_login')
    form = LogInFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('fragments/login_fragment.html', {'form': form, 'CLIENT_ID': settings.CLIENT_ID, 'REDIRECT_URI': settings.REDIRECT_URI}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/login.html', {'form': form, 'CLIENT_ID': settings.CLIENT_ID, 'REDIRECT_URI': settings.REDIRECT_URI})
   
User = get_user_model()

def post_login(request):
    logger.debug('post_login')
    authentif_url = 'https://authentif:9001/api/login/'
    
    if request.method != 'POST':
        return redirect('405')

    csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies
    jwt_token = request.COOKIES.get('jwt_token')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
        'Authorization': f'Bearer {jwt_token}',
    }
    # Get the request data (credentials)
    data = json.loads(request.body)

    # Forward the request to the auth service
    try:
        response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    except requests.exceptions.RequestException as e:
        logger.error(f"post_login > Error calling auth service: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Authentication service unavailable'}, status=503)

    # Handle the response from the auth service
    if response.ok:
        # Extract token and message from the auth service
        response_data = response.json()
        jwt_token = response_data.get("token")
        user_id = response_data.get("user_id")
        message = response_data.get("message")

        if jwt_token:
            user_response = JsonResponse({'status': 'success', 'message': message, 'user_id': user_id})
            profile_data = get_profileapi_variables(request=request)
            logger.debug(f"post_login > profile_data: {profile_data}")
            preferred_language = profile_data.get('preferred_language')
            logger.debug(f"post_login > preferred_language: {preferred_language}")
            # Set the preferred language of the user, HTTP-only cookie
            user_response.set_cookie('django_language', preferred_language, domain='localhost', httponly=True, secure=True)
            # Set the JWT token in a secure, HTTP-only cookie
            user_response.set_cookie('jwt_token', jwt_token, httponly=True, secure=True, samesite='Lax')
            return user_response
        else:
            logger.error("post_login > No JWT token returned from auth service")
            return JsonResponse({'status': 'error', 'message': 'Failed to retrieve token'}, status=500)
    
    else:
        response_data = response.json()
        message = response_data.get("message", "Login failed")
        return JsonResponse({'status': 'error', 'message': message}, status=response.status_code)

# Signup

def view_signup(request):
    logger.debug('view_login')
    if request.user.is_authenticated:
      return redirect('home')
    if request.method == 'GET': 
       return get_signup(request)      
    elif request.method == 'POST':
       return post_signup(request)
    else:
      return redirect('405')

def get_signup(request):
    logger.debug('get_signup')
    if request.method != 'GET':
      return redirect('405')
    form = SignUpFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('fragments/signup_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/signup.html', {'form': form})

def post_signup(request):
    logger.debug('post_signup')
    authentif_url = 'https://authentif:9001/api/signup/' 
    if request.method != 'POST':
      return redirect('405')

    csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies
    jwt_token = request.COOKIES.get('jwt_token')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
        'Authorization': f'Bearer {jwt_token}',
    }
    data = json.loads(request.body)

    # logger.debug(f'csrf_token: {csrf_token}')
    # logger.debug(f'Extracted headers: {headers}')
    # logger.debug(f'Extracted data from JSON: {data}')
    
    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))

    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_signup > Response: {response.json()}")
    response_data = response.json()
    jwt_token = response_data.get("token")
    user_id = response_data.get("user_id")
    message = response_data.get("message")

    if jwt_token:
        user_response = JsonResponse({'status': 'success', 'message': message, 'user_id': user_id})
        # Set the JWT token in a secure, HTTP-only cookie
        user_response.set_cookie('jwt_token', jwt_token, httponly=True, secure=True, samesite='Lax')
        return user_response
    else:
        # logger.debug('post_signup > Response NOT OK')
        data = json.loads(request.body)
        form = SignUpFormFrontend(data)
        # existing_errors = form.non_field_errors.as_text()
        # logger.debug(f"existing_errors: {existing_errors}")
        form.add_error(None, message)
        # form._non_field_errors = form._create_errors(message)
        # existing_errors = form.non_field_errors.as_text()
        # logger.debug(f"existing_errors: {existing_errors}")
        html = render_to_string('fragments/signup_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html, 'status': status, 'message': message}, status=response.status_code)

import requests
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect

import json
import os
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

import json
import os
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

import json
import os
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def oauth(request):
    authentif_url = 'https://authentif:9001/api/oauth/'  # External auth service endpoint
    
    # Only allow POST requests
    if request.method != 'POST':
        return redirect('405')  # Redirect to a 405 page for incorrect methods

    # Parse JSON data from the request body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON data", status=400)

    # Get the 'code' and 'state' parameters from the parsed JSON data
    auth_code = data.get('code')

    # TODO - compare the states for preventing cross-site attacks
    state = data.get('state')
    if not auth_code:
        return HttpResponse("Authorization code is missing", status=400)

    try:
        # Set up the JSON data to send in the POST request to the external service
        payload = json.dumps({'code': auth_code})  # Convert the data to a JSON string
        csrf_token = request.COOKIES.get('csrftoken')  # Get CSRF token from cookies
        jwt_token = request.COOKIES.get('jwt_token')

        headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
        'Authorization': f'Bearer {jwt_token}',
        }
        # Make the POST request to the external authentif service
        response = requests.post(authentif_url, cookies=request.COOKIES,data=payload, headers=headers, verify=os.getenv("CERTFILE"))
        
        response_data = response.json() if response.status_code == 200 else {}
        
        # Create a base JsonResponse with status and message
        json_response_data = {
            'status': 'success',
            'message': response_data.get("message", "No message provided")
        }

        # Merge response_data into the JsonResponse data
        json_response_data.update(response_data)

        # Create JsonResponse
        json_response = JsonResponse(json_response_data)

        # Set cookies from the response into the JsonResponse
        for cookie_name, cookie_value in response.cookies.items():
            json_response.set_cookie(cookie_name, cookie_value)
        
        # Set headers from response
        for header_name, header_value in response.headers.items():
            # Avoid overwriting 'Content-Type' or 'Content-Length' as they are set by JsonResponse
            if header_name.lower() not in ['content-type', 'content-length']:
                json_response[header_name] = header_value
        
        if response.cookies.get('django_language') == None:
            profile_data = get_profileapi_variables(request=request)
            logger.debug(f"post_login > profile_data: {profile_data}")
            preferred_language = profile_data.get('preferred_language')
            json_response.set_cookie('django_language', preferred_language, samesite='Lax', httponly=True, secure=True)
        return json_response

    except requests.exceptions.RequestException as e:
        # Handle external request failure gracefully
        return JsonResponse({'status': 'error', 'message': _('Failed to login with 42')})


def oauth_callback(request):
    """
    Renders the OAuth callback page where the popup window will extract the 'code'
    and 'state' from the URL, then send it back to the parent window using postMessage.
    """
    return render(request, 'fragments/oauth_callback.html')
