// TODO -- It doesnt work I think...
function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999; path=/;';
}

// TODO -- Client secret changes over a certain period, making it unsuable.
// Your 42 OAuth settings from Django variables

// Function to handle OAuth code once available
function handleOAuthCode(oauth_callback_url) {
    const oauthCode = getCookie('oauth_code');
    if (oauthCode) {
        console.log("OAuth code found in cookie:", oauthCode);
        // Delete the OAuth code cookie after retrieving it
        deleteCookie('oauth_code');

        // Send the code to the server to exchange for an access token
        fetch(oauth_callback_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
				
            },
            body: JSON.stringify({ code: oauthCode })
        }).then(response => {
            if (response.ok) {
                window.location.href = "/";
            } else {
                console.error("OAuth authentication failed");
            }
        }).catch(error => {
            console.error("Error during OAuth authentication:", error);
        });
    }
}

// When the user clicks the "Login with 42" button
function loginButton42() {
	const configElement = document.getElementById('config42login');
	const CLIENT_ID = configElement.getAttribute('data-client-id');
	const REDIRECT_URI = configElement.getAttribute('data-redirect-uri');
	const STATE = Math.random().toString(36).substring(7); // Generate random state to prevent CSRF attacks
	const oauth_callback_url = configElement.getAttribute('oauth-view-url');
    const authUrl = `https://api.intra.42.fr/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=public&state=${STATE}`;
    const width = 600;
    const height = 600;
    const left = (window.innerWidth / 2) - (width / 2);
    const top = (window.innerHeight / 2) - (height / 2);
    const authWindow = window.open(authUrl, "42OAuthLogin", `width=${width},height=${height},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,scrollbars=no,resizable=no`);

    // Polling for OAuth code every second after the popup is opened
    const intervalId = setInterval(function() {
        // Check for the OAuth code in cookies
        const oauthCode = getCookie('oauth_code');
        if (oauthCode) {
            clearInterval(intervalId); // Stop polling once we get the OAuth code
            authWindow.close(); // Close the popup

            // Handle the OAuth code (send to server, etc.)
            handleOAuthCode(oauth_callback_url);
        }
    }, 1000); // Check every 1 second
};
