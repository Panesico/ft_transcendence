# # views.py
from django.http import HttpResponse
import os
from django.conf import settings
import logging

# Configure logger
logger = logging.getLogger(__name__)

# # Serve the index.html and (some) static files
# def index(request):
    # logger.debug(request)

    # file_extension = os.path.splitext(request.path)[1]
    # file_path = os.path.join(settings.STATIC_ROOT, request.path[1:])
    # # logger.debug("file_extension: %s", file_extension)
    # # logger.debug("file_path: %s", file_path)

    # # Check if the request is for a static file and if not, serve index.html
    # if os.path.splitext(request.path)[1] != '.html' and os.path.isfile(file_path):
    #   logger.debug(f"Serving file: {file_path}")
    #   with open(file_path, 'rb') as f:
    #     if file_extension == '.js':
    #       return HttpResponse(f.read(), content_type='application/javascript')
    #     elif file_extension == '.css':
    #       return HttpResponse(f.read(), content_type='text/css')
    #     elif file_extension == '.svg':
    #       return HttpResponse(f.read(), content_type='image/svg+xml')
    #     elif file_extension == '.png':
    #       return HttpResponse(f.read(), content_type='image/png')
    #     elif file_extension == '.jpg' or file_extension == '.jpeg':
    #       return HttpResponse(f.read(), content_type='image/jpeg')
    #     elif file_extension == '.gif':
    #       return HttpResponse(f.read(), content_type='image/gif')
    #     else:
    #       return HttpResponse(f.read(), content_type='application/octet-stream')
    # else:
    #   logger.debug("Serving index.html")
    #   index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
    #   with open(index_path, 'r') as f:
    #     return HttpResponse(f.read(), content_type='text/html')

from django.shortcuts import render

def load_home(request):
    logger.debug("")
    logger.debug("load_home")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_home XMLHttpRequest")
        return render(request, 'fragments/home_fragment.html')
    return render(request, 'partials/home.html')

def load_game(request):
    logger.debug("")
    logger.debug("load_game")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_game XMLHttpRequest")
        return render(request, 'fragments/game_fragment.html')
    return render(request, 'partials/game.html')

def load_login(request):
    logger.debug("")
    logger.debug("load_login")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_login XMLHttpRequest")
        return render(request, 'fragments/login_fragment.html')
    return render(request, 'partials/login.html')

def load_signup(request):
    logger.debug("")
    logger.debug("load_signup")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_signup XMLHttpRequest")
        return render(request, 'fragments/signup_fragment.html')
    return render(request, 'partials/signup.html')

def load_tournament(request):
    logger.debug("")
    logger.debug("load_tournament")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_tournament XMLHttpRequest")
        return render(request, 'fragments/tournament_fragment.html')
    return render(request, 'partials/tournament.html')

def load_404(request):
    logger.debug("")
    logger.debug("load_404")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_404 XMLHttpRequest")
        return render(request, 'fragments/404_fragment.html')
    return render(request, 'partials/404.html')

def load_other(request):
    logger.debug("")
    logger.debug("load_other")
    
    file_extension = os.path.splitext(request.path)[1]
    file_path = os.path.join(settings.STATIC_ROOT, request.path[1:])

    logger.debug(request)
    logger.debug("file_extension: %s", file_extension)
    logger.debug("file_path: %s", file_path)

    # Check if the request is for a static file and if not, serve index.html
    if os.path.splitext(request.path)[1] != '.html' and os.path.isfile(file_path):
      logger.debug(f"Serving file: {file_path}")
      with open(file_path, 'rb') as f:
        if file_extension == '.js':
          return HttpResponse(f.read(), content_type='application/javascript')
        elif file_extension == '.css':
          return HttpResponse(f.read(), content_type='text/css')
        elif file_extension == '.svg':
          return HttpResponse(f.read(), content_type='image/svg+xml')
        elif file_extension == '.png':
          return HttpResponse(f.read(), content_type='image/png')
        elif file_extension == '.jpg' or file_extension == '.jpeg':
          return HttpResponse(f.read(), content_type='image/jpeg')
        elif file_extension == '.gif':
          return HttpResponse(f.read(), content_type='image/gif')
        else:
          return HttpResponse(f.read(), content_type='application/octet-stream')
    else:
      logger.debug("load_other Serving home.html")
      return render(request, 'partials/home.html')
