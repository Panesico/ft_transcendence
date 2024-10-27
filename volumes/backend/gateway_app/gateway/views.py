import os, requests, logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
# from django.template.response import TemplateResponse
logger = logging.getLogger(__name__)

def get_home(request):
    logger.debug("")
    logger.debug(f"get_home > request: {request}")
    status = request.GET.get('status', '')
    message = request.GET.get('message', '')
    logger.debug(f"get_home > Request Cookies: {request.COOKIES}")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('fragments/home_fragment.html', context={}, request=request)
        return JsonResponse({'html': html, 'status': status, 'message': message})
    return render(request, 'partials/home.html', {'status': status, 'message': message})

def get_friends(request):
  logger.debug("")
  logger.debug(f"get_friends > request: {request}")
  if not request.user.is_authenticated:
    return redirect('login')
  if request.method != 'GET':
    return redirect('405')

  # Get friends
  profile_api_url = 'https://profileapi:9002/api/getfriends/' + str(request.user.id) + '/'
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
  friends = response.json()
  logger.debug(f"get_friends > friends: {friends}")
  if response.status_code == 200:
    return JsonResponse({'friends': friends}, status=200)


def list_friends(request):
    logger.debug("")
    logger.debug(f"list_friends > request: {request}")
    if not request.user.is_authenticated:
      return redirect('login')
    if request.method != 'GET':
      return redirect('405')

    # Get friends
    profile_api_url = 'https://profileapi:9002/api/getfriends/' + str(request.user.id) + '/'
    response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
    friends = response.json()
    logger.debug(f"list_friends > friends: {friends}")
    if response.status_code == 200:
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
