# views.py
from django.http import HttpResponse
import os
from django.conf import settings
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Serve the index.html and (some) static files
def index(request):
    # logger.debug(request)

    file_extension = os.path.splitext(request.path)[1]
    file_path = os.path.join(settings.STATIC_ROOT, request.path[1:])
    # logger.debug("file_extension: %s", file_extension)
    # logger.debug("file_path: %s", file_path)

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
      logger.debug("Serving index.html")
      index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
      with open(index_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/html')
