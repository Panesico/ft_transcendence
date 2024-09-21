// script.js
// const fetchedFiles = new Set();

// Intercept form submissions for AJAX processing
function handleFormSubmission() {
  const form = document.querySelector('form');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const formData = new FormData(form);
      let url = form.action;

      fetch(url, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
      })
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error - status: ${response.status}`);
            }
            return response.text();
          })
          .then(html => {
            document.querySelector('main').innerHTML = html;
            handleFormSubmission();
            loadAdditionalJs(window.location.pathname);
          })
          .catch(error => {
            console.error('Form submission error:', error);
          });
    });
  }
}

// Load additional JS based on current path
function loadAdditionalJs(path) {
  if (path === '/game' && !document.querySelector('script[src="js/pong.js"]')) {
    const script = document.createElement('script');
    script.src = 'js/pong.js';
    document.head.appendChild(script);
  }
	if (path === '/profile' && !document.querySelector('script[src="js/profile.js"]')) {
		console.log('%cLoading profile.js', 'color: yellow; font-weight: bold;');
    const script = document.createElement('script');
    script.src = 'js/profile.js';
    document.head.appendChild(script);
  }

  // if (path === '/game' || path === '/game/') {
  //   console.log('fetchedFiles:', fetchedFiles);
  //   if (!fetchedFiles.has(path)) {
  //     {
  //       const fileName = 'js/pong.js';
  //       const url = `/api/data/?fileName=${encodeURIComponent(fileName)}`;
  //       fetch(url)
  //           .then(response => response.json())
  //           .then(data => {
  //             console.log('Fetched data:', data);
  //           })
  //           .catch(error => {
  //             console.error('Error fetching API data:', error);
  //           });
  //     }
  //   }
  // }
}

// Load content based on current path
function loadContent(path) {
  let url = '';
  if (path === '/')
    url = path;
  else if (
      path === '/game' || path === '/login' || path === '/logout' ||
      path === '/signup' || path === '/tournament' || path === '/admin' ||
      path === '/profile') {
    url = path + '/';
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
        handleFormSubmission();
        loadAdditionalJs(path);
      })
      .catch(error => {
        console.error('Error loading content:', error);
        document.querySelector('main').innerHTML =
            '<h1>Error loading content</h1>';
      });
}

// Handle navigation
function navigate(e, path) {
  e.preventDefault();

  // Push the new state into the browser's history
  history.pushState({}, '', path);

  loadContent(path);
}

// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  loadContent(window.location.pathname);
};

// Initialise the correct content on page load
window.onload = () => {
  console.log('onload');
  loadContent(window.location.pathname);
};
