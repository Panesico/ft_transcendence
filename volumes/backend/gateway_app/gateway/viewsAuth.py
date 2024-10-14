import os, json, requests, logging
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .forms import SignUpFormFrontend, LogInFormFrontend
from .viewsProfile import get_profileapi_variables
import jwt
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
        
        # Create a Django HttpResponse from the requests response
        django_response = HttpResponse(
            response.content,  # Content from the external request
            status=response.status_code  # Status code from the external request
        )
        
        # Set any headers from the external response if needed
        for key, value in response.headers.items():
            django_response[key] = value
        
        return django_response

    except requests.exceptions.RequestException as e:
        # If the external request fails, handle the error gracefully
        return HttpResponse(f"Failed to log out: {e}", status=500)

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
        html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/login.html', {'form': form})
   
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
    if response.ok:
        logger.debug('post_signup > Response OK')
        user_response =  JsonResponse({'status': status, 'message': message})

        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True, secure=True)

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
