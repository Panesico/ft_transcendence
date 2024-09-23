from django.contrib import admin
from django.urls import path, re_path

from gateway import views as views
from gateway import viewsAuth as viewsAuth
from gateway import viewsErrors as viewsErrors

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.get_home, name='home'),
    path('home/', views.get_home, name='home'),

    path('game/', views.get_game, name='game'),
    path('tournament/', views.get_tournament, name='tournament'),
		path('profile/', views.get_profile, name='profile'),

		path('api/invite/', views.post_invite, name='post_invite'),
		path('my_friends/', views.list_friends, name='list_friends'),
    path('404/', viewsErrors.get_404, name='404'),
    path('405/', viewsErrors.get_405, name='405'),

    # authentif app
    path('signup/', viewsAuth.get_signup, name='signup'),
    path('login/', viewsAuth.get_login, name='login'),
    path('api/auth/signup/', viewsAuth.post_signup, name='post_signup'),
    path('api/auth/login/', viewsAuth.post_login, name='post_login'),
    path('api/auth/logout/', viewsAuth.get_logout, name='logout'),
    
    # path('api/data/', views.get_files, name='files'),
    # re_path(r'^.*$', views.get_other),  # Catch-all route to serve the SPA
]
