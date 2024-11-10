Auth:
- Password validator commented while in development. Uncomment 2 * validate_password() in api_signup() and api_edit_profile() of authentif_app/authentif/views.py

@iisaacc

  # Questions


  @BenjaminLarger
- Strongsify password
- startGame-button does not works during tournament -> does not happens each time
- When we click on a notification during a game, the game get interupted and does not resume -> does not happens each time
- a user should be able to accept a game invite if block
- Fail to save tournament in blockchain -> byte32 conversion


# TO-DO
  - Modal when inviting to play someone


- Logout sometimes fails

- game crashes when accessing some jwt
user_id = await getUserId(jwt_token)

- If friend is blocked, shouldn't be able to start an invite game where the invite had been sent beforehand

- Languages cookies not set properly when changing from edit profile

- user profile pictures don't show with nginx