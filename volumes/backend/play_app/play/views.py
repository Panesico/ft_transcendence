from django.utils import timezone
from django.http import JsonResponse
from django.db import DatabaseError
from django.forms.models import model_to_dict
# from .forms import TournamentForm
from .models import Game, Tournament
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
            logger.debug(f'game_winner_name: {data.get("game_winner_name")}, id: {data.get("game_winner_id")}')
            logger.debug('api_saveGame > Saving game...')
            game = Game.objects.create(
                game_type = data.get('game_type'),
                game_round = data.get('game_round'),
                p1_name = data.get('p1_name'),
                p2_name = data.get('p2_name'),
                p1_id = data.get('p1_id'),
                p2_id = data.get('p2_id'),
                p1_score = data.get('p1_score'),
                p2_score = data.get('p2_score'),
                game_winner_name = data.get('game_winner_name'),
                game_winner_id = data.get('game_winner_id')
            )
            logger.debug('api_saveGame > Game saved')

            return JsonResponse({'status': 'success', 'message': 'Game saved'})
        except (json.JSONDecodeError, DatabaseError) as e:
            logger.debug(f'api_saveGame > Error: {str(e)}')
            return JsonResponse({'status': 'error', 'message': 'Error: ' + str(e)}, status=400)

    logger.debug('api_saveGame > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
def api_newTournament(request):
    logger.debug("api_newTournament")
    if request.method == 'POST':
        try:
          data = json.loads(request.body)
          logger.debug(f'api_newTournament > Received data: {data}')

          logger.debug('api_newTournament > Creating tournament...')
          tournament = Tournament.objects.create(
              tournament_type = data.get('tournament_type'),
              t_p1_name = data.get('player1'),
              t_p2_name = data.get('player2'),
              t_p3_name = data.get('player3'),
              t_p4_name = data.get('player4'),
              t_p1_id = data.get('p1_id'),
              t_p2_id = data.get('p2_id'),
              t_p3_id = data.get('p3_id'),
              t_p4_id = data.get('p4_id')
          )
          logger.debug(f'api_newTournament > Starting tournament: {tournament}')
          tournament.start_tournament()

          tournament_round = 'Semi-Final 1'
          info = {
              'tournament_id': tournament.id,
              'tournament_round': tournament_round,
              'p1_name': tournament.t_p1_name,
              'p2_name': tournament.t_p2_name,
              'p1_id': tournament.t_p1_id,
              'p2_id': tournament.t_p2_id,
          }

          message = (f"{tournament_round}: {tournament.t_p1_name} against {tournament.t_p2_name}")
          
          return JsonResponse({'status': 'success', 'message': message, 'info': info})
        except (json.JSONDecodeError, DatabaseError) as e:
            logger.debug(f'api_saveGame > Error: {str(e)}')
            return JsonResponse({'status': 'error', 'message': 'Error: ' + str(e)}, status=400)
    logger.debug('api_newTournament > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_updateTournament(request):
    logger.debug("api_updateTournament")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f'api_updateTournament > Received data: {data}')
            tournament_id = data.get('tournament_id')
            game_round = data.get('game_round')
            p1_score = data.get('p1_score')
            p2_score = data.get('p2_score')
            game_winner_name = data.get('game_winner_name')
            game_winner_id = data.get('game_winner_id')

            logger.debug(f'api_updateTournament > tournament_id: {tournament_id}, game_round: {game_round}, p1_score: {p1_score}, p2_score: {p2_score}, game_winner_name: {game_winner_name}, game_winner_id: {game_winner_id}')

            tournament = Tournament.objects.get(id=tournament_id)
            logger.debug(f'api_updateTournament > Tournament: {tournament}')
            logger.debug(f'api_updateTournament > current game_round: {game_round}')

            # Get the game to update the score of
            if game_round == 'Semi-Final 1':
                game = tournament.semifinal1
            elif game_round == 'Semi-Final 2':
                game = tournament.semifinal2
            elif game_round == 'Final':
                game = tournament.final

            logger.debug(f'api_updateTournament > Game {game.id} before: {game}')
            # Update the game
            game = Game.objects.get(id=game.id)
            game.p1_score = p1_score
            game.p2_score = p2_score
            game.game_winner_name = game_winner_name
            game.game_winner_id = game_winner_id
            game.date = timezone.now()
            game.save()
            logger.debug(f'api_updateTournament > Game {game.id} after : {game}')
            tournament = Tournament.objects.get(id=tournament_id)

            # Check the tournament's progress and advance if needed

            # If SF1, start SF2
            if game_round == 'Semi-Final 1':
              tournament_round = 'Semi-Final 2'
              info = {
                  'tournament_id': tournament.id,
                  'tournament_round': tournament_round,
                  'p1_name': tournament.t_p3_name,
                  'p2_name': tournament.t_p4_name,
                  'p1_id': tournament.t_p3_id,
                  'p2_id': tournament.t_p4_id,
              }
              message = (f"{tournament_round}: {tournament.t_p3_name} against {tournament.t_p4_name}")
            # If SF2, start Final
            elif game_round == 'Semi-Final 2':
              tournament.create_final()
              tournament_round = 'Final'
              info = {
                  'tournament_id': tournament.id,
                  'tournament_round': tournament_round,
                  'p1_name': tournament.semifinal1.game_winner_name,
                  'p2_name': tournament.semifinal2.game_winner_name,
                  'p1_id': tournament.semifinal1.game_winner_id,
                  'p2_id': tournament.semifinal2.game_winner_id,
              }
              message = (f"{tournament_round}: {tournament.semifinal1.game_winner_name} against {tournament.semifinal2.game_winner_name}")
            # If Final, end Tournament
            elif game_round == 'Final':
              tournament.date_finished = timezone.now()
              tournament.t_winner_name = game_winner_name
              tournament.t_winner_id = game_winner_id
              tournament.save()
              tournament_round = 'has_ended'
              tournament = Tournament.objects.get(id=tournament_id)
              info = {
                  'tournament': model_to_dict(tournament),
                  'tournament_round': tournament_round
              }
              message = (f"{tournament.t_winner_name} has won the tournament!")
            logger.debug(f'api_updateTournament > {tournament_round}: {message}')
            logger.debug(f'api_updateTournament > info: {info}')
            return JsonResponse({'status': 'success', 'message': message, 'info': info})
        except (json.JSONDecodeError, DatabaseError) as e:
            logger.debug(f'api_updateTournament > Error: {str(e)}')
            return JsonResponse({'status': 'error', 'message': 'Error: ' + str(e)}, status=400)
    logger.debug('api_updateTournament > Method not allowed')
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
