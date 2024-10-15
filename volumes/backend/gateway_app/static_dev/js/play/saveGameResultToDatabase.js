
async function saveGameResultToDatabase(
    game_type, tournament_id, game_round, p1_name, p1_id, p2_name, p2_id,
    game_result) {
  let path = window.location.pathname;
  let url = '';
  // console.log('path: ', path);
  if (path === '/play/') {
    url = 'saveGame/';
  } else if (path === '/play') {
    url = path + '/saveGame/';
  } else if (path === '/tournament/') {
    url = 'update/';
  } else if (path === '/tournament') {
    url = path + '/update/';
  }
  // console.log('url: ', url);

  const jsonData = {
    'tournament_id': tournament_id,
    'game_type': game_type,
    'game_round': game_round,
    'p1_name': p1_name,
    'p2_name': p2_name,
    'p1_id': p1_id,
    'p2_id': p2_id,
    'p1_score': game_result.scorePlayer1,
    'p2_score': game_result.scorePlayer2,
    'game_winner_name': game_result.winner,
    'game_winner_id': (game_result.winner == p1_name) ? p1_id : p2_id,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    credentials: 'include',
    body: JSON.stringify(jsonData)
  });

  const data = await response.json();
  console.log('data.status: ', data.status);
  console.log('data.message: ', data.message);

  document.querySelector('main').innerHTML = data.html;
}
