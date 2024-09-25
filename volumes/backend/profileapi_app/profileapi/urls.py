from django.http import HttpResponse
from django.urls import path
import logging
logger = logging.getLogger(__name__)

def api_signup(request):
    logger.debug("hello from api_signup")
    return HttpResponse('api_signup', status=201)

urlpatterns = [
    path('api/signup/', api_signup, name='api_signup'),
]
