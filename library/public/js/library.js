// Function to check and redirect if the pathname matches '/app/home'
function checkPathname() {
	if (window.location.pathname.startsWith("/app/home")) {
		// Redirect to '/app/library'
		window.location.replace("/app/library");
	}
}

// Continuously check the URL every 500 milliseconds (adjustable)
setInterval(checkPathname, 500);
