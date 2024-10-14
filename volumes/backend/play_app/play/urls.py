from django.urls import path
from . import views

urlpatterns = [
    path('api/saveGame/', views.api_saveGame, name='saveGame'),
    path('api/newTournament/', views.api_newTournament, name='newTournament'),
    path('api/updateTournament/', views.api_updateTournament, name='updateTournament'),
	path('api/getGames/<str:user_id>/', views.api_getUserGames, name='getGames'),
	path('api/getMatchMaking/<str:user_id>/', views.api_getMatchMaking, name='getMatchMaking'),
]
