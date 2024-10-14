import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .forms import InviteFriendFormFrontend
from django.contrib import messages
import json
import logging
import requests
logger = logging.getLogger(__name__)
# May deelete this import
from django.template.response import TemplateResponse

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
      return render(request, 'partials/myfriends.html', {'error': 'Error retrieving friends'})


	# if request.method == 'GET':
	# 	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
	# 		logger.debug("list_friends > GET")
	# 		html = render_to_string('fragments/myfriends_fragment.html', {'my_variable': my_variable}, request=request)
	# 		return JsonResponse({'html': html})
	# 	return render(request, 'partials/myfriends.html', {'my_variable': my_variable})
	# else:
	# 	logger.debug("post_login > not POST returning 405")
	# 	html = render_to_string('fragments/405_fragment.html', {'my_variable': my_variable}, request=request)
	# 	return JsonResponse({'html': html}, status=405)


    #Handle form error



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
