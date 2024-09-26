from django.http import HttpResponse
from django.urls import path
from django.http import JsonResponse
import logging
import json
from .models import Profile
logger = logging.getLogger(__name__)


def api_signup(request):
    logger.debug("--> hello from api_signup")
    if (request.method != 'POST'):
        logger.debug("Method not allowed")
        return HttpResponse('Method not allowed', status=405)
    csrf_token = request.COOKIES.get('csrftoken')
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'HTTP_HOST': 'profileapi',
    }
    logger.debug("--> POST method")
    data = json.loads(request.body)
    logger.debug(f"data : {data['user_id']}")
    try:
      profile = Profile(
      user_id=data['user_id'],
      )
      profile.save()
      logger.debug("--> profile created")
      return JsonResponse({'message': 'Signup successful'}, status=201)
    except Exception as e:
      return JsonResponse({'error': str(e)}, status=400)
    else:
      return JsonResponse({'error': 'Method not allowed'}, status=405)

urlpatterns = [
    path('api/signup/', api_signup, name='api_signup'),
]