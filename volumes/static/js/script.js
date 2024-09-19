// script.js

// Function to handle navigation
function navigate(e, path) {
  e.preventDefault();

  // Push the new state into the browser's history
  history.pushState({}, '', path);

  // Load the appropriate content based on the path
  loadContent(path);
}

// Load additional JS based on current path
function loadAdditionalJs(path) {
  if (path === '/game') {
    const script = document.createElement('script');
    script.src = 'js/pong.js';
    document.head.appendChild(script);
  }
}

// Load content based on current path
function loadContent(path) {
  let url = '';
  if (path === '/' || path === '/game' || path === '/login' ||
      path === '/signup' || path === '/tournament' || path === '/admin') {
    url = path;
  } else {
    url = '/404/';
  }

  // console.log('url: ', url);
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
        loadAdditionalJs(path);
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
