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

# TO-DO
  - Modal when inviting to play someone
  - If someone invite me to play, I accept but then I exit before he joins the room, the other playter doesnt get   notified
  - 