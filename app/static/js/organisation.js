/*
	Get all departments from the server and return the Promise.
*/
async function getDepartments() {
	try {
		const response = await fetch('/api/departments');
		if (!response.ok) {
			throw new Error(`Error: ${response.status} ${response.statusText}`);
		}
		const departments = await response.json();
		return departments;
	} catch (error) {
		console.error('Failed to fetch departments:', error);
		return [];
	}
}

/*
	Get a team from the server and return the Promise.
*/
async function getDepartmentById(departmentId) {
	try {
		const response = await fetch('/api/departments/' + departmentId);
		// Check if the response is ok (status in the range 200-299)
		if (!response.ok) {
			throw new Error(`Error: ${response.status} ${response.statusText}`);
		}
		const department = await response.json();
		return department; // Assuming the API returns an array with one department object
	} catch (error) {
		console.error('Failed to fetch teams:', error);
		return [];
	}
}

/*
	Get all teams from the server and return the Promise.
*/
async function getTeams() {
	try {
		const response = await fetch('/api/teams');
		if (!response.ok) {
			throw new Error(`Error: ${response.status} ${response.statusText}`);
		}
		const teams = await response.json();
		return teams;
	} catch (error) {
		console.error('Failed to fetch teams:', error);
		return [];
	}
}

/*
	Get team by id
*/
async function getTeamById(teamId) {
	try {
		const response = await fetch('/api/teams/' + teamId);
		if (!response.ok) {
			throw new Error(`Error: ${response.status} ${response.statusText}`);
		}
		const team = await response.json();
		return team[1]; // Assuming the API returns an array with one team object
	} catch (error) {
		console.error('Failed to fetch team:', error);
		return '';
	}
}
/*
	Populate the department table.
*/
const departmentTable = document.getElementById('department-table-rows');
getDepartments().then(departments => {
	departmentTable.innerHTML = "";
	const rows = departments.map(department => {
		getTeamById(department[4]).then(team => {
			departmentTable.innerHTML += `
				<tr>
					<td>${department[1] != null ? department[1] : ""}</td>
					<td class="text-secondary">${department[3] != null ? department[3] : ""}</td>
					<td class="text-secondary">${team}</td>
					<td>
						<div class="btn-list flex-nowrap">
							<a href="#" class="btn btn-1"> Edit </a>
						</div>
					</td>
				</tr>
			`;
		});
	});
});

/*
	Populate the teams table.
*/
const teamsTable = document.getElementById('teams-table-rows');
teamsTable.innerHTML += getTeams().then(teams => {
	const rows = teams.map(team => `
		<tr>
			<td>${team[1] != null ? team[1] : ""}</td> 
			<td class="text-secondary">${team[3] != null ? team[3] : ""}</td>
			<td class="text-secondary">${team[4] != null ? team[4] : ""}</td>
			<td>
				<div class="btn-list flex-nowrap">
					<a href="#" class="btn btn-1">Edit</a>
				</div>
			</td>
		</tr>
	`).join('');
	teamsTable.innerHTML = rows;
});

/*
	Configure and populate the new department modal.
*/

// Set the initial options in the model, will be updated when the teams are fetched
function updateDepartmentModalSelectables() {
	const addTeamsSelect = document.getElementById('select-new-department-teams');
	const addInitialTeamSelect = document.getElementById('select-initial-team');
	getTeams().then(teams => {
		const options = teams.map(team => `
			<option value="${team[0]}">${team[1]}</option>
		`).join('');
		addTeamsSelect.innerHTML = options;
		// addInitialTeamSelect.innerHTML = options;
	});
}

updateDepartmentModalSelectables();

