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

/*
	Generated a random password.
	@returns {string} The value of randomly generated password
*/
function generatePassword() {
    var length = 32,
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789)(*&^%$#@!",
        pw = "";
    
	for (var i = 0, n = characters.length; i < length; ++i) {
		pw += characters.charAt(Math.floor(Math.random() * n));
	}
	
    return pw;
}