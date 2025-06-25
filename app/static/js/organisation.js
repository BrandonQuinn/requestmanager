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
	Populate the department table.
*/
const departmentTable = document.getElementById('department-table-rows');
departmentTable.innerHTML += getDepartments().then(departments => {
	const rows = departments.map(department => `
		<tr>
			<td>${department[1] != null ? department[1] : ""}</td>
			<td>${department[3] != null ? department[3] : ""}</td>
			<td>${department[4] != null ? department[4] : ""}</td>
			<td>
				<div class="btn-list flex-nowrap">
					<a href="#" class="btn btn-1"> Edit </a>
				</div>
			</td>
		</tr>
	`).join('');
	departmentTable.innerHTML = rows;
});

/*
	Populate the teams table.
*/
const teamsTable = document.getElementById('teams-table-rows');
teamsTable.innerHTML += getTeams().then(teams => {
	const rows = teams.map(team => `
		<tr>
			<td>${team[1] != null ? team[1] : ""}</td> 
			<td>${team[3] != null ? team[3] : ""}</td>
			<td>${team[4] != null ? team[4] : ""}</td>
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

// Update the fields that require validation and display that e.g. showing the red x or green tick etc.
function updateFieldValidationUI() {
	
	// New Department Modal

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

	// New Team Modal

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

updateFieldValidationUI(); // call once to update

/*
	NEW DEPARTMENT MODAL FUNCTIONALITY
*/

// Add event listener to update validation UI on input change for the new department name field
const departmentNameInput = document.getElementById('new-department-name');
departmentNameInput.addEventListener('input', updateFieldValidationUI);

// Add event listener to update validation UI on input change for the new department name field
const departmentDescriptionInput = document.getElementById('new-department-description');
departmentDescriptionInput.addEventListener('input', updateFieldValidationUI);

// Add event listener to add a team to the department (will add to a table/list)
const addTeamToDepartmentBtn = document.getElementById('add-team-to-department-btn');
addTeamToDepartmentBtn.addEventListener('click', function() {
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
teamListTable.addEventListener('click', function(event) {
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

// Add event listener to update validation UI on input change for the new department name field
const teamNameInput = document.getElementById('new-team-name');
teamNameInput.addEventListener('input', updateFieldValidationUI);

// Add event listener to update validation UI on input change for the new department name field
const teamDescriptionInput = document.getElementById('new-team-description');
teamDescriptionInput.addEventListener('input', updateFieldValidationUI);

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
