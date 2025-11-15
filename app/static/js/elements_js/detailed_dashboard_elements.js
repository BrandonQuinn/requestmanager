/*
    Updates the unassigned requests table with data from the server
*/
function updateUnassignedRequestsTable() {
    var unassignedRequestsTables = document.querySelectorAll('.simple-unassigned-request-table');

    unassignedRequestsTables.forEach(function (table) {

        // Clear existing rows
        table.querySelector('tbody').innerHTML = '';

        // Fetch unassigned requests from the server
        fetch('/api/requests/unassigned')
            .then(response => {
                if (response.status == 403) { // Permission denied
                    unassignedRequestsTables.forEach(function (table) {
                        table.innerHTML = '<div style="margin:15px">Permission denied to view unassigned requests.</div>';
                    });
                    return;
                }

                if (!response.ok && response.status != 403) {
                    showErrorModal('Error', 'An error occurred while fetching unassigned requests.');
                    throw new Error('Network response was not ok while fetching unassigned requests');
                }

                response.json().then(data => {
                    data.forEach(request => {
                        var createdDate = new Date(request[2]);
                        var priorityBadge = '';
                        const priority = request[3]; // Assuming request[3] is the priority

                        switch (priority) { // Assuming request[3] is the priority
                            case 1:
                                // Change color to red for high priority
                                priorityBadge = `<span class="badge bg-purple text-purple-fg">${priority}</span>`;
                                break;
                            case 2:
                                // Change color to orange for medium priority
                                priorityBadge = `<span class="badge bg-red text-red-fg">${priority}</span>`;
                                break;
                            case 3:
                                // Change color to yellow for low priority
                                priorityBadge = `<span class="badge bg-orange text-orange-fg">${priority}</span>`;
                                break;
                            case 4:
                                // Default color
                                priorityBadge = `<span class="badge bg-yellow text-yellow-fg">${priority}</span>`;
                                break;
                        }

                        // Create a new row for each request
                        var row = document.createElement('tr');
                        row.innerHTML = `
                        <td class="text-secondary">${priorityBadge}</td>
                        <td class="text-secondary"><a href="#" class="text-reset">${request[6]}</a></td>
                        <td class="text-secondary"><a href="#" class="text-reset">${createdDate.toLocaleString()}</a></td>
                        <td>
                            <a href="#" class="view-request-btn" data-bs-toggle="modal"
									data-bs-target="#modal-request-view">View<span class="view-id" style="display:none">${request[0]}</span></a>
                        </td>
                    `;
                        table.querySelector('tbody').appendChild(row);
                    });
                });
            }).catch(error => console.error('Error fetching unassigned requests:', error));
    });
}

