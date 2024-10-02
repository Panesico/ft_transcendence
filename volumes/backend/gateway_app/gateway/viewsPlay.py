import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from .forms import TournamentFormFrontend
import json
import requests
import logging
logger = logging.getLogger(__name__)


def view_tournament(request):
    logger.debug('view_tournament')
    if request.method == 'GET': 
       return get_tournament(request)      
    elif request.method == 'POST':
       return post_tournament(request)
    else:
      return redirect('405')

def get_tournament(request):
    logger.debug("")
    logger.debug("get_tournament")
    if request.user.is_authenticated:
        form = TournamentFormFrontend(initial={'player1': request.user.username}) ### use displayName
        form.fields['player1'].label = request.user.username
    else:
        form = TournamentFormFrontend()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_tournament XMLHttpRequest")
        html = render_to_string('fragments/tournament_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/tournament.html', {'form': form})

def post_tournament(request):
    logger.debug('post_tournament')
    play_url = 'https://play:9003/api/newTournament/'
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
    if request.user.is_authenticated:
        data['player1_id'] = request.user.id
    logger.debug(f'post_tournament > extracted data from JSON: {data}')

    form = TournamentFormFrontend(data)
    if not form.is_valid():
        logger.debug(f"post_tournament > Form is NOT valid: {form.errors}")
        html = render_to_string('fragments/tournament_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html, 'status': 'error', 'message': 'Form is not valid'})
    
    # logger.debug(f'csrf_token: {csrf_token}')
    # logger.debug(f'Extracted headers: {headers}')
    
    response = requests.post(play_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    # logger.debug(f"post_tournament > Response cookies: {response.cookies}")

    status = response.json().get("status")
    message = response.json().get("message")
    if response.ok:        
        user_response =  JsonResponse({'status': status, 'message': message})
        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True, secure=True)
        return user_response
    else:
        logger.debug(f"post_tournament > Response NOT OK: {response.json()}")
        logger.debug(message)
        data = json.loads(request.body)
        form = TournamentFormFrontend(data)
        form.add_error(None, message)
        html = render_to_string('fragments/tournament_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html, 'status': status, 'message': message})


# def view_game(request):
#     logger.debug('view_game')
#     if request.method == 'GET': 
#        return get_game(request)      
#     elif request.method == 'POST':
#        return post_game(request)
#     else:
#       return redirect('405')
    
def get_game(request):
    logger.debug("")
    logger.debug("get_game")
    if request.method != 'GET': 
      return redirect('405')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_game XMLHttpRequest")
        html = render_to_string('fragments/game_fragment.html', context={}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/game.html')

def save_game(request):
    if request.method != 'POST': 
      return redirect('405')
    logger.debug('save_game')
    play_url = 'https://play:9003/api/saveGame/'
    
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
    
    response = requests.post(play_url, json=data, headers=headers, verify=os.getenv("CERTFILE"))
    # logger.debug(f"save_game > Response cookies: {response.cookies}")

    status = response.json().get("status")
    message = response.json().get("message")
    logger.debug(f"save_game > Response message: {message}")
    if response.ok:        
        user_response =  JsonResponse({'status': status, 'message': message})
        for cookie in response.cookies:
            user_response.set_cookie(cookie.name, cookie.value, domain='localhost', httponly=True, secure=True)
        return user_response
    else:
        logger.debug(f"save_game > Response NOT OK: {response.json()}")
        logger.debug(message)
        data = json.loads(request.body)
        form = TournamentFormFrontend(data)
        form.add_error(None, message)
        html = render_to_string('fragments/game_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html, 'status': status, 'message': message})