async function executeCowGame(p1_name, p2_name) {
  // Get the game container
  const gameContainer = document.querySelector('#game-container');
  const scorePlayer1Element = document.querySelector('.scorePlayer1');
  const scorePlayer2Element = document.querySelector('.scorePlayer2');
  scorePlayer1Element.textContent = 0;
  scorePlayer2Element.textContent = 0;

  // Set up the canvas
  const canvas = document.createElement('canvas');
  canvas.width = 650;
  canvas.height = 450;
  gameContainer.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#d3d3d3';  // Set the fill color
  ctx.strokeStyle = '#d3d3d3';

  // Game variables
  const borderWidth = 15;
  const paddleSpeed = 10;
  let scorePlayer1 = 0;
  let scorePlayer2 = 0;
  let frameCount = 0;        // frame count
  let pauseFrameCount = 0;   // to avoid repeat pause key press
  let gameStarted = false;
  let gameEnded = false;
  let gamePaused = false;

  // Controls
  const keys = {
  w: false,
  s: false,
  ArrowUp: false,
  ArrowDown: false,
  8: false,
  5: false,
  ' ': false,
  Escape: false
  };

  // Event listeners for controls
  window.addEventListener('keydown', (e) => {
    //Check if the key pressed is in the keys object
  if (e.key in keys) {
      //Set the key to true
      keys[e.key] = true;
  }
  });
  window.addEventListener('keyup', (e) => {
  if (e.key in keys) {
      keys[e.key] = false;
  }
  });

  const player1 = {
    x: 50,
    y:canvas.height/2 - paddleHeight/2,
  }

}