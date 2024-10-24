from django.urls import path
from . import views, viewsBlockchain

urlpatterns = [
  # Save single game
  path('api/saveGame/', views.api_saveGame, name='saveGame'),

  # Create and update tournaments
  path('api/createTournament/', views.api_createTournament, name='createTournament'),
  path('api/updateTournament/', views.api_updateTournament, name='updateTournament'),

  path('api/getGames/<str:user_id>/', views.api_getUserGames, name='getGames'),
  path('api/getMatchMaking/<str:user_id>/', views.api_getMatchMaking, name='getMatchMaking'),

  # BlockChain
  path('api/connecttoblockchain/', viewsBlockchain.connect_to_blockchain, name='connect_to_blockchain'),
  
  # Get winrate of a user for a given game type
  path('api/getWinrate/<str:user_id>/<str:game_type>/', views.api_getWinrate, name='getWinrate'),
]