/*
    Refreshes the updates list in the request details modal
*/
function updateUpdatesList(requestId) {
    const updatesList = document.getElementById('updates-list');

    // Clear data
    updatesList.innerHTML = '';
    document.getElementById('update-content-field').value = '';

    fetch(`/api/requests/${requestId}/updates`)
        .then(response => response.json())
        .then(updates => {

            // Update the badge on the updates button
            updatesCountBadge = document.getElementById('update-btn-count-badge');
            if (updates.length > 0) {
                updatesCountBadge.textContent = updates.length;

                updatesList.innerHTML = ''; // Clear any existing updates
                updates.forEach(update => {
                    const updateItem = document.createElement('div');
                    updateItem.className = 'list-group-item';
                    updateItem.innerHTML = `
									<div class="col">
										<div class="text-reset d-block">${update[4]}</div>
										<div class="text-secondary">${update[2]} at ${new Date(update[1]).toLocaleString()}</div>
									</div>
								`;
                    updatesList.appendChild(updateItem);
                });
            } else {
                updatesCountBadge.textContent = 0;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            updatesList.innerHTML = 'No updates available.';
        });


    // update the requestid for the button to add an update
    document.getElementById('add-update-btn').setAttribute('data-request-id', requestId);
}

/* 
    Event listener for viewing request details, shows the modal with request data
*/
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('view-request-btn')) {
        const requestId = event.target.querySelector('.view-id').textContent;
        document.getElementById('view-modal-selected-request-id').textContent = requestId;

        fetch(`/api/requests/${requestId}`)
            .then(response => response.json())
            .then(data => {
                // Populate the modal with request data
                priorityBadge = document.getElementById('priority-view-badge');

                switch (data[3]) {
                    case 1:
                        // Change color to red for high priority
                        priorityBadge.innerHTML = `<span class="badge bg-purple text-purple-fg">P${data[3]}</span>`;
                        break;
                    case 2:
                        // Change color to orange for medium priority
                        priorityBadge.innerHTML = `<span class="badge bg-red text-red-fg">P${data[3]}</span>`;
                        break;
                    case 3:
                        // Change color to yellow for low priority
                        priorityBadge.innerHTML = `<span class="badge bg-orange text-orange-fg">P${data[3]}</span>`;
                        break;
                    case 4:
                        // Default color
                        priorityBadge.innerHTML = `<span class="badge bg-yellow text-yellow-fg">P${data[3]}</span>`;
                        break;
                }

                outageBadge = document.getElementById('outage-view-badge');

                if (data[4] === true) {
                    outageBadge.style = 'display:block';
                    outageBadge.textContent = 'Outage';
                } else {
                    outageBadge.style = 'display:none';
                    outageBadge.textContent = 'Outage';
                }

                document.getElementById('title-view-field').value = data[5];
                // document.getElementById('resolve-secondary-text').innerText = '\'' + data[5] + '\'';
                document.getElementById('description-view-field').value = data[6];
                document.getElementById('created-view-date').textContent = new Date(data[2]).toLocaleString();

                // update the select for departments
                updateDepartmentSelect(data[7]);

                // update the select for teams then for asignees ensuring the teams are updated first
                updateTeamSelect(data[8]).then(() => {
                    updateAssingeeSelect(data[9]);
                });

                updateViewRequestTypeField(data[11]);
                updateUpdatesList(requestId);
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorModal('Error', 'An error occurred while fetching the request details.');
            });
    }
});

/*
    Add new update to request when the add update button is clicked
*/
document.getElementById('add-update-btn').addEventListener('click', function () {
    const requestId = this.getAttribute('data-request-id');
    const updateContent = document.getElementById('update-content-field').value;

    fetch(`/api/requests/${requestId}/updates/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            'update-content': updateContent
        })
    })
        .then(response => {
            if (response.ok) {

                // Clear the update content field
                document.getElementById('update-content-field').value = '';

                // Refresh the updates list
                updateUpdatesList(requestId);
            } else {
                throw new Error('Failed to add update');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorModal('Error', 'An error occurred while adding the update.');
        });
});

/*
    Save changes to the request when the save button is clicked
*/
document.getElementById('save-edit-request-btn').addEventListener('click', function () {
    const requestId = document.getElementById('view-modal-selected-request-id').textContent;
    const title = document.getElementById('title-view-field').value;
    const description = document.getElementById('description-view-field').value;
    const departmentId = document.getElementById('department-select').value;
    const teamId = document.getElementById('team-view-field').value;
    const assigneeId = document.getElementById('assignee-view-field').value;
    const typeId = document.getElementById('type-view-field').value;

    fetch(`/api/requests/${requestId}/edit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'request-id': requestId,
            'request-title': title,
            'request-description': description,
            'request-department': departmentId,
            'request-team': teamId,
            'request-assignee': assigneeId,
            'request-type': typeId
        })
    }).then(response => {
        if (response.ok) {
            // Close the modal
            const viewRequestModal = document.getElementById('modal-request-view');
            const modalInstance = bootstrap.Modal.getInstance(viewRequestModal);
            modalInstance.hide();

            // refresh the unassigned requests table
            updateUnassignedRequestsTable();
        }
        else {
            throw new Error('Failed to save changes');
        }
    })
        .catch(error => {
            console.error('Error:', error);
            showErrorModal('Error', 'An error occurred while editing request.');
        })
});