/*
	Update the fields that require validation and display that e.g. showing the red x or green tick etc for the department modal
*/
function updateFieldValidationDepartmentModal() {
	// show when the new department name field is valid or not
	const departmentNameInput = document.getElementById('new-department-name');
	if (departmentNameInput.value.trim() === '') {
		departmentNameInput.classList.remove('is-valid');
		departmentNameInput.classList.add('is-invalid');
	} else {
		departmentNameInput.classList.remove('is-invalid');
		departmentNameInput.classList.add('is-valid');
	}

	// show when the new department description field is valid or not
	const departmentDescriptionInput = document.getElementById('new-department-description');
	if (departmentDescriptionInput.value.trim() === '') {
		departmentDescriptionInput.classList.remove('is-valid');
		departmentDescriptionInput.classList.add('is-invalid');
	} else {
		departmentDescriptionInput.classList.remove('is-invalid');
		departmentDescriptionInput.classList.add('is-valid');
	}
}

updateFieldValidationDepartmentModal(); // call once to update

/*
	NEW DEPARTMENT MODAL FUNCTIONALITY
*/

// Add event listener to update validation UI on input change for the new department name field
const departmentNameInput = document.getElementById('new-department-name');
departmentNameInput.addEventListener('input', updateFieldValidationDepartmentModal);

// Add event listener to update validation UI on input change for the new department name field
const departmentDescriptionInput = document.getElementById('new-department-description');
departmentDescriptionInput.addEventListener('input', updateFieldValidationDepartmentModal);

// Add event listener to add a team to the department (will add to a table/list)
const addTeamToDepartmentBtn = document.getElementById('add-team-to-department-btn');
addTeamToDepartmentBtn.addEventListener('click', function () {
	const selectedTeamId = document.getElementById('select-new-department-teams').value;

	const teamListTable = document.getElementById('new-department-team-list');
	const selectedTeamName = document.querySelector(`#select-new-department-teams option[value="${selectedTeamId}"]`).textContent;

	// Check if the team is already in the list
	const existingTeams = Array.from(teamListTable.querySelectorAll('tr td:first-child')).map(td => td.textContent);
	if (existingTeams.includes(selectedTeamId)) {
		return;
	}

	if (selectedTeamId) {
		const newRow = `
			<tr>
				<td style="display:none">${selectedTeamId}</td>
				<td>${selectedTeamName}</td>
				<td>
					<a href="#" id="remove-team-btn">Remove</button>
				</td>
			</tr>
		`;
		teamListTable.innerHTML += newRow;
	}

	// Remove the selected team from the dropdown list
	const selectedOption = document.querySelector(`#select-new-department-teams option[value="${selectedTeamId}"]`);
	if (selectedOption) {
		selectedOption.remove();
	}

	// Add the selected team to the initial team selection dropdown
	const initialTeamSelect = document.getElementById('select-initial-team');
	const newOption = document.createElement('option');
	newOption.value = selectedTeamId;
	newOption.textContent = selectedTeamName;
	initialTeamSelect.appendChild(newOption);
});

// Add event listener to remove a team from the list when the "Remove" button is clicked
const teamListTable = document.getElementById('new-department-team-list');
teamListTable.addEventListener('click', function (event) {
	if (event.target.id == 'remove-team-btn') {
		const row = event.target.closest('tr');
		if (row) {
			row.remove();

			// Add the removed team back to the dropdown list
			const removedTeamId = row.querySelector('td:first-child').textContent;
			const removedTeamName = row.querySelector('td:nth-child(2)').textContent;
			const addTeamsSelect = document.getElementById('select-new-department-teams');
			const newOption = document.createElement('option');

			newOption.value = removedTeamId;
			newOption.textContent = removedTeamName;
			addTeamsSelect.appendChild(newOption);

			// Remove the team from the initial team selection dropdown
			const initialTeamSelect = document.getElementById('select-initial-team');
			const optionToRemove = initialTeamSelect.querySelector(`option[value="${removedTeamId}"]`);
			if (optionToRemove) {
				optionToRemove.remove();
			}
		}
	}
});

