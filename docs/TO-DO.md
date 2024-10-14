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
- send friend request
- windows.on_reload() => create websocket when a user is connected
- Handle websocket if user not connected
- Error handling of friend request -> send a request to himself + send more than a request to the same person
- Add an href associated to the avatar displayed in notification
- Ensure modal close after friend request
- Notification does not get there when user is disconnected
- Add the correct data to friend page ->

