# views.py
import os
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
# from django.contrib.auth.models import User
from authuser.models import User
from django.contrib import messages
from authuser.forms import SignUpForm, LogInForm
from django.middleware.csrf import get_token
import logging
logger = logging.getLogger(__name__)


def get_home(request):
    logger.debug("")
    logger.debug("get_home")
    logger.debug(request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_home XMLHttpRequest")
        html = render_to_string('fragments/home_fragment.html', context={}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/home.html')

def get_game(request):
    logger.debug("")
    logger.debug("get_game")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_game XMLHttpRequest")
        html = render_to_string('fragments/game_fragment.html', context={}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/game.html')

def get_login(request):
    logger.debug("")
    logger.debug("get_login")
    if request.method != 'GET':
        logger.debug("get_login > != 'GET'")
        return render(request, 'partials/405.html', status=405)
    
    form = LogInForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_login returning fragment")
        html = render_to_string('fragments/login_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    logger.debug("get_login returning")
    logger.debug("form.errors:")
    logger.debug(form.errors) 
    return render(request, 'partials/login.html', {'form': form})

def get_signup(request):
    logger.debug("")
    logger.debug("get_signup")
    logger.debug(request)
    if request.method != 'GET':
        logger.debug("get_signup > != 'GET'")
        return render(request, 'partials/405.html', status=405)

    form = SignUpForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_signup returning fragment")
        html = render_to_string('fragments/signup_fragment.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    logger.debug("get_signup returning")
    logger.debug("form.errors:")
    logger.debug(form.errors) 
    return render(request, 'partials/signup.html', {'form': form})

def get_profile(request):
    logger.debug("")
    logger.debug("get_profile")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_profile XMLHttpRequest")
        html = render_to_string('fragments/profile_fragment.html', context={}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/profile.html')

def get_tournament(request):
    logger.debug("")
    logger.debug("get_tournament")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_tournament XMLHttpRequest")
        html = render_to_string('fragments/tournament_fragment.html', context={}, request=request)
        return JsonResponse({'html': html})
    return render(request, 'partials/tournament.html')

def get_404(request):
    logger.debug("")
    logger.debug("get_404")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_404 XMLHttpRequest")
        html = render_to_string('fragments/404_fragment.html', context={}, request=request)
        return JsonResponse({'html': html}, status=404)
    return render(request, 'partials/404.html', status=404)

def post_invite(request):
	logger.debug("")
	logger.debug("post_invite")
	if request.method == 'POST':
		logger.debug("post_invite > POST")
		return render(request, 'partials/profile.html')
	else:
		logger.debug("post_login > not POST returning 405")
		html = render_to_string('fragments/405_fragment.html', context={}, request=request)
		return JsonResponse({'html': html}, status=405)
		# form = InviteForm(request, data=request.POST)
		# logger.debug(form)
		# if form.is_valid():
		# 	logger.debug("post_invite > POST > form.is_valid")
		# 	invite = form.save(commit=False)
		# 	invite.inviter = request.user
		# 	invite.save()
		# 	messages.success(request, 'Invite sent successfully!')
		# 	return redirect('home')
		# else:
		# 	logger.debug("post_invite > POST > form NOT valid")
		# 	logger.debug("form.errors:")
		# 	logger.debug(form.errors) 
		# 	messages.error(request, 'Please correct the error below.')


# def get_other(request):
#     logger.debug("")
#     logger.debug("get_other")
    
#     file_extension = os.path.splitext(request.path)[1]
#     file_path = os.path.join(settings.STATIC_ROOT, request.path[1:])

#     logger.debug(request)
#     logger.debug("file_extension: %s", file_extension)
#     logger.debug("file_path: %s", file_path)

#     # Check if the request is for a static file and if not, serve index.html
#     if os.path.splitext(request.path)[1] != '.html' and os.path.isfile(file_path):
#       logger.debug(f"Serving file: {file_path}")
#       with open(file_path, 'rb') as f:
#         if file_extension == '.js':
#           return HttpResponse(f.read(), content_type='application/javascript')
#         elif file_extension == '.css':
#           return HttpResponse(f.read(), content_type='text/css')
#         elif file_extension == '.svg':
#           return HttpResponse(f.read(), content_type='image/svg+xml')
#         elif file_extension == '.png':
#           return HttpResponse(f.read(), content_type='image/png')
#         elif file_extension == '.jpg' or file_extension == '.jpeg':
#           return HttpResponse(f.read(), content_type='image/jpeg')
#         elif file_extension == '.gif':
#           return HttpResponse(f.read(), content_type='image/gif')
#         elif file_extension == '.ttf':
#           return HttpResponse(f.read(), content_type='font/ttf')
#         else:
#           return HttpResponse(f.read(), content_type='application/octet-stream')
#     else:
#       logger.debug("get_other Serving home.html")
#       return render(request, 'partials/home.html')


# def get_files(request):
#     logger.debug("")
#     logger.debug("get_files")
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
              
#     logger.debug("get_files Serving home.html")
#     return render(request, 'partials/404.html', status=404)
