from django.contrib import admin
from django.urls import path #, re_path
from gateway import views, viewsAuth, viewsErrors, viewsProfile, viewsPlay
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include

handler405 = 'gateway.viewsErrors.get_405'

urlpatterns = [
    # django admin
    path('admin/', admin.site.urls),

    # errors pages
    path('404/', viewsErrors.get_404, name='404'),
    path('405/', viewsErrors.get_405, name='405'),

    # home page
    path('', views.get_home, name='home'),
    path('home/', views.get_home, name='home'),

    # authentif api
    path('signup/', viewsAuth.view_signup, name='signup'),
    path('login/', viewsAuth.view_login, name='login'),
    path('api/auth/logout/', viewsAuth.get_logout, name='logout'),

    # profile api
    path('profile/', viewsProfile.get_profile, name='profile'),
    path('edit_profile/', viewsProfile.get_edit_profile, name='edit_profile'),
    path('edit_profile_general/', viewsProfile.post_edit_profile_general, name='edit_profile_general'),
    path('edit_profile_security/', viewsProfile.post_edit_profile_security, name='edit_profile_security'),
    path('edit_profile_avatar/', viewsProfile.post_edit_profile_avatar, name='edit_profile_avatar'),

    # play api
    path('game/', viewsPlay.get_game, name='game'),
    path('game/saveGame/', viewsPlay.save_game, name='saveGame'),
    path('tournament/', viewsPlay.view_tournament, name='tournament'),
    path('tournament/update/', viewsPlay.view_tournament_update, name='tournamentUpdate'),
    path('remote/', viewsPlay.get_remote, name='remote'),

    # Languages API
    path('i18n/', include('django.conf.urls.i18n')),

    path('api/invite/', views.post_invite, name='post_invite'),
    path('my_friends/', views.list_friends, name='list_friends'),

    # path('api/data/', views.get_files, name='files'),
    # re_path(r'^.*$', views.get_other),  # Catch-all route to serve the SPA
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)