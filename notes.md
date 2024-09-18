In an SPA, the frontend handles routing, so even if a user navigates directly to a URL (e.g., /dashboard or /profile), the server should always return the same index.html file and let the frontend take care of routing.
  - Create a Django view that returns the static index.html
  - Update urls.py to route all requests to that view