/*
    Function to update department selects with options
*/
async function updateDepartmentSelect(selectedDepartment = null) {
    const departments = await getDepartments();
    const departmentSelect = document.getElementById('department-select');

    // Clear existing options
    departmentSelect.innerHTML = '';

    // Populate with fetched departments as options
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept[0];
        option.textContent = dept[1];
        option.selected = (dept[1] == selectedDepartment);
        departmentSelect.appendChild(option);
    });
}

/*
    When the department select changes, update the team select options (only showing teams in that department)
*/
document.getElementById('department-select').addEventListener('change', function () {
    updateTeamSelect().then(() => {
        updateAssingeeSelect();
    });
});

/*
    When the team select changes, update the assignee select options (only showing users in that team)
*/
document.getElementById('team-view-field').addEventListener('change', function () {
    updateAssingeeSelect();
});

/*
    Function to update the team field in the view request modal
*/
async function updateTeamSelect(selectedTeam = null) {
    const departments = await getDepartments();
    const teams = await getTeams();
    const teamSelect = document.getElementById('team-view-field');
    const selectedDepartment = document.getElementById('department-select').value;

    teamSelect.innerHTML = '';

    departments.forEach(dept => {
        if (dept[0] == selectedDepartment) {
            teamsInDepartments = dept[2];
            teams.forEach(team => {
                if (teamsInDepartments.includes(team[0])) {
                    const option = document.createElement('option');
                    option.value = team[0];
                    option.textContent = team[1];

                    if (selectedTeam != null) {
                        option.selected = (team[1] == selectedTeam);
                    }

                    teamSelect.appendChild(option);
                }
            });
        }
    });
}

/*
    Function to update the assignee field in the view request modal
*/
async function updateAssingeeSelect(selectedAssignee = null) {
    // Get department selected
    const selectedTeam = document.getElementById('team-view-field').value;
    const assignees = await getUsersInTeam(selectedTeam);

    // Clear existing options
    const assigneeSelect = document.getElementById('assignee-view-field');
    assigneeSelect.innerHTML = '';

    // Leave empty if no assignees
    if (assignees == null || assignees.length == 0) {
        return;
    }

    // Populate with fetched assignees
    Object.values(assignees).forEach(assignee => {
        const option = document.createElement('option');
        option.value = assignee[0];
        option.textContent = assignee[8] + " " + assignee[9];

        if (selectedAssignee != null) {
            option.selected = (assignee[1] == selectedAssignee);
        }

        assigneeSelect.appendChild(option);
    });

    // There's no assignee selected, deselect all options, ugh i screwed myself and didnt' use a consistent
    // method of determine if it's unassigned, months ago I decided -1 meant that but also NULL means that and "".
    // wtf have i done
    if (selectedAssignee == null || selectedAssignee == -1 || selectedAssignee == "") {
        const option = document.createElement('option');
        option.value = "-1";
        option.textContent = "";
        option.selected = true;
        assigneeSelect.appendChild(option);
    }
}

/*
    Function to update requests type list in the view request modal
*/
async function updateViewRequestTypeField(selectedType = null) {
    const types = await getTypes();
    const typesSelect = document.getElementById('type-view-field');

    typesSelect.innerHTML = '';

    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type[0];
        option.textContent = type[1];
        option.selected = (type[1] == selectedType);
        typesSelect.appendChild(option);
    });
}

/*
    Function to update the new request modal department select
*/
async function updateNewRequestModal() {
    const departments = await getDepartments();
    const departmentSelect = document.getElementById('new-request-department');

    // Clear existing options
    departmentSelect.innerHTML = '';

    // Populate with fetched departments
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept[0];
        option.textContent = dept[1];
        departmentSelect.appendChild(option);
    });

    const requestTypes = await getRequestTypes();
    const requestTypeSelect = document.getElementById('new-request-type');

    // Clear existing options
    requestTypeSelect.innerHTML = '';

    // Populate with fetched request types
    requestTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type[0];
        option.textContent = type[1];
        requestTypeSelect.appendChild(option);
    });
}

