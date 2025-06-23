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
		addInitialTeamSelect.innerHTML = options;
	});
}

updateDepartmentModalSelectables();

// Update the fields that require validation and display that e.g. showing the red x or green tick etc.
function updateFieldValidationUI() {
	
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

updateFieldValidationUI(); // call once to update

// Add event listener to update validation UI on input change for the new department name field
const departmentNameInput = document.getElementById('new-department-name');
departmentNameInput.addEventListener('input', updateFieldValidationUI);

// Add event listener to update validation UI on input change for the new department name field
const departmentDescriptionInput = document.getElementById('new-department-description');
departmentDescriptionInput.addEventListener('input', updateFieldValidationUI);

// Add event listener to add a team to the department (will add to a table/list)
const addTeamToDepartmentBtn = document.getElementById('add-team-to-department-btn');
addTeamToDepartmentBtn.addEventListener('click', function() {
	const selectedTeam = document.getElementById('select-new-department-teams').value;
	
	const teamListTable = document.getElementById('new-department-team-list');
	const selectedTeamName = document.querySelector(`#select-new-department-teams option[value="${selectedTeam}"]`).textContent;
	
	// Check if the team is already in the list
	const existingTeams = Array.from(teamListTable.querySelectorAll('tr td:first-child')).map(td => td.textContent);
	if (existingTeams.includes(selectedTeam)) {
		return;
	}

	if (selectedTeam) {
		const newRow = `
			<tr>
				<td style="display:none">${selectedTeam}</td>
				<td>${selectedTeamName}</td>
				<td>
					<a href="#" id="remove-team-btn">Remove</button>
				</td>
			</tr>
		`;
		teamListTable.innerHTML += newRow;
	}

	// Remove the selected team from the dropdown list
	const selectedOption = document.querySelector(`#select-new-department-teams option[value="${selectedTeam}"]`);
	if (selectedOption) {
		selectedOption.remove();
	}
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
		}
	}
});

/*
	Submit a new department request.
*/
function submitNewDepartment() {
	const departmentNameInput = document.getElementById('new-department-name');
	const initialTeamSelect = document.getElementById('select-initial-team');
	const selectedTeamsSelect = document.getElementById('select-new-department-teams');
}