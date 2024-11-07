Auth:
- Password validator commented while in development. Uncomment 2 * validate_password() in api_signup() and api_edit_profile() of authentif_app/authentif/views.py

@iisaacc



  # Questions


  @BenjaminLarger
- Add an href associated to the avatar displayed in notification to his profile
- Must process two logouts to logout ---> Maybe realated with token/midlleware --> Jorge
    logs : authentif   | Incoming request: GET /api/logout/
    authentif   | EditProfileForm > Meta
    authentif   | model: <class 'authentif.models.User'>
    authentif   | fields: ('username', 'avatar')
    authentif   | api_logout > token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3MzA3OTU3MTIsInJlZnJlc2hfZXhwIjoxNzMxMzk0MTA0LCJpYXQiOjE3MzA3OTU2NTJ9.s8hJUQbQcevhckMhqFBJWHjnN_wktgcaJ1WIl3qIWoQ
    authentif   | api_logout > user assignation failed
    authentif   | api_logout > response: <JsonResponse status_code=200, "application/json">
    authentif   | INFO:     172.18.0.8:44306 - "GET /api/logout/ HTTP/1.1" 200 OK
- Strongsify password
- You can play against yourself
  gateway     | Matched players with combined_id 4_12
gateway     | 
gateway     | ProxyCalcGameInvite > start_game game_id: 120093
calcgame    | INFO:     ('172.18.0.8', 49728) - "WebSocket /pongcalc_consumer/remote/pong/" [accepted]
calcgame    | PongCalcRemote > Client connected
calcgame    | INFO:     connection open
gateway     | ProxyCalcGameLocal > from calcgame: You are connected!
gateway     | ProxyCalcGameInvite > listen_to_calcgame:  p1_name: Bellingham#1, p2_name: Bellingham#2
calcgame    | PongCalcRemote > received data: {'type': 'opening_connection, game details', 'game_id': 120093, 'p1_name': 'Bellingham#1', 'p2_name': 'Bellingham#2'}
calcgame    | PongCalcRemote > Opening connection with players: Bellingham#1, Bellingham#2
gateway     | INFO:     172.18.0.1:42918 - "GET /media/avatars/default.png HTTP/1.1" 200 OK
postgres    | 2024-11-06 14:30:45.866 UTC [27] LOG:  checkpoint starting: time
postgres    | 2024-11-06 14:30:47.584 UTC [27] LOG:  checkpoint complete: wrote 18 buffers (0.1%); 0 WAL file(s) added, 0 removed, 0 recycled; write=1.708 s, sync=0.003 s, total=1.718 s; sync files=18, longest=0.002 s, average=0.001 s; distance=35 kB, estimate=35 kB; lsn=0/1CE6670, redo lsn=0/1CE6638

# TO-DO
  - If someone invite me to play, I accept but then I exit before he joins the room, the other playter doesnt get notified
  - 
