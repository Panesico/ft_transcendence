from django.contrib import admin
from django.urls import path #, re_path
from gateway import views, viewsAuth, viewsErrors, viewsProfile
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.get_home, name='home'),
    path('home/', views.get_home, name='home'),

    path('game/', views.get_game, name='game'),
    path('tournament/', views.get_tournament, name='tournament'),

		path('profile/', viewsProfile.get_profile, name='profile'),
    path('edit_profile/', viewsProfile.get_edit_profile, name='edit_profile'),
    path('edit_profile_general/', viewsProfile.post_edit_profile_general, name='edit_profile_general'),
    path('edit_profile_security/', viewsProfile.post_edit_profile_security, name='edit_profile_security'),


		path('api/invite/', views.post_invite, name='post_invite'),
		path('my_friends/', views.list_friends, name='list_friends'),
    path('404/', viewsErrors.get_404, name='404'),
    path('405/', viewsErrors.get_405, name='405'),

    # authentif app
    path('signup/', viewsAuth.view_signup, name='signup'),
    path('login/', viewsAuth.view_login, name='login'),
    path('api/auth/logout/', viewsAuth.get_logout, name='logout'),
    
    # path('api/data/', views.get_files, name='files'),
    # re_path(r'^.*$', views.get_other),  # Catch-all route to serve the SPA
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)