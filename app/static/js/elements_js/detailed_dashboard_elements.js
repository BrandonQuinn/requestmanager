// Function to update the table with unassigned requests
function updateUnassignedRequestsTable() {
    var unassignedRequestsTables = document.querySelectorAll('.simple-unassigned-request-table');

    unassignedRequestsTables.forEach(function (table) {

        // Clear existing rows
        table.querySelector('tbody').innerHTML = '';

        // Fetch unassigned requests from the server
        fetch('/api/requests/unassigned')
            .then(response => response.json())
            .then(data => {
                data.forEach(request => {

                    var createdDate = new Date(request[2]);
                    var priorityBadge = '';
                    const priority = request[3]; // Assuming request[3] is the priority

                    switch (priority) { // Assuming request[3] is the priority
                        case 1:
                            // Change color to red for high priority
                            priorityBadge = `<span class="badge bg-purple text-purple-fg">P${priority}</span>`;
                            break;
                        case 2:
                            // Change color to orange for medium priority
                            priorityBadge = `<span class="badge bg-red text-red-fg">P${priority}</span>`;
                            break;
                        case 3:
                            // Change color to yellow for low priority
                            priorityBadge = `<span class="badge bg-orange text-orange-fg">P${priority}</span>`;
                            break;
                        case 4:
                            // Default color
                            priorityBadge = `<span class="badge bg-yellow text-yellow-fg">P${priority}</span>`;
                            break;
                    }

                    // Create a new row for each request
                    var row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="text-secondary">${priorityBadge}</td>
                        <td class="text-secondary">${request[5]}</td>
                        <td class="text-secondary"><a href="#" class="text-reset">${createdDate.toLocaleString()}</a></td>
                        <td>
                            <a class="view-request-btn" data-bs-toggle="modal"
									data-bs-target="#modal-request-view">View<span class="view-id" style="display:none">${request[0]}</span></a>
                        </td>
                    `;
                    table.querySelector('tbody').appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching unassigned requests:', error));
    });
}

// Event listener for viewing request details, shows the modal with request data

document.addEventListener('click', function (event) {
    if (event.target.classList.contains('view-request-btn')) {
        const requestId = event.target.querySelector('.view-id').textContent;

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
                document.getElementById('type-view-field').value = data[11];
                document.getElementById('department-view-field').value = data[7];
                document.getElementById('team-view-field').value = data[8];
                document.getElementById('assignee-view-field').value = data[9];

                // populate the updates modal as well, so when the user clicks on the updates tab, so it's already loaded

                const updatesList = document.getElementById('updates-list');
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
                // document.getElementById('add-update-btn').setAttribute('data-request-id', requestId);
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorModal('Error', 'An error occurred while fetching the request details.');
            });
    }
});

// Update the unassigned requests table when the page loads
document.addEventListener('DOMContentLoaded', updateUnassignedRequestsTable);