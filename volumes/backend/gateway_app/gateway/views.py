import os, json, requests, logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import activate, gettext as _
from .consumerMainRoom import users_connected
from .authmiddleware import login_required
# from django.template.response import TemplateResponse
logger = logging.getLogger(__name__)

def get_home(request):
    if request.user.is_authenticated:
        logger.debug(f"IN GET HOME > USERNAME: {request.user.username}")
    logger.debug(f"get_home > request: {request}")
    status = request.GET.get('status', '')
    message = request.GET.get('message', '')
    type_msg = request.GET.get('type', '')
    logger.debug(f"get_home > Request Cookies: {request.COOKIES}")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        context = {'user': request.user}

        if type_msg == 'header':
            html = render_to_string('includes/header.html', context=context, request=request)
        elif type_msg == 'chat':
            html = render_to_string('includes/chat_modal.html', context=context, request=request)
        else:
            html = render_to_string('fragments/home_fragment.html', context=context, request=request)
            
        return JsonResponse({'html': html, 'status': status, 'message': message, 'user_id': request.user.id}, status=200)
    return render(request, 'partials/home.html', {'status': status, 'message': message})

@login_required
def get_friends(request):
  logger.debug("")
  logger.debug(f"get_friends > request: {request}")
  if request.method != 'GET':
    return redirect('405')

  # Get friends
  profile_api_url = 'https://profileapi:9002/api/getfriends/' + str(request.user.id) + '/'
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
  friends = response.json()
  logger.debug(f"get_friends > friends: {friends}")
  if response.status_code == 200:
    logger.debug(f"get_friends > users_connected: {users_connected}")
    # Add 'online': true to friends who are in users_connected
    for friend in friends:
      if friend['user_id'] in users_connected:
        friend['online'] = True
    return JsonResponse({'friends': friends}, status=200)


@login_required
def list_friends(request):
    logger.debug("")
    logger.debug(f"list_friends > request: {request}")
    if request.method != 'GET':
      return redirect('405')

    # Get friends
    profile_api_url = 'https://profileapi:9002/api/getfriends/' + str(request.user.id) + '/'
    response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
    friends = response.json()

    request_user_profile = requests.get('https://profileapi:9002/api/profile/' + str(request.user.id) + '/', verify=os.getenv("CERTFILE"))
    response_user_profile = request_user_profile.json()

    logger.debug(f"list_friends > friends: {friends}")
    if response.status_code == 200 and request_user_profile.status_code == 200:
      logger.debug(f"list_friends > users_connected: {users_connected}")
      # Add 'online': true to friends who are in users_connected
      for friend in friends:
        if not friend['im_blocked'] and friend['user_id'] in users_connected:
          friend['online'] = True

      blocked_users = response_user_profile['blocked_users']
      logger.debug(f"list_friends > blocked_users: {blocked_users}")
      
      if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # if friends is empty
        if not friends or len(friends) == 0:
          html = render_to_string('fragments/myfriends_fragment.html', request=request)
          return JsonResponse({'html': html, 'status': 200})
        else:
          html = render_to_string('fragments/myfriends_fragment.html', {'friends': friends}, request=request)
          return JsonResponse({'html': html, 'status': 200})
      return render(request, 'partials/myfriends.html', {'friends': friends})
    
    else:
      if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Error retrieving friends'}, status=500)
      return render(request, 'partials/myfriends.html', {'error': _('Error retrieving friends')})

def set_language(request):
    logger.debug("set_language")
    if request.method != 'POST':
        return redirect('405')
    
    try:
      data = json.loads(request.body)
    except json.JSONDecodeError:
      return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    
    # logger.debug(f"set_language > data: {data}")
    language = data.get('language')
    activate(language)
    logger.debug(f"set_language > new language: {language}")
    response = JsonResponse({'language': language}, status=200)
    response.set_cookie('django_language', language, httponly=False, secure=True, samesite='Lax')
    return response