import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
User = get_user_model()

# In-memory blacklist
blacklisted_tokens = set()  # Set to store blacklisted tokens


class GuestUser:
    """A simple class to represent a guest user."""
    def __init__(self):
        self.id = 0  # Guest user ID
        self.is_authenticated = False

    def __str__(self):
        return 'Guest User'

def generate_guest_token():
	"""Generate a JWT for the guest user."""
	guest_payload = {
		'user_id': 0,
		'exp': datetime.now(timezone.utc) + timedelta(hours=24),
		'iat': datetime.now(timezone.utc),
		'role': 'guest'
	}
	return jwt.encode(guest_payload, settings.SECRET_KEY, algorithm='HS256')

class JWTAuthenticationMiddleware:
    """JWT middleware for authenticating users or creating guest tokens."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_request(self, request):
        """Handle the request before it reaches the view."""
        auth_header = request.headers.get('Authorization')
        jwt_token = request.COOKIES.get('jwt_token')  # Get token from cookie
        
        token = None

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
        elif jwt_token:
            token = jwt_token

        if not token:
            request.user = self.create_guest_user()
            return

        # Check if the token is blacklisted
        if self.is_token_blacklisted(token):
            logger.info("Token is blacklisted, treating as guest.")
            request.user = self.create_guest_user()
            return

        try:
            decoded_data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = decoded_data.get('user_id')

            if user_id is not None:
                user = User.objects.get(pk=user_id)
                request.user = user
            else:
                request.user = self.create_guest_user()

        except (ExpiredSignatureError, InvalidTokenError, User.DoesNotExist) as e:
            logger.error(f"JWT Error: {str(e)} - Treating as guest user.")
            request.user = self.create_guest_user()

    def process_response(self, request, response):
        """Modify the response, setting a token for guest users if needed."""
        jwt_token = request.COOKIES.get('jwt_token')
        
        if jwt_token:
            try:
                jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                return response
            except jwt.ExpiredSignatureError:
                logger.debug('JWT token has expired.')
            except jwt.InvalidTokenError:
                logger.debug('Invalid JWT token.')

        if isinstance(request.user, GuestUser) or not jwt_token:
            guest_token = generate_guest_token()
            response['Authorization'] = f'Bearer {guest_token}'
            response.set_cookie('jwt_token', guest_token, httponly=True, secure=True, samesite='Lax')

        return response

    def create_guest_user(self):
        """Create a guest user (user_id=0)."""
        return GuestUser()

    def is_token_blacklisted(self, token):
        """Check if a token is blacklisted."""
        return token in blacklisted_tokens

    @staticmethod
    def blacklist_token(token):
        """Blacklist a token by adding it to the in-memory set."""
        blacklisted_tokens.add(token)

from functools import wraps
from django.http import JsonResponse

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # If user is not authenticated, respond with an error
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
