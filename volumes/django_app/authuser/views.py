# # views.py
import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from authuser.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from authuser.forms import SignUpForm, LogInForm
import logging
logger = logging.getLogger(__name__)


def load_home(request):
    logger.debug("")
    logger.debug("load_home")
    logger.debug(request)
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

def load_logout(request):
    logger.debug("")
    logger.debug("load_logout")

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_logout XMLHttpRequest")
        return render(request, 'fragments/home_fragment.html')
    return redirect('home')

def load_login(request):
    logger.debug("")
    logger.debug("load_login")
    if request.method == 'POST':
        logger.debug("load_login > POST")
        form = LogInForm(request, data=request.POST)
        logger.debug(form)
        if form.is_valid():
            logger.debug("load_login > POST > form.is_valid")
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            logger.debug("load_login > POST > form NOT valid")
            messages.error(request, 'Invalid username or password.')
    else:
        form = LogInForm()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_login returning fragment")
        return render(request, 'fragments/login_fragment.html', {'form': form})
    logger.debug("load_login returning")
    logger.debug("form.errors:")
    logger.debug(form.errors) 
    return render(request, 'partials/login.html', {'form': form})

def load_signup(request):
    logger.debug("")
    logger.debug("load_signup")
    logger.debug(request)
    if request.method == 'POST':
        logger.debug("POST load_signup")
        logger.debug(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            logger.debug("POST load_signup form.is_valid")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Log the user in automatically after signup
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Sign up successful!')
                return redirect('home')
        else:
            logger.debug("POST load_signup NOT form.is_valid")
            logger.debug("form.errors:")
            logger.debug(form.errors) 
            messages.error(request, 'Please correct the error below.')
    else:
        logger.debug("not POST load_signup")
        form = SignUpForm()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("load_signup returning fragment")
        return render(request, 'fragments/signup_fragment.html', {'form': form})
    logger.debug("load_signup returning")
    logger.debug("form.errors:")
    logger.debug(form.errors) 
    return render(request, 'partials/signup.html', {'form': form})

def load_profile(request):
		logger.debug("")
		logger.debug("load_profile called")
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				logger.debug("load_profile XMLHttpRequest")
				return render(request, 'fragments/profile_fragment.html')
		return render(request, 'partials/profile.html')

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
        elif file_extension == '.ttf':
          return HttpResponse(f.read(), content_type='font/ttf')
        else:
          return HttpResponse(f.read(), content_type='application/octet-stream')
    else:
      logger.debug("load_other Serving home.html")
      return render(request, 'partials/home.html')


# def load_files(request):
#     logger.debug("")
#     logger.debug("load_files")
#     logger.debug(request)
    
#     # file_extension = os.path.splitext(request.path)[1]

#     # logger.debug("file_extension: %s", file_extension)
#     # logger.debug("file_path: %s", file_path)

#     if request.method == 'GET':
#         file_name = request.GET.get('fileName', None)
        
#         if file_name:
#           logger.debug("file_name: %s", file_name)
#           file_path = os.path.join(settings.STATIC_ROOT, file_name)
#           logger.debug("file_path: %s", file_path)
#           logger.debug(os.path.isfile(file_path))

#     # Check if the request is for a static file and if not, serve index.html
#     # if os.path.splitext(request.path)[1] != '.html' and os.path.isfile(file_path):
#           if os.path.isfile(file_path):
#             file_extension = os.path.splitext(file_path)[1]
#             logger.debug(f"Serving file: {file_path}")
#             with open(file_path, 'rb') as f:
#               if file_extension == '.js':
#                 return FileResponse(f.read(), content_type='application/javascript')
#               elif file_extension == '.css':
#                 return FileResponse(f.read(), content_type='text/css')
#               elif file_extension == '.svg':
#                 return FileResponse(f.read(), content_type='image/svg+xml')
#               elif file_extension == '.png':
#                 return FileResponse(f.read(), content_type='image/png')
#               elif file_extension == '.jpg' or file_extension == '.jpeg':
#                 return FileResponse(f.read(), content_type='image/jpeg')
#               elif file_extension == '.gif':
#                 return FileResponse(f.read(), content_type='image/gif')
#               elif file_extension == '.ttf':
#                 return FileResponse(f.read(), content_type='font/ttf')
#               else:
#                 return FileResponse(f.read(), content_type='application/octet-stream')
              
#     logger.debug("load_files Serving home.html")
#     return render(request, 'partials/404.html', status=404)
