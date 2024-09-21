"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.load_home, name='home'),
    path('home/', views.load_home, name='home'),
    path('game/', views.load_game, name='game'),
    path('login/', views.load_login, name='login'),
    path('logout/', views.load_logout, name='logout'),
    path('signup/', views.load_signup, name='signup'),
    path('tournament/', views.load_tournament, name='tournament'),
		path('profile/', views.load_profile, name='profile'),
    path('404/', views.load_404, name='404'),
    path('admin/', admin.site.urls),
    # path('api/data/', views.load_files, name='files'),
    re_path(r'^.*$', views.load_other),  # Catch-all route to serve the SPA
]
