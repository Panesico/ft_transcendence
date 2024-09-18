# views.py
from django.http import HttpResponse
import os
from django.conf import settings

def index(request):
    # Serve the built SPA's index.html
    index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
    with open(index_path, 'r') as f:
        return HttpResponse(f.read(), content_type='text/html')