/* 
    On click of the new request submit button, submit the new request form
*/
document.getElementById('new-request-submit').addEventListener('click', function () {
    const title = document.getElementById('new-request-title').value;
    const description = document.getElementById('new-request-description').value;
    const departmentId = document.getElementById('new-request-department').value;
    const requestTypeId = document.getElementById('new-request-type').value;

    try {
        const response = submitNewRequest(title, description, departmentId, requestTypeId);

        // Close the modal
        const newRequestModal = document.getElementById('modal-new-request');
        const modalInstance = bootstrap.Modal.getInstance(newRequestModal);
        modalInstance.hide();

        // refresh the unassigned requests table - do it after we're sure it's been done
        // hence the then() usage. Had a situation where after the table update, the new 
        // request would not show because it update faster than the data was put in to the DB
        response.then(data => {
            updateUnassignedRequestsTable();
        });

    } catch (error) {
        console.error('Error submitting new request:', error);
        showErrorModal('Error', 'An error occurred while submitting the new request.');
    }
});

/*
    Handle when the user clicks the resolve request button. Just adds some text
    on the modal to confirm that it's the right request being resolved.
*/
document.getElementById('resolve-request-btn').addEventListener('click', function () {
    let requestTitle = document.getElementById('title-view-field').value;

    // Add a little message to ensure the user knows what request they're resolving
    let modalSecondayText = document.getElementById('resolve-secondary-text')

    if (requestTitle != "") {
        modalSecondayText.innerHTML = "Would you like to resolve request titled: </br><b>" + requestTitle + "</b>";
    } else {
        modalSecondayText.innerHTML = "";
    }
});

/*
    Handle when the user clicks the confirm button on the resolve request modal.
    This resolves the request, FOR REAL.
*/
document.getElementById('resolve-request-btn-real').addEventListener('click', function () {
    // Get the current request id
    const selectedRequestId = document.getElementById('view-modal-selected-request-id').innerText;

    // Resolve, there's no body for this
    jsonResponse = resolveRequest(selectedRequestId);

    if (jsonResponse[0] && jsonResponse[0] == 'error') {

    } else {
        jsonResponse.then(data => {
            console.log(data);
        });
    }

    // Update the table of unassigned requests
    updateUnassignedRequestsTable()
});

/*
    ASSIGNED REQUESTS TABLE (YOUR REQUESTS)
*/

/*
    Populate the assigned requests table.
*/
async function updateAssignedRequestsTable() {
    var assignedRequestsTables = document.querySelectorAll('.assigned-request-table');
    assignedRequestsTables.forEach(function (table) {

        // Clear existing rows
        table.querySelector('tbody').innerHTML = '';

        // Fetch assigned requests from the server
        var assignedRequests = getAssignedRequests();

        if (assignedRequests[0] && assignedRequests[0] == 'error') {
            console.error('Error fetching assigned requests:', assignedRequests[1]);
            return;
        }

        assignedRequests.then(data => {
            data.forEach(request => {

            });



        }).catch(error => {
            console.error('Error fetching assigned requests:', error);
        });

        // remove the progress bar
        var prog = table.getElementsByClassName('progress');
        console.log(prog);
    });
}

// TODO: Go go go

/*
    Update anything that needs to be updated when the DOM is loaded
*/
document.addEventListener('DOMContentLoaded', updateUnassignedRequestsTable());
document.addEventListener('DOMContentLoaded', updateAssignedRequestsTable());
document.addEventListener('DOMContentLoaded', updateDepartmentSelect());
document.addEventListener('DOMContentLoaded', updateNewRequestModal());
