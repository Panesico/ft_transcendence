In an SPA, the frontend handles routing, so even if a user navigates directly to a URL (e.g., /dashboard or /profile), the server should always return the same index.html file and let the frontend take care of routing.
  - Create a Django view that returns the static index.html
  - Update urls.py to route all requests to that view

// Depending on the route do a fetch request
index.html:
<body>
<div id=main></div>
</body>

js :
fetch('/page/home').xxx((html) => {
  main.innerHTML = '';
  main.inserAdjacentElement('beforeend', html)
}

/page/home :
Hello World !<br>
<button> play!</button>

How to properly catch fetch request in django:
https://stackoverflow.com/questions/72251730/how-to-properly-catch-fetch-request-in-django

Request:
GET /css/styles.css HTTP/1.1

Response:
HTTP/1.1 200 OK
Content-Type: text/html

for templates:
{% load static %}
<!-- {% load 'css/styles.css' %} -->
<link rel="stylesheet" href="{% static 'css/styles.css' %}">
<link rel="icon" href="images/favicon.ico" type="image/x-icon">
<!-- Custom JS -->
<script src="{% static 'js/script.js' %}" defer></script>
<script src="{% static 'js/pong.js' %}" defer></script>

# Explore postgres
docker container exec -it postgres sh
psql -U postgres_main_user -d transcendence_db
\dt
SELECT * FROM authentif_user;

# Include every service when generating the certificate
openssl req -x509 -nodes -newkey rsa:4096 -days 365 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=ES/L=Malaga/O=42 Malaga/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:gateway,DNS:authentif,DNS:profileapi,DNS:play,DNS:gamecalc"

# Create and compile translation files
- python manage.py makemessages -l <language_code>
- python manage.py compilemessages