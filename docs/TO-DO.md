Auth:
- Password validator commented while in development. Uncomment 2 * validate_password() in api_signup() and api_edit_profile() of authentif_app/authentif/views.py

@iisaacc
-	Minor module: Show in more languages (3 minimum).
  - Username and password are not being translated X
  - It only adds the country prefix when you click in change language, but it doesnt stay while navigating
-	Replacing Pong implementation in the backend
-	Research web sockets?? Live chat and playing at the same time??
-	Other game implementation
  # Questions
  - It seems so strange to have different django's configs files for each container. "Django’s philosophy revolves around modularity and reusability. This is where the distinction between projects and applications comes into play. A project represents the entire web application — a collection of settings, configurations, and apps that work together to form a complete entity. An application, on the other hand, is a smaller, self-contained module within the project that serves a specific purpose. An application could be a user authentication system, a blog, or any other standalone functionality."


  @BenjaminLarger
- Add an href associated to the avatar displayed in notification to his profile
- Block player -> iZaak
- Ensure modal close after message displayed -> double notification
- Delete friends request when accepted
