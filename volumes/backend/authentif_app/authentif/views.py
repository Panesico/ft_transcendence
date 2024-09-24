from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from authentif.forms import SignUpForm, LogInForm
from authentif.models import User
import json
import logging
logger = logging.getLogger(__name__)

def api_logout(request):
    logger.debug("api_logout")
    if request.method == 'GET':
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_login(request):
    logger.debug("api_login")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          # logger.debug(f'Received data: {data}')
          form = LogInForm(request, data=data)
          if form.is_valid():
              user = form.get_user()
              login(request, user)
              logger.debug('api_login > User logged in')
              return JsonResponse({'status': 'success', 'message': 'Login successful'})
          else:
              logger.debug('api_login > Invalid username or password')
              return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=401)
        except json.JSONDecodeError:
            logger.debug('api_login > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    logger.debug('api_login > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_signup(request):
    logger.debug("api_signup")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          logger.debug(f'Received data: {data}')
          form = SignUpForm(data=data)
          if form.is_valid():
              user = form.save(commit=False)
              user.password = make_password(data['password'])
              user = form.save()
              username = data.get('username')
              password = data.get('password')
              logger.info(f'api_signup > User.username: {user.username}, hased pwd {user.password}')

              try:
                  user_obj = User.objects.get(username=username)
              except User.DoesNotExist:
                  logger.debug(f'api_signup > User not found: {username}')
                  return JsonResponse({
                      'status': 'error', 
                      'message': 'User not found'
                  }, status=400)

              # Check if the user is active
              if not user_obj.is_active:
                  logger.debug('api_signup > User is inactive')
                  return JsonResponse({
                      'status': 'error', 
                      'message': 'User is inactive'
                  }, status=400)

              user = authenticate(username=username, password=password)
              if user is not None:
                  logger.debug('api_signup > Sign up successful')
                  login(request, user)
                  return JsonResponse({
                      'status': 'success',
                      'message': 'Sign up successful',
                  })
              else:
                  logger.debug('api_signup > Authentication failed')
                  return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=401)
          else:
              logger.debug('api_signup > Invalid form')
              errors = json.loads(form.errors.as_json())
              logger.debug(f'Errors: {errors}')
              # message = errors.get('username')[0].get('message')
              message = None
              if errors:
                message = next((error['message'] for field_errors in errors.values() for error in field_errors), None)
              logger.debug(f'message: {message}')
              return JsonResponse({'status': 'error', 'message': message}, status=400)
        except json.JSONDecodeError:
            logger.debug('api_signup > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f'api_signup > Unexpected error: {e}')
            return JsonResponse({
                'status': 'error', 
                'message': 'An unexpected error occurred'
            }, status=500)
    logger.debug('api_signup > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)