from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from authentif.forms import SignUpForm, LogInForm
import logging
logger = logging.getLogger(__name__)

def api_logout(request):
    if request.method == 'GET':
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_login(request):
    logger.debug("api_login says hiiiiiiiiiii")
    if request.method == 'POST':
        form = LogInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse({'status': 'success', 'message': 'Login successful'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=401)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request, data=request.POST)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)