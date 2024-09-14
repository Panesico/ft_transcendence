// script.js

// Function to handle navigation
function navigate(event, path) {
  // Prevent the default link behavior
  event.preventDefault();

  // Push the new state into the browser's history
  history.pushState({}, '', path);

  // Load the appropriate content based on the path
  loadContent(path);
}

// Function to load content based on the current path
function loadContent(path) {
  // Hide all sections first
  document.querySelectorAll('.page').forEach((page) => {
    page.style.display = 'none';
  });

  // Show the appropriate section based on the path
  switch (path) {
    case '/tournament':
      document.getElementById('tournament').style.display = 'block';
      break;
    case '/game':
      document.getElementById('game').style.display = 'block';
      break;
    default:
      document.getElementById('home').style.display = 'block';
  }
}

// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  // Load the content for the current state
  loadContent(window.location.pathname);
};

// Initialize the correct content on page load
window.onload = () => {
  loadContent(window.location.pathname);
};
