document.getElementById('login-btn').addEventListener('click', function() {
	const username = document.getElementById('username').value;
	const password = document.getElementById('password').value;

	// Reset alerts and progress elements for user for feedback
	document.getElementsByClassName('login-progress')[0].style.display = 'block';
	
	// Send the username and password to the auth api
	fetch('/api/authenticate', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ username: username, password: password })
	})
	.then(response => response.json())
	.then(data => {
		if (data.token) {
			// Print the token and store it in a cookie
			console.log('Token:', data.token);
			document.cookie = `auth_token=${data.token}; secure; SameSite=Strict`;
			document.cookie = `user=${username}; secure; SameSite=Strict`;

			// redirect to the dashboard
			window.location.href = '/dashboard'
		} else {
			const failedtext = document.getElementsByClassName('signin-failed-text')[0]
			failedtext.style.display = 'block';
			failedtext.innerHTML = data.message
		}
	})
	.catch(error => {
		console.error('Error:', error)
		document.getElementsByClassName('signin-failed-text')[0].style.display = 'block';
	});

	// Hide the progress bar
	document.getElementsByClassName('login-progress')[0].style.display = 'none';
});