from django.urls import path
from . import views

urlpatterns = [
    path('api/newTournament/', views.api_newTournament, name='newTournament'),
    path('api/playGame/', views.api_playGame, name='playGame'),
]
