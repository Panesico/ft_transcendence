// script.js
const fetchedFiles = new Set();

// Load additional JS based on current path
function loadAdditionalJs(path) {
  let url = '/static/js/';

  if (path === '/game') {
    url += 'pong.js';
    loadJs(url);
  } else if (path === '/profile') {
    url += 'profile.js';
    loadJs(url);
  }

  function loadJs(url) {
    if (url.length > 11 && !document.querySelector(`script[src="${url}"]`)) {
      console.log(`%cLoading ${url}`, 'color: yellow; font-weight: bold;');
      const script = document.createElement('script');
      script.src = url;
      script.type = 'text/javascript';
      document.body.appendChild(script);
      fetchedFiles.add(url);
    }
  }
}

// Intercept form submissions for AJAX processing
async function handleFormSubmission() {
  const form = document.querySelector('form');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(form);
      let url = form.action;

      // console.log('formData: ', formData);
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          body: formData
        })

        if (!response.ok) {
          throw new Error(`HTTP error - status: ${response.status}`);
        }

        const data = await response.json();
        // console.log('data: ', data);
        document.querySelector('main').innerHTML = data.html;

        handleFormSubmission();
        loadAdditionalJs(window.location.pathname);

      } catch (error) {
        console.error('Form submission error:', error);
        document.querySelector('main').innerHTML =
            '<h1>Form submission error</h1>';
      }
    });
  }
}

// Load content based on current path
async function loadContent(path) {
  console.log('loadContent');
  let url = (path === '/') ? path : `${path}/`;

  // console.log('url: ', url);
  // Fetch content from Django and inject into main
  try {
    const response =
        await fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})

    // console.log('response: ', response);
    if (!response.ok) {
      throw new Error(`HTTP error - status: ${response.status}`);
    }
    const data = await response.json();
    // console.log('data: ', data);
    document.querySelector('main').innerHTML = data.html;
    handleFormSubmission();
    loadAdditionalJs(path);
  } catch (error) {
    console.error('Error loading content:', error);
    document.querySelector('main').innerHTML = '<h1>Error loading content</h1>';
  }
}

// Handle navigation
function navigate(e, path) {
  e.preventDefault();

  for (const jsFile of fetchedFiles) {
    console.log(`%cRemoving ${jsFile}`, 'color: red; font-weight: bold;');
    const script = document.querySelector(`script[src="${jsFile}"]`);
    script.remove();
    fetchedFiles.delete(jsFile);
  }

  // Push the new state into the browser's history
  if (path === '/api/auth/logout') {
    window.history.pushState({}, '', '/');
  } else
    window.history.pushState({}, '', path);

  loadContent(path);
}

// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  loadContent(window.location.pathname);
};

// Initialise the correct content on page load
// window.onload = () => {
//   console.log('onload');
//   // loadContent(window.location.pathname);
// };
