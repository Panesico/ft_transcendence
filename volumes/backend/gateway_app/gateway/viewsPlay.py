import os, json, requests, logging
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

#from web3 import Web3
# from .blockchain import connect_to_blockchain
# from .utils import getUserId, getUserData
from django.contrib.auth import get_user_model
from .viewsProfile import get_profileapi_variables
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)
User = get_user_model()

def get_tournament(request):
    logger.debug("")
    logger.debug("get_tournament")

    if request.method != 'GET':
      return redirect('405')
    
    # temp --> to test
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }

    response = requests.get('https://play:9003/api/connecttoblockchain/', headers=headers, verify=os.getenv("CERTFILE"))
    # --> end test
    
    if request.user.id != 0:
        user_profile = get_profileapi_variables(request)
        info = {
            'p1_label': request.user.username,
            'p1_value': user_profile['display_name'],
        }
    else:
        info = {
            'p1_label': _('Name Player') + ' 1',
            'p1_value': _('Name') + '1',
        }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_tournament XMLHttpRequest")
        html = render_to_string('fragments/tournament_form_fragment.html', {'info': info}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/tournament.html', {'info': info})

def get_play(request):
    logger.debug("")
    logger.debug("get_play")
    if request.method != 'GET': 
      return redirect('405')
    
    # jwt_token = request.COOKIES.get('jwt_token')
    # user_id = await getUserId(jwt_token)
    # user = await getUserData(user_id)
    # logger.debug(f"get_play > user['profile']: {user['profile']}")

    if request.user.id != 0:
        user_profile = get_profileapi_variables(request)
        info = {
            'p1_label': request.user.username,
            'p1_value': user_profile['display_name'],
        }
    else:
        info = {
            'p1_label': _('Name Player') + ' 1',
            'p1_value': _('Name') + '1',
        }
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_play XMLHttpRequest")
        html = render_to_string('fragments/play_fragment.html', {'info': info}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/play.html', {'info': info})
