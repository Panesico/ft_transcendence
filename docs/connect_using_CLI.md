# 1 - install websocat
brew install websocat

# 2 - Connect to the websocket using websocat
websocat --insecure --header="Cookie: jwt_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjowLCJleHAiOjE3MzAxOTg4MjcsImlhdCI6MTczMDExMjQyNywicm9sZSI6Imd1ZXN0In0.dzoQlKEi3YAMPq6H6k5j4dFHOTrDuvEjQBHMCpGkP4g" "wss://localhost:8443/wss/calcgame/remote/?gameType=pong"

# 3 - Send opening_connection info
{ "type": "opening_connection, my name is", "p1_name": "terminal", "game_type": "pong" }

# 4 - Notify player_ready
Check "player_role" for player1 or player2, and game_id
{ "type": "player_ready", "player": "player2", "game_id": 1 }

# 5 - Input a key
{ "type": "key_press", "keys": ["w"], "game_id": 1, "player_role": "2" }