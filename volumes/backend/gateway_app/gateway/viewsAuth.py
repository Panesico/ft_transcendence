import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from .forms import SignUpFormFrontend, LogInFormFrontend
import json
import requests
import logging
logger = logging.getLogger(__name__)

# Logout

def get_logout(request):
    authentif_url = 'http://authentif:9001/api/logout/' 
    if request.method != 'GET':
        return redirect('405')
    response = requests.get(authentif_url, cookies=request.COOKIES)
    if response.ok:
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    else:
        html = render_to_string('fragments/home_fragment.html', context={}, request=request)
        return JsonResponse({'html': html, 'status': 'error', 'message': 'Logout failed'}, status=response.status_code)

# Login

def view_login(request):
    logger.debug('view_login')
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
    authentif_url = 'http://authentif:9001/api/login/'
    if request.method != 'POST':
      return redirect('405')
    
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json'
    }
    data = json.loads(request.body)

    # logger.debug(f'csrf_token: {csrf_token}')
    # logger.debug(f'Extracted headers: {headers}')
    # logger.debug(f'Extracted data from JSON: {data}')
    
    response = requests.post(authentif_url, json=data, headers=headers)
    # logger.debug(f"post_login > Response cookies: {response.cookies}")

    status = response.json().get("status")
    message = response.json().get("message")
    if response.ok:
        # if 'HTTP_X_REQUESTED_WITH' in request.META:
        #     logger.debug("Removing 'x-requested-with' header from request")
        #     request.META.pop('HTTP_X_REQUESTED_WITH', None)
        
        # for cookie in response.cookies:
        #     request.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True)
        
        # # user_response = render(request, 'partials/home.html', {'status': status, 'message': message})
        # # user_response = render(request, 'partials/home.html')

        # # user_response = redirect(f"{reverse('home')}?status={status}&message={message}")
        # # logger.debug(request.headers.get('x-requested-with'))

        # htmlMain = render_to_string('fragments/home_fragment.html', context={}, request=request)
        # htmlHeader = render_to_string('includes/header.html', context={}, request=request)
        # user_response =  JsonResponse({'htmlMain': htmlMain, 'htmlHeader': htmlHeader, 'status': status, 'message': message})
        
        # for cookie in response.cookies:
        #     user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True)
        # # logger.debug(f"post_login > authentif_cookies: {user_response.cookies}")
        # return user_response

        # Build the redirect response to the home page with status and message
        # user_response = redirect(f"{reverse('home')}?status={status}&message={message}")
        
        user_response =  JsonResponse({'status': status, 'message': message})
        # Set cookies from the external response if available
        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True)

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
    authentif_url = 'http://authentif:9001/api/signup/' 
    if request.method != 'POST':
      return redirect('405')

    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json'
    }
    data = json.loads(request.body)

    # logger.debug(f'csrf_token: {csrf_token}')
    # logger.debug(f'Extracted headers: {headers}')
    # logger.debug(f'Extracted data from JSON: {data}')
    
    response = requests.post(authentif_url, json=data, headers=headers)

    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"status: {status}, message: {message}")
    logger.debug(f"post_signup > Response: {response.json()}")
    if response.ok:
        logger.debug('post_signup > Response OK')
        user_response =  JsonResponse({'status': status, 'message': message})

        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True)

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
