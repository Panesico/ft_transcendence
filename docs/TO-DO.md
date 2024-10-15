Auth:
- Prevent log-in and sign-up if already logged in
- Add password validator, or make AUTH_PASSWORD_VALIDATORS work

Remote game:
- user shouldn't be able to play against themselves through two remote games

@iisaacc
-	Minor module: Show in more languages (3 minimum).
  - Username and password are not being translated X
  - It only adds the country prefix when you click in change language, but it doesnt stay while navigating
-	Replacing Pong implementation in the backend
-	Research web sockets?? Live chat and playing at the same time??
-	Other game implementation
  # Questions
  - rooting.py ??
  - It seems so strange to have different django's configs files for each container. "Django’s philosophy revolves around modularity and reusability. This is where the distinction between projects and applications comes into play. A project represents the entire web application — a collection of settings, configurations, and apps that work together to form a complete entity. An application, on the other hand, is a smaller, self-contained module within the project that serves a specific purpose. An application could be a user authentication system, a blog, or any other standalone functionality."


  @BenjaminLarger
- Redirection to edit_profile after update info
- Add an href associated to the avatar displayed in notification to his profile
- Ensure modal close after friend request
- Set read message to answer in notification and profileapi set as read
- Check if player is already your friend before adding him
- Check if invitation has already be sent before popping the notification
- Block player
- Order player suggestion by alphabetical order
- Clean web socket unused (AsyncWebsocketConsumer)

