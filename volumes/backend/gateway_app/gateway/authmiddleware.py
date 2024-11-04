import os, logging, jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
User = get_user_model()

# In-memory blacklist with expiration timestamps
blacklisted_tokens = {}  # Dictionary to store blacklisted tokens and their expiration times

def get_user_id(token):
    try:
        decoded_data = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )
        return decoded_data.get('user_id')
    except:
        return None

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
		'exp': int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
		'iat': int(datetime.now(timezone.utc).timestamp()),
		'role': 'guest'
	}
	return jwt.encode(guest_payload, settings.SECRET_KEY, algorithm='HS256')

def generate_jwt_token(user, refresh_exp=None):
    # Set refresh expiration to 7 days from now if not specified
    refresh_exp = refresh_exp or (datetime.now(timezone.utc) + timedelta(days=7))

    # Convert datetime objects to timestamps
    payload = {
        'user_id': user.id,
        'exp': int((datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp()),  # Short-lived access expiration
        'refresh_exp': int(refresh_exp.timestamp()),  # Long-lived refresh expiration
        'iat': int(datetime.now(timezone.utc).timestamp()),  # Issued at time
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

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
        token = auth_header.split('Bearer ')[1] if auth_header and auth_header.startswith('Bearer ') else jwt_token

        if not token:
            request.user = self.create_guest_user()
            return

        if self.is_token_blacklisted(token):
            logger.info("Token is blacklisted, treating as guest.")
            request.user = self.create_guest_user()
            return

        try:
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
            
            # Check if it's a guest token
            
            if decoded_data.get('role') == 'guest':
                request.user = self.create_guest_user()
                return

            user_id = decoded_data.get('user_id')
            
            exp = datetime.fromtimestamp(decoded_data['exp'], timezone.utc)
            
            # If it's not a guest, get refresh_exp
            refresh_exp = datetime.fromtimestamp(decoded_data['refresh_exp'], timezone.utc) if 'refresh_exp' in decoded_data else None
            iat = datetime.fromtimestamp(decoded_data['iat'], timezone.utc)

            # Handle refresh expiration logic for authenticated users
            if refresh_exp and datetime.now(timezone.utc) > refresh_exp:
                logger.info("Refresh period expired, treating as guest.")
                request.user = self.create_guest_user()
                return

            if datetime.now(timezone.utc) > exp:
                # If access expired but within refresh period, refresh the token
                time_since_issued = datetime.now(timezone.utc) - iat
                new_refresh_exp = refresh_exp - time_since_issued if refresh_exp else None

                # Generate a new token with updated refresh period
                user = User.objects.get(pk=user_id)
                new_token = generate_jwt_token(user, refresh_exp=new_refresh_exp)

                # Set the new token in the request attribute for process_response
                request.new_jwt_token = new_token
                request.user = user
            else:
                # Token is valid as an access token
                user = User.objects.get(pk=user_id)
                request.user = user

        except (ExpiredSignatureError, InvalidTokenError, User.DoesNotExist) as e:
            logger.error(f"JWT Error: {str(e)} - Treating as guest user.")
            request.user = self.create_guest_user()

    def process_response(self, request, response):
        """Modify the response, setting a token for guest users if needed."""
        # Clean up expired blacklisted tokens
        self.cleanup_blacklisted_tokens()

        if hasattr(request, 'new_jwt_token'):
            new_token = request.new_jwt_token
            response.set_cookie('jwt_token', new_token, httponly=True, secure=True, samesite='Lax')


        # 1. Check if the response already has an authenticated JWT in the 'Authorization' header
        if 'Authorization' in response and response['Authorization'].startswith('Bearer '):
            return response

        # 2. Check if the response has a jwt_token cookie
        response_jwt_token = response.cookies.get('jwt_token')
        if response_jwt_token:
            try:
                # Decode the JWT token from the response cookie to verify it's valid
                jwt.decode(response_jwt_token.value, settings.SECRET_KEY, algorithms=['HS256'])
                # If the token is valid, do not modify the response
                return response
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                # Log the issue but continue processing since the token in the response might be bad
                logger.debug(f'Response JWT token error: {str(e)}')
            except Exception as e:
                logger.error(f'Unknown error when decoding response JWT token: {str(e)}')

        self.verify_or_generate_guest_token(request, response)

        return response

    def verify_or_generate_guest_token(self, request, response):
        jwt_token = request.COOKIES.get('jwt_token')

        if isinstance(request.user, GuestUser) or not request.user.is_authenticated:
            if jwt_token:
                try:
                    jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
                    return
                except:
                    pass
            # Generate and set a new guest token if no valid token exists
            guest_token = generate_guest_token()
            response['Authorization'] = f'Bearer {guest_token}'
            response.set_cookie('jwt_token', guest_token, httponly=True, secure=True, samesite='Lax')

    def create_guest_user(self):
        """Create a guest user (user_id=0)."""
        return GuestUser()

    def is_token_blacklisted(self, token):
        """Check if a token is blacklisted."""
        return token in blacklisted_tokens and blacklisted_tokens[token] > datetime.now(timezone.utc)

    @staticmethod
    def blacklist_token(token, refresh_exp):
        """Blacklist a token with the expiration set to the refresh token duration."""
        blacklisted_tokens[token] = refresh_exp

    @staticmethod
    def cleanup_blacklisted_tokens():
        """Remove expired tokens from the blacklist."""
        current_time = int(datetime.now(timezone.utc).timestamp())  # Convert to timestamp
        tokens_to_remove = [token for token, exp in blacklisted_tokens.items() if exp < current_time]
        for token in tokens_to_remove:
            del blacklisted_tokens[token]

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
