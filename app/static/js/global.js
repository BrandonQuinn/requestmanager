/*
	Show a modal with the given title and message
	@param {string} title The title of the modal
	@param {string} msg The message to display in the modal
*/
function showErrorModal(title, msg) {
	document.getElementById('error-modal-title').textContent = title;
	document.getElementById('error-modal-message').textContent = msg;
	var errorModal = new bootstrap.Modal(document.getElementById("error-modal"));
	errorModal.show();
}

/*
	Return the value of the auth_token cookie
	@returns {string} The value of the auth_token cookie
*/
function getTokenFromCookie() {
	const token = document.cookie.split('; ').find(row => row.startsWith('auth_token=')).split('=')[1];
	return token;
}