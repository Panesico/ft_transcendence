from django.db import models

# Player model with user_id if registered user
class Player(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    displayName = models.CharField(max_length=20)

    def __str__(self):
        return self.displayName

# Game model with 2 players, score and winner
class Game(models.Model):
    GAME_TYPES = [
        ('pong', 'Pong'),
    ]

    GAME_ROUNDS = [
        ('single', 'Single'),
        ('semifinal1', 'Semi-Final 1'),
        ('semifinal2', 'Semi-Final 2'),
        ('final', 'Final'),
    ]

    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    game_round = models.CharField(max_length=20, choices=GAME_ROUNDS, default='single')

    player1 = models.ForeignKey(Player, related_name='player1_games', on_delete=models.SET_NULL, null=True)
    player2 = models.ForeignKey(Player, related_name='player2_games', on_delete=models.SET_NULL, null=True)
    
    score_player1 = models.IntegerField()
    score_player2 = models.IntegerField()

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game_type}: {self.player1} vs {self.player2}"

# Tournament with 4 players, 2 semi-finals, final and winner
# class Tournament(models.Model):