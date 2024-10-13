
// Show the winner and next round button for the tournament
function tournamentNextRound(game_round, p1_name, p2_name) {
  document.getElementById('startGame-winner').remove();
  document.getElementById('nextRound-button').remove();
  document.getElementById('startGame-button').style.display = 'block';
  document.getElementById('namePlayer1').textContent = p1_name;
  document.getElementById('namePlayer2').textContent = p2_name;
  document.querySelector('.scorePlayer1').textContent = 0;
  document.querySelector('.scorePlayer2').textContent = 0;
  document.querySelector('h1').textContent = game_round;

  announceGame(game_round, `${p1_name} vs ${p2_name}`);
}
