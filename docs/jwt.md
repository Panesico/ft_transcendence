### requirements.txt
# JWT authentication
PyJWT==2.9.0


### settings.py:
# JWT
JWT_SECRET = os.getenv("JWT_SECRET")


### views.py in authentif
from datetime import timedelta
from django.utils.timezone import now
import jwt
JWT_ALGORITHM = 'HS256'

def set_jwt_cookie(response, token):
    # Set JWT as a cookie
    response.set_cookie(
        key='jwt',
        value=token,
        httponly=True,   # Prevent access to cookie via JavaScript
        secure=True,     # Ensure the cookie is only sent over HTTPS
        samesite='Lax',  # Help prevent CSRF attacks
        expires=now() + timedelta(days=7)  # Cookie expiration (e.g., 7 days)
    )

### import in views files to call the decorator
from .jwt_decorators import jwt_required
@jwt_required

### jwt_decorators.py in gateway or forwards to authentif
from functools import wraps
from django.http import JsonResponse
import jwt
from django.conf import settings  # Use Django settings for the JWT secret

# Assuming you have your JWT secret and algorithm set in your settings
JWT_SECRET = settings.JWT_SECRET  # Define JWT_SECRET in settings.py
JWT_ALGORITHM = 'HS256'

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')

        if not token:
            return JsonResponse({'error': 'Token is missing'}, status=401)

        try:
            # Decode the token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = payload.get('user_id')  # Attach user_id to request
            return view_func(request, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

    return wrapper

### example of login function in authentif

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
              logger.debug(f'api_login > User.id: {user.id}')
              logger.debug('api_login > User logged in')

              token = jwt.encode({
                  'user_id': user.id,
                  'exp': now() + timedelta(days=7)
              }, os.getenv("JWT_SECRET"), algorithm=JWT_ALGORITHM)
              
              response = JsonResponse({'status': 'success', 'message': _('Login successful'), 'user_id': user.id})
          
              # Set the JWT in a secure HTTP-only cookie
              set_jwt_cookie(response, token)

              return response
          else:
              logger.debug('api_login > Invalid username or password')
              return JsonResponse({'status': 'error', 'message': _('Invalid username or password')}, status=401)
        except json.JSONDecodeError:
            logger.debug('api_login > Invalid JSON')
            return JsonResponse({'status': 'error', 'message': _('Invalid JSON')}, status=400)
    logger.debug('api_login > Method not allowed')
    return JsonResponse({'status': 'error', 'message': _('Method not allowed')}, status=405)