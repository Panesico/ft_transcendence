from django.http import JsonResponse
from django.db import DatabaseError
# from .forms import TournamentForm
from .models import Game, Player
import json
import os
import requests
import logging
logger = logging.getLogger(__name__)

def api_saveGame(request):
    logger.debug("api_saveGame")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f'api_saveGame > Received data: {data}')

            game_type = data.get('game_type')
            game_round = data.get('game_round')
            player1_name = data.get('player1_name')
            player2_name = data.get('player2_name')
            player1_id = data.get('player1_id')
            player2_id = data.get('player2_id')
            score_player1 = data.get('score_player1')
            score_player2 = data.get('score_player2')
            # winner = data.get('winner')

            if not all([game_type, game_round, player1_name, player2_name, score_player1 is not None, score_player2 is not None]):
                return JsonResponse({'status': 'error', 'message': 'Missing or invalid parameters'}, status=400)
            
            player1 = Player.objects.create(
                user_id=player1_id if player1_id else None,
                displayName=player1_name
            )
            player2 = Player.objects.create(
                user_id=player2_id if player2_id else None,
                displayName=player2_name
            )

            logger.debug('api_saveGame > Saving game...')
            game = Game.objects.create(
                game_type=game_type,
                game_round=game_round,
                player1=player1,
                player2=player2,
                score_player1=score_player1,
                score_player2=score_player2,
            )
            logger.debug('api_saveGame > Game saved')
            return JsonResponse({'status': 'success', 'message': 'Game saved'})
        except (json.JSONDecodeError, DatabaseError) as e:
            logger.debug(f'api_saveGame > Database error: {str(e)}')
            return JsonResponse({'status': 'error', 'message': 'Database error: ' + str(e)}, status=400)

    logger.debug('api_saveGame > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
def api_newTournament(request):
    logger.debug("api_newTournament")
    # if request.method == 'POST':
    #     try:
    #       data = json.loads(request.body)
    #       logger.debug(f'Received data: {data}')
    #       logger.debug('api_newTournament > Received data')
    #       form = TournamentForm(data=data)
    #       logger.debug('api_newTournament > Created form')
    #       logger.debug(f'api_newTournament > Form data keys: {data.keys()}')
    #       logger.debug(f'api_newTournament > is form.is_valid()? {form.is_valid()}')
    #       logger.debug(f'api_newTournament > Form.data: {form.data}')
    #       logger.debug(f'api_newTournament > Form errors: {form.errors}')

    #       if form.is_valid():
    #           logger.debug('api_newTournament > TournamentForm valid')
    #           return JsonResponse({'status': 'success', 'message': 'TournamentForm valid'})
    #       else:
    #           logger.debug('api_newTournament > Invalid TournamentForm')
    #           return JsonResponse({'status': 'error', 'message': 'Invalid TournamentForm'}, status=500) # replace with Internal Server Error
    #     except json.JSONDecodeError:
    #         logger.debug('api_newTournament > Invalid JSON')
    #         return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    # logger.debug('api_newTournament > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)