// script.js

// Function to handle navigation
function navigate(e, path) {
  e.preventDefault();

  // Push the new state into the browser's history
  history.pushState({}, '', path);

  // Load the appropriate content based on the path
  loadContent(path);
}

// Load content based on current path
function loadContent(path) {
  let url = '';
  switch (path) {
    case '/':
      url = '/';
      break;
    case '/tournament':
      url = '/tournament/';
      break;
    case '/game':
      url = '/game/';
      break;
    case '/signup':
      url = '/signup/';
      break;
    case '/login':
      url = '/login/';
      break;
    default:
      url = '/404/';
  }

  // Fetch content from Django and inject into main
  fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.text();
      })
      .then(html => {
        document.querySelector('main').innerHTML = html;
      })
      .catch(error => {
        console.error('Error loading content:', error);
        document.querySelector('main').innerHTML =
            '<h1>Error loading content</h1>';
      });
}

// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  loadContent(window.location.pathname);
};

// Initialise the correct content on page load
window.onload = () => {
  loadContent(window.location.pathname);

  // document.querySelectorAll('a').forEach(anchor => {
  //   anchor.addEventListener('click', function(e) {
  //     e.preventDefault();
  //     const path = this.getAttribute('href');
  //     history.pushState(null, '', path);
  //     loadContent(path);
  //   });
  // });
};