/*
	Submit a new department request.
*/
async function submitNewDepartment() {
	const departmentNameInput = document.getElementById('new-department-name');
	const initialTeamSelect = document.getElementById('select-initial-team');
	const selectedTeamsSelect = document.getElementById('select-new-department-teams');

	if (departmentNameInput.value.trim() === '') {
		showErrorModal('Invalid Department Name', 'Please enter a valid department name.');
		return;
	}

	const teamListTable = document.getElementById('new-department-team-list');
	const selectedTeams = Array.from(teamListTable.querySelectorAll('tr td:first-child')).map(td => td.textContent);
	if (selectedTeams.length === 0) {
		showErrorModal('No Teams Selected', 'Please add at least one team to the department.');
		return;
	}

	const departmentData = {
		name: departmentNameInput.value.trim(),
		description: document.getElementById('new-department-description').value.trim(),
		initial_team: initialTeamSelect.value,
		teams: selectedTeams
	};

	// send the data to the api
	fetch('/api/departments/new', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(departmentData)
	})
		.then(response => {
			if (!response.ok) {
				throw new Error(`Error: ${response.status} ${response.statusText}`);
			}
			return response.json();
		})
		.then(data => {
			console.log('Department created successfully:', data);
			// Optionally, refresh the department table or clear the form
			location.reload(); // Reload the page to reflect changes
		})
		.catch(error => {
			console.error('Failed to create department:', error);
			showErrorModal('Submission Failed', 'An error occurred while creating the department. Please try again.');
		});
}

// Add event listener to the "Submit New Department" button
const submitNewDepartmentBtn = document.getElementById('submit-new-department-btn');
submitNewDepartmentBtn.addEventListener('click', submitNewDepartment);

/*
	NEW TEAM MODAL FUNCTIONALITY
*/

/*
	Update the fields that require validation and display that e.g. showing the red x or green tick etc for the team modal
*/
function updateFieldValidationTeamModal() {
	// show when the new department name field is valid or not
	const teamNameInput = document.getElementById('new-team-name');
	if (teamNameInput.value.trim() === '') {
		teamNameInput.classList.remove('is-valid');
		teamNameInput.classList.add('is-invalid');
	} else {
		teamNameInput.classList.remove('is-invalid');
		teamNameInput.classList.add('is-valid');
	}

	// show when the new department description field is valid or not
	const teamDescriptionInput = document.getElementById('new-team-description');
	if (teamDescriptionInput.value.trim() === '') {
		teamDescriptionInput.classList.remove('is-valid');
		teamDescriptionInput.classList.add('is-invalid');
	} else {
		teamDescriptionInput.classList.remove('is-invalid');
		teamDescriptionInput.classList.add('is-valid');
	}
}

updateFieldValidationTeamModal(); // call once to update before the user opens the modal

// Add event listener to update validation UI on input change for the new department name field
const teamNameInput = document.getElementById('new-team-name');
teamNameInput.addEventListener('input', updateFieldValidationTeamModal);

// Add event listener to update validation UI on input change for the new department name field
const teamDescriptionInput = document.getElementById('new-team-description');
teamDescriptionInput.addEventListener('input', updateFieldValidationTeamModal);

/*
	Submit a new team via the API.
*/
async function submitNewTeam() {
	const teamNameInput = document.getElementById('new-team-name');
	const teamDescriptionInput = document.getElementById('new-team-description');

	if (teamNameInput.value.trim() === '') {
		showErrorModal('Invalid Team Name', 'Please enter a valid team name.');
		return;
	}

	const teamData = {
		name: teamNameInput.value.trim(),
		description: teamDescriptionInput.value.trim()
	};

	// send the data to the api
	fetch('/api/teams/new', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(teamData)
	})
		.then(response => {
			if (!response.ok) {
				throw new Error(`Error: ${response.status} ${response.statusText}`);
			}
			return response.json();
		})
		.then(data => {
			console.log('Team created successfully:', data);
			location.reload(); // Reload the page to reflect changes
		})
		.catch(error => {
			console.error('Failed to create team:', error);
			showErrorModal('Submission Failed', 'An error occurred while creating the team. Please try again.');
		});
}

