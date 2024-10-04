from django.utils import translation

class LanguagePreferenceMiddleware:
    # This constructor is called only once to create an instance of the middleware, when the Web server starts
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
      if request.user.is_authenticated:
        profile = request.user.profile
        translation.activate(profile.prefered_language)
        request.LANGUAGE_CODE = translation.get_language()