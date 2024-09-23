import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from .forms import SignUpFormFrontend, LogInFormFrontend
import requests
import logging
logger = logging.getLogger(__name__)

def get_login(request):
    if request.method != 'GET':
      return redirect('405')    
    form = LogInFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/login.html', {'form': form})

def get_signup(request):
    if request.method != 'GET':
      return redirect('405')
    form = SignUpFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('fragments/signup_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/signup.html', {'form': form})

def get_logout(request):
    authentif_url = 'http://authentif:8001/api/logout/' 
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

def post_login(request):
    authentif_url = 'http://authentif:9000/api/login/' 
    if request.method != 'POST':
      return redirect('405')
    csrf_token = request.COOKIES.get('csrftoken')
    # logger.debug(request.POST)
    # logger.debug(f'csrf_token: {csrf_token}')
    # logger.debug("")
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
    }
    data = {
        'csrfmiddlewaretoken': request.POST.get('csrfmiddlewaretoken'),
        'username': request.POST.get('username'),
        'password': request.POST.get('password')
    }
    response = requests.post(authentif_url, data=data, headers=headers)
    if response.ok:
        return redirect('home', {'status': 'success', 'message': 'Login successful'})
    else:
        form = LogInFormFrontend()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
            return JsonResponse({'html': html, 'status': 'error', 'message': response.json().get('message')}, status=response.status_code)
        return render(request, 'partials/login.html', {'form': form, 'status': 'error', 'message': response.json().get('message')})

def post_signup(request):
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
