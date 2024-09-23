from django.urls import path
from . import views

urlpatterns = [
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
]
