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


def get_logout(request):
    authentif_url = 'http://authentif:9000/api/logout/' 
    if request.method != 'GET':
      return redirect('405')
    response = requests.get(authentif_url, cookies=request.COOKIES)
    if response.ok:
      if request.headers.get('x-requested-with') == 'XMLHttpRequest':
          html = render_to_string('fragments/home_fragment.html', context={}, request=request)
          return JsonResponse({'html': html, 'status': 'success', 'message': 'Logged out successfully'})
      return redirect('home', {'status': 'success', 'message': 'Logged out successfully'})
    else:
        # Add html?
        return JsonResponse({'status': 'error', 'message': 'Logout failed'}, status=response.status_code)

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
    authentif_url = 'http://authentif:9000/api/login/'
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
        html = render_to_string('fragments/home_fragment.html', context={}, request=request)

        user_response =  JsonResponse({'html': html, 'status': status, 'message': message})
        
        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True)
        # logger.debug(f"post_login > authentif_cookies: {user_response.cookies}")
        return user_response
    else:
        form = LogInFormFrontend()
        html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html, 'status': status, 'message': message})


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
    authentif_url = 'http://authentif:9000/api/signup/' 
    if request.method != 'POST':
      return redirect('405')    
    response = requests.post(authentif_url, data=request.POST)        
    if response.ok:
        return redirect('home', {'status': 'success', 'message': 'Login successful'})
    else:
        form = SignUpFormFrontend()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('fragments/signup_fragment.html', {'form': form}, request=request)
            return JsonResponse({'html': html, 'status': 'error', 'message': response.json().get('message')}, status=response.status_code)
        return render(request, 'partials/signup.html', {'form': form, 'status': 'error', 'message': response.json().get('message')})