// Add event listener to the "Submit New Department" button
const submitNewTeamBtn = document.getElementById('submit-new-team-btn');
submitNewTeamBtn.addEventListener('click', submitNewTeam);

/*
	NEW USER MODAL FUNCTIONALITY
*/

// Update the fields that require validation and display that e.g. showing the red x or green tick etc.
async function updateFieldValidationUserModal() {
	// New User Modal

	// show when the new user first name field is valid or not
	const userFirstnameInput = document.getElementById('new-user-firstname');
	if (userFirstnameInput.value.trim() === '') {
		userFirstnameInput.classList.remove('is-valid');
		userFirstnameInput.classList.add('is-invalid');
	} else {
		userFirstnameInput.classList.remove('is-invalid');
		userFirstnameInput.classList.add('is-valid');
	}

	// show when the new user last name field is valid or not
	const userLastnameInput = document.getElementById('new-user-lastname');
	if (userLastnameInput.value.trim() === '') {
		userLastnameInput.classList.remove('is-valid');
		userLastnameInput.classList.add('is-invalid');
	} else {
		userLastnameInput.classList.remove('is-invalid');
		userLastnameInput.classList.add('is-valid');
	}

	// show when the new user username field is valid or not
	const userUsernameInput = document.getElementById('new-user-username');
	if (userUsernameInput.value.trim() === '') {
		userUsernameInput.classList.remove('is-valid');
		userUsernameInput.classList.add('is-invalid');
	} else {
		userUsernameInput.classList.remove('is-invalid');
		userUsernameInput.classList.add('is-valid');
	}

	// show when the new user username field is valid or not
	const userEmailInput = document.getElementById('new-user-email');
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(userEmailInput.value.trim())) {
		userEmailInput.classList.remove('is-valid');
		userEmailInput.classList.add('is-invalid');
	} else if (userEmailInput.value.trim() === '') {
		userEmailInput.classList.remove('is-valid');
		teamEmailInput.classList.add('is-invalid');
	} else {
		userEmailInput.classList.remove('is-invalid');
		userEmailInput.classList.add('is-valid');
	}

	const userPasswordInput = document.getElementById('new-user-password');
	const minPasswordLengthSetting = await fetchSettingByName('user_password_min_length');

	if (userPasswordInput.value.trim().length < minPasswordLengthSetting[2]) {
		userPasswordInput.classList.remove('is-valid');
		userPasswordInput.classList.remove('is-valid-lite');
		userPasswordInput.classList.add('is-invalid');
		userPasswordInput.classList.add('is-invalid-lite');
	} else {
		userPasswordInput.classList.remove('is-invalid');
		userPasswordInput.classList.remove('is-invalid-lite');
		userPasswordInput.classList.add('is-valid');
		userPasswordInput.classList.add('is-valid-lite');
	}
}

updateFieldValidationUserModal(); // call once to update

// Add event listener to update validation UI on input change for the new user firstname field
const userFirstnameInput = document.getElementById('new-user-firstname');
userFirstnameInput.addEventListener('input', updateFieldValidationUserModal);

// Add event listener to update validation UI on input change for the new user lastname field
const userLastnameInput = document.getElementById('new-user-lastname');
userLastnameInput.addEventListener('input', updateFieldValidationUserModal);

// Add event listener to update validation UI on input change for the new user lastname field
const userUsernameInput = document.getElementById('new-user-username');
userUsernameInput.addEventListener('input', updateFieldValidationUserModal);

// Add event listener to update validation UI on input change for the new user lastname field
const userEmailInput = document.getElementById('new-user-email');
userEmailInput.addEventListener('input', updateFieldValidationUserModal);

// Add event listener to update validation UI on input change for the new user lastname field
const userPasswordInput = document.getElementById('new-user-password');
userPasswordInput.addEventListener('input', updateFieldValidationUserModal);

