from django.urls import path
from . import views

urlpatterns = [
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/checkExists/', views.api_check_exists, name='api_check_exists'),
    path('api/editprofile/', views.api_edit_profile, name='api_edit_profile'),
    path('api/oauth/', views.oauth, name='oauth'),

    # Getter
    path('api/getUserInfo/<str:user_id>/', views.api_get_user_info, name='api_get_user_info'),
]
