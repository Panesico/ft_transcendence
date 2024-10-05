
async function executeCowGame(p1_name, p2_name) {
  // Get the game container
  const gameContainer = document.querySelector('#game-container');
  const scorePlayer1Element = document.querySelector('.scorePlayer1');
  const scorePlayer2Element = document.querySelector('.scorePlayer2');
  scorePlayer1Element.textContent = 0;
  scorePlayer2Element.textContent = 0;

  // Set up the canvas
  const canvas = document.createElement('canvas');
  canvas.width = 900;
  canvas.height = 550;
  gameContainer.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#d3d3d3';  // Set the fill color
  ctx.strokeStyle = '#d3d3d3';

  // Game variables
  let frameCount = 0;        // frame count
  let pauseFrameCount = 0;   // to avoid repeat pause key press
  let gameStarted = false;
  let gameEnded = false;
  let gamePaused = false;

  // Controls
  const keys = {
    w: false,
    s: false,
    a: false,
    d: false,
    ArrowUp: false,
    ArrowDown: false,
    ArrowLeft: false,
    ArrowRight: false,
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
    y:canvas.height / 2 - 25,
    width: 40,
    height: 40,
    color: '#0000ff',
    score: 0,
  };

  const player2 = {
    x: canvas.width - 50,
    y: canvas.height / 2 - 25,
    width: 40,
    height: 40,
    color: '#ff0000',
    score: 0,
  };

  const cows = [];
  const cowCount = 9; 

  function createCows() {
    for (let i = 0; i < cowCount; i++) {
        cows.push({
            x: Math.random() * (canvas.width - 50),
            y: Math.random() * (canvas.height - 50),
            width: 30,
            height: 30,
            captured: false,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2
        });
    }
  }

  function movePlayers() {
    if (keys.w && player1.y > 0) player1.y -= 2;
    if (keys.s && player1.y < canvas.height - player1.height) player1.y += 2;
    if (keys.a && player1.x > 0) player1.x -= 2;
    if (keys.d && player1.x < canvas.width - player1.width) player1.x += 2;

    if (keys.ArrowUp && player2.y > 0) player2.y -= 2;
    if (keys.ArrowDown && player2.y < canvas.height - player2.height) player2.y += 2;
    if (keys.ArrowLeft && player2.x > 0) player2.x -= 2;
    if (keys.ArrowRight && player2.x < canvas.width - player2.width) player2.x += 2;
  }

  
  function detectCollisions() {
    cows.forEach(cow => {
        if (!cow.captured) {
          if (
                player1.x < cow.x + cow.width &&
                player1.x + player1.width > cow.x &&
                player1.y < cow.y + cow.height &&
                player1.y + player1.height > cow.y
              ) {
                cow.captured = true;
                player1.score++;
                scorePlayer1Element.textContent = player1.score;
                // Speed boosting
                player1.speed = 4;
                setTimeout(() => {
                    player1.speed = 2;
                }, 1000);
              }
              if (
                player2.x < cow.x + cow.width &&
                player2.x + player2.width > cow.x &&
                player2.y < cow.y + cow.height &&
                player2.y + player2.height > cow.y
              ) {
                cow.captured = true;
                player2.score++;
                scorePlayer2Element.textContent = player2.score;
                // Speed boosting
                player2.speed = 4;
                setTimeout(() => {
                    player2.speed = 2;
                }, 1000);
              }
            }
    });
  }

  const player1Image = new Image();
  player1Image.src = 'static/images/game/spaceship1.png';
  
  const player2Image = new Image();
  player2Image.src = 'static/images/game/spaceship2.png';
  
  const cowImage = new Image();
  cowImage.src = 'static/images/game/cow400.png';
  
  function moveCows() {
    cows.forEach(cow => {
        if (!cow.captured) {
            cow.x += cow.vx;
            cow.y += cow.vy;

            // Wall coliision
            if (cow.x <= 0 || cow.x + cow.width >= canvas.width) {
                cow.vx *= -1;
            }
            if (cow.y <= 0 || cow.y + cow.height >= canvas.height) {
                cow.vy *= -1;
            }
        }
    });
  }
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpiar canvas

    // Dibujar jugadores
    ctx.drawImage(player1Image, player1.x, player1.y, player1.width, player1.height);
    ctx.drawImage(player2Image, player2.x, player2.y, player2.width, player2.height);

    // Dibujar vacas
    cows.forEach(cow => {
        if (!cow.captured) {
            ctx.drawImage(cowImage, cow.x, cow.y, cow.width, cow.height);
        }
    });
  }

  // Función principal del juego
  function gameLoop() {
    movePlayers();
    moveCows();
    detectCollisions();
    draw();
    requestAnimationFrame(gameLoop); // Loop del juego
  }
  
  // Inicialización
  createCows();
  console.log('Game Started');
  gameLoop(); // Inicia el juego
}