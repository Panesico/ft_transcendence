// Load content based on current path
async function loadContent(path) {
  // console.log('loadContent');
  let url = (path === '/') ? path : `${path}/`;

  //if url ends by //, remove the last /
  console.log('url: ', url);
  if (url.endsWith('//')) {
    url = url.slice(0, -1);
  }

  // Check go back arrow has been clicked
  if (url === '/back') {
    console.log('Go back arrow clicked');
  }

  // console.log('url: ', url);
  // Fetch content from Django and inject into main
  try {
    let request = new Request(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'include',
    });
    // console.log('loadContent > request: ', request);

    const response = await fetch(request);

    // console.log('loadContent > response: ', response);
    if (!response.ok) {
      throw new Error(`HTTP error - status: ${response.status}`);
    }
    const data = await response.json();

    console.log('loadContent > data: ', data);

    if (data.type && data.message && (data.type === 'logout_successful')) {
      // disconnect main room socket
      handleRefresh("logout");
      closeMainRoomSocket();
      console.log('loadContent > logout_successful');
    }
    else {
      document.querySelector('main').innerHTML = data.html;
    }
    console.log('loadContent > main updated');

    displayMessageInModal(data.message);
    handleFormSubmission();
  } catch (error) {
    console.error('Error loading content:', error);
    document.querySelector('main').innerHTML = '<h1>Error loading content</h1>';
  }
}


// Handle navigation
function navigate(e, path) {
  e.preventDefault();

  // Push the new state into the browser's history
  window.history.pushState({}, '', path);

  loadContent(path);
}


// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  loadContent(window.location.pathname);
};


async function changeLanguage(lang) {
  console.log('changeLanguage > lang: ', lang);
  const path = window.location.pathname;

  // console.log('changeLanguage > current django_language:', getCookie('django_language'));

  try {
    const response = await fetch(`/setLanguage/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
      body: JSON.stringify({ language: lang })
    });

    if (response.ok) {
      data = await response.json();
      // console.log('changeLanguage > new django_language:', getCookie('django_language'));
      loadContent(path);
      handleRefresh('language');
    } else {
      console.error('Error changing language:', response.statusText);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}