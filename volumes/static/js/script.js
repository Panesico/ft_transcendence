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
  // Hide all sections first
  document.querySelectorAll('.page').forEach((page) => {
    page.style.display = 'none';
  });

  // Show appropriate section based on the path
  let pageFound = true;
  switch (path) {
    case '/':
      document.getElementById('home').style.display = 'block';
      break;
    case '/tournament':
      document.getElementById('tournament').style.display = 'block';
      break;
    case '/game':
      document.getElementById('game').style.display = 'block';
      break;
    case '/signup':
      document.getElementById('signup').style.display = 'block';
      break;
    case '/login':
      document.getElementById('login').style.display = 'block';
      break;
    default:
      document.getElementById('page404').style.display = 'block';
      document.title = '404 Not Found';
      pageFound = false;
  }

  // Simulate sending a 404 status code by updating the state
  if (!pageFound) {
    history.replaceState({}, '', '/404');
  }
}

// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  loadContent(window.location.pathname);
};

// Initialise the correct content on page load
window.onload = () => {
  loadContent(window.location.pathname);
};
