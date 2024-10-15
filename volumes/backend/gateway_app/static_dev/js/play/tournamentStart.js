// Open WebSocket connection to calcgame and start a new tournament
async function startNewTournament(
    gameMode, gameType, gameRound, p1_name, p2_name, p3_name, p4_name) {
  // Allowed controls depending on game mode (local(2p), remote(1p))
  const keys = (gameMode === 'local') ?
      {w: false, s: false, 5: false, 8: false, ' ': false, Escape: false} :
      {w: false, s: false, ' ': false, Escape: false};

  return new Promise((resolve, reject) => {
    let cfg;
    let game_id;
    let player_role;

    // open WebSocket connection
    const calcGameSocket = getCalcGameSocket(gameMode, gameType, gameRound);
    if (calcGameSocket === undefined) return;

    calcGameSocket.onopen = function(e) {
      console.log('startNewGame > .onopen, connection opened.');

      if (gameMode === 'local')
        calcGameSocket.send(JSON.stringify({
          type: 'opening_connection, game details',
          p1_name: p1_name,
          p2_name: p2_name,
          game_type: gameType
        }));

      else if (gameMode === 'remote')
        calcGameSocket.send(JSON.stringify({
          type: 'opening_connection, my name is',
          p1_name: p1_name,
          game_type: gameType
        }));
    };

    calcGameSocket.onmessage = function(e) {
      let data = JSON.parse(e.data);

      if (data.type === 'connection_established, calcgame says hello') {
        console.log(
            'startNewGame > .onmessage connection_established:', data.message);
        cfg = getInitialVariables(gameType, data.initial_vars);

      } else if (data.type === 'waiting_room') {  // while finding an opponent
                                                  // in remote
        console.log('startNewGame > .onmessage waiting_room:', data.message);
        // Load html waiting room
        document.querySelector('main').innerHTML = data.html;

      }  // displays Start button in local and checkboxes in remote
      else if (data.type === 'game_start') {
        console.log('startNewGame > .onmessage game_start:', data.message);
        // Load start game page
        document.querySelector('main').innerHTML = data.html;
        if (gameMode === 'local') {
          addStartButtonListener()
        } else if (gameMode === 'remote') {
          game_id = data.game_id;
          player_role = data.player_role;
          addIndicatorToThisPlayer(player_role);
          announceGame(data.title, data.message);
          setPlayerReadyCheckBoxes(player_role, calcGameSocket, game_id);
        }

      }  // updates oppenent's ready checkbox in remote
      else if (data.type === 'opponent_ready') {
        console.log('startNewGame > .onmessage opponent_ready:', data.message);
        updateOpponentReadyCheckBoxes(data.opponent)

      } else if (data.type === 'game_countdown') {
        console.log('startNewGame > .onmessage game_countdown:', data.message);
        if (data.countdown === 3) displayCanvasElement(cfg);
        showCountdown(cfg, data.game_state, data.countdown);

      } else if (data.type === 'game_update') {
        // console.log('startNewGame > .onmessage game_update:', data.message);
        if (gameType === 'pong')
          renderPongGame(cfg, data.game_state);
        else if (gameType === 'cows')
          renderCowsGame(cfg, data.game_state);

      } else if (data.type === 'game_end') {
        console.log('startNewGame > .onmessage game_end:', data.message);
        console.log('game_result:', data.game_result);
        document.querySelector('#game-container').innerHTML = data.html;
        document.querySelector('.scorePlayer1').textContent =
            data.game_result.p1_score;
        document.querySelector('.scorePlayer2').textContent =
            data.game_result.p2_score;

        if (gameRound != 'single')
          console.log('game_end gameRound:', gameRound);

        resolve(data.game_result);
        calcGameSocket.close();

      } else
        console.log('startNewGame > .onmessage data:', data);
    };

    calcGameSocket.onclose = function(e) {
      if (!e.wasClean) {
        console.error('WebSocket closed unexpectedly:', e);
        reject('WebSocket closed unexpectedly');
      } else
        console.log('startNewGame > .onclose, connection closed');
    };

    calcGameSocket.onerror = function(e) {
      console.error('startNewGame > .onerror, error occurred: ', e);
      reject(error);
    };

    // Event listeners for controls
    window.addEventListener('keydown', (e) => {
      if (e.key in keys) {
        keys[e.key] = true;
        notifyKeyPressed();
      }
    });
    window.addEventListener('keyup', (e) => {
      if (e.key in keys) {
        keys[e.key] = false;
        notifyKeyPressed();
      }
    });

    function notifyKeyPressed() {
      // console.log('keys:', keys);
      // Filter out the keys that are pressed
      const pressedKeys = Object.keys(keys).filter(key => keys[key]);
      // console.log('pressedKeys:', pressedKeys);
      calcGameSocket.send(JSON.stringify(
          {type: 'key_press', keys: pressedKeys, game_id, player_role}));
    }

    // Event listener for start button
    function addStartButtonListener() {
      const startButton = document.getElementById('startGame-button');
      if (startButton) {
        startButton.addEventListener('click', () => {
          startButton.removeEventListener('click', arguments.callee);
          calcGameSocket.send(JSON.stringify({type: 'players_ready'}));
        });
      }
    }
  });
}