/*
	Generate a random password.
*/
function generatePasswordAndUpdateField() {
	const userPasswordInput = document.getElementById('new-user-password');
	const generatedPassword = generatePassword();
	userPasswordInput.value = generatedPassword;
	updateFieldValidationUserModal();
}

// add listener for when the user clicks the generate password button
const generatePasswordBtn = document.getElementById('generate-password-btn');
generatePasswordBtn.addEventListener('click', generatePasswordAndUpdateField);

function togglePasswordVisibility() {
	const userPasswordInput = document.getElementById('new-user-password');
	if (userPasswordInput.type === 'password') {
		userPasswordInput.type = 'text';
		pwHiddenBtn.style.display = 'none';
		pwVisibleBtn.style.display = 'inline';
	} else {
		userPasswordInput.type = 'password';
		pwHiddenBtn.style.display = 'inline';
		pwVisibleBtn.style.display = 'none';
	}
}

/*
	Add event listeners for the password visibility toggle buttons.
*/

const pwVisibleBtn = document.getElementById('new-user-pw-visible-icon');
pwVisibleBtn.addEventListener('click', togglePasswordVisibility);

const pwHiddenBtn = document.getElementById('new-user-pw-hidden-icon');
pwHiddenBtn.addEventListener('click', togglePasswordVisibility);

// set initial state for password visiblity toggle
pwHiddenBtn.style.display = 'inline';
pwVisibleBtn.style.display = 'none';

/*
	Configure and populate the new team modal.
*/

// Set the initial options in the model, will be updated when the teams are fetched
function updateTeamModalSelectables() {
	const addTeamsSelect = document.getElementById('select-new-team-for-user');
	getTeams().then(teams => {
		const options = teams.map(team => `
			<option value="${team[0]}">${team[1]}</option>
		`).join('');
		addTeamsSelect.innerHTML = options;
	});
}

updateTeamModalSelectables();

// Add event listener to add a team to the user (will add to a table/list)
const addTeamToUserBtn = document.getElementById('add-team-to-user-btn');
addTeamToUserBtn.addEventListener('click', function () {
	const selectedTeamId = document.getElementById('select-new-team-for-user').value;

	const teamListTable = document.getElementById('new-user-team-list');
	const selectedTeamName = document.querySelector(`#select-new-team-for-user option[value="${selectedTeamId}"]`).textContent;

	// Check if the team is already in the list
	const existingTeams = Array.from(teamListTable.querySelectorAll('tr td:first-child')).map(td => td.textContent);
	if (existingTeams.includes(selectedTeamId)) {
		return;
	}

	if (selectedTeamId) {
		const newRow = `
			<tr>
				<td style="display:none">${selectedTeamId}</td>
				<td>${selectedTeamName}</td>
				<td>
					<a href="#" id="remove-team-btn-user-list">Remove</button>
				</td>
			</tr>
		`;
		teamListTable.innerHTML += newRow;
	}

	// Remove the selected team from the dropdown list
	const selectedOption = document.querySelector(`#select-new-team-for-user option[value="${selectedTeamId}"]`);
	if (selectedOption) {
		selectedOption.remove();
	}
});

// Add event listener to remove a team from the list when the "Remove" button is clicked
const userTeamListTable = document.getElementById('new-user-team-list');
userTeamListTable.addEventListener('click', function (event) {
	if (event.target.id == 'remove-team-btn-user-list') {
		const row = event.target.closest('tr');
		if (row) {
			row.remove();

			// Add the removed team back to the dropdown list
			const removedTeamId = row.querySelector('td:first-child').textContent;
			const removedTeamName = row.querySelector('td:nth-child(2)').textContent;
			const addTeamsSelect = document.getElementById('select-new-team-for-user');
			const newOption = document.createElement('option');

			newOption.value = removedTeamId;
			newOption.textContent = removedTeamName;
			addTeamsSelect.appendChild(newOption);
		}
	}
});