import os, json, requests, logging
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .forms import SignUpFormFrontend, LogInFormFrontend
logger = logging.getLogger(__name__)

# Logout

@login_required
def get_logout(request):
    authentif_url = 'https://authentif:9001/api/logout/' 
    if request.method != 'GET':
        return redirect('405')
    response = requests.get(authentif_url, cookies=request.COOKIES, verify=os.getenv("CERTFILE"))
    if response.ok:
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    else:
        html = render_to_string('fragments/home_fragment.html', context={}, request=request)
        return JsonResponse({'html': html, 'status': 'error', 'message': 'Logout failed'}, status=response.status_code)

# Login

def view_login(request):
    logger.debug('view_login')
    if request.user.is_authenticated:
      return redirect('home')
    if request.method == 'GET': 
       return get_login(request)      
    elif request.method == 'POST':
       return post_login(request)
    else:
      return redirect('405')

def get_login(request):
    logger.debug('get_login')
    form = LogInFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/login.html', {'form': form})
   
def post_login(request):
    logger.debug('post_login')
    authentif_url = 'https://authentif:9001/api/login/'
    if request.method != 'POST':
      return redirect('405')
    
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }
    data = json.loads(request.body)

    # logger.debug(f'csrf_token: {csrf_token}')
    # logger.debug(f'Extracted headers: {headers}')
    # logger.debug(f'Extracted data from JSON: {data}')
    
    response = requests.post(authentif_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    # logger.debug(f"post_login > Response cookies: {response.cookies}")

    status = response.json().get("status")
    message = response.json().get("message")
    if response.ok:        
        user_response =  JsonResponse({'status': status, 'message': message})
        # Set cookies from the external response if available
        
        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True, secure=True)
        return user_response
    else:
        logger.debug(f"post_login > Response NOT OK: {response.json()}")
        logger.debug(message)
        data = json.loads(request.body)
        form = LogInFormFrontend(data)
        form.add_error(None, message)
        html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html, 'status': status, 'message': message})

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

    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
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
