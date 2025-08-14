if (getTokenFromCookie()) {
	fetch('/api/users/self', {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	})
	.then(response => response.json())
	.then(user => {
		document.getElementById('username-display').textContent = user[1];
		document.getElementById('title-display').textContent = "Breakglass Account (root)";
		
	})
	.catch(error => {
		showErrorModal('Error', 'An error occurred while fetching user details.');
		console.error('Error:', error);
	});
} else {
	showErrorModal('Error', 'An error occurred while fetching user details. No token stored in cookie.');
	console.error('No auth token found');
}

/*
	Fetch requests
*/
fetch('/api/requests/user/self')
	.then(response => response.json())
	.then(data => {
		priorityBadge = ""

		// Sort data by index 2 (date), newest first
		data.sort((a, b) => new Date(b[2]) - new Date(a[2]));

		data.forEach(request => {
			// Check priority and change colour of P indicator
			const priority = request[3];

			switch (priority) {
				case 1:
					// Change color to red for high priority
					priorityBadge = `<span class="badge bg-purple text-purple-fg">P${request[3]}</span>`;
					break;
				case 2:
					// Change color to orange for medium priority
					priorityBadge = `<span class="badge bg-red text-red-fg">P${request[3]}</span>`;
					break;
				case 3:
					// Change color to yellow for low priority
					priorityBadge = `<span class="badge bg-orange text-orange-fg">P${request[3]}</span>`;
					break;
				case 4:
					// Default color
					priorityBadge = `<span class="badge bg-yellow text-yellow-fg">P${request[3]}</span>`;
					break;
			}

			const requestList = document.getElementById('request-list');
			requestList.innerHTML +=
				`
			<div class="list-group-item">
				<div class="row align-items-center">
					<div class="col-auto">${priorityBadge}</div>
					<div class="col text-truncate">
						<a href="#" class="text-reset d-block">${request[5]}</a>
					</div>
					<div class="col-auto">
						<a href="#" class="btn btn-6 btn-primary active w-100 view-request-btn" data-bs-toggle="modal"
									data-bs-target="#modal-request-view"><div style="display:none;" class="request-id">${request[0]}</div>View</a>
					</div>
				</div>
			</div>
			`
		});

	})
	.catch(error => {
		console.error('Error:', error);
	});

/*
	Set the fields in the new request form
*/

typeSelector = document.getElementById('new-request-type');
departmentSelector = document.getElementById('new-request-department');

fetch('/api/requests/departments')
	.then(response => response.json())
	.then(departments => {
		departments.forEach(department => {
			const option = document.createElement('option');
			option.value = department[0];
			option.textContent = department[1];
			departmentSelector.appendChild(option);
		});
	})
	.catch(error => {
		console.error('Error:', error);
	});

fetch('/api/requests/types')
	.then(response => response.json())
	.then(types => {
		types.forEach(type => {
			const option = document.createElement('option');
			option.value = type[0];
			option.textContent = type[1];
			typeSelector.appendChild(option);
		});
	})
	.catch(error => {
		console.error('Error:', error);
	});

/*
	Submit the new request form
*/

newRequestSubmitBtn = document.getElementById('new-request-submit').onclick = function () {
	newRequestTitle = document.getElementById('new-request-title').value;
	newRequestDescription = document.getElementById('new-request-description').value;
	newRequestType = document.getElementById('new-request-type').value;
	newRequestDepartment = document.getElementById('new-request-department').value;

	// do some basic value checking, just needs to be not blank
	if (newRequestTitle !== "" || newRequestDescription !== "" || newRequestType !== "") {
		fetch('/api/requests/new', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				'request-title': newRequestTitle,
				'request-description': newRequestDescription,
				'request-type': newRequestType,
				'request-department': newRequestDepartment
			})
		})
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					location.reload(); // Reload the page to see the new request
				} else {
					showErrorModal('Error', 'Failed to submit request: ' + data.message);
				}
			})
			.catch(error => {
				console.error('Error:', error);
				showErrorModal('Error', 'An error occurred while submitting the request.');
			});
	}
}

/*
	Handle the View button on each request.
*/

document.addEventListener('click', function (event) {
	if (event.target.classList.contains('view-request-btn')) {
		const requestId = event.target.querySelector('.request-id').textContent;

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
				document.getElementById('resolve-secondary-text').innerText = '\''+data[5]+'\'';
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
					document.getElementById('add-update-btn').setAttribute('data-request-id', requestId);
			})
			.catch(error => {
				console.error('Error:', error);
				showErrorModal('Error', 'An error occurred while fetching the request details.');
			});
	}
});

/*
	Handle the add update button on each request.
*/

document.addEventListener('click', function (event) {
	if (event.target.id === 'add-update-btn') {
		const requestId = document.getElementById('add-update-btn').getAttribute('data-request-id');
		const updateText = document.getElementById('update-text').value;
		
		if (updateText !== '') {
			fetch(`/api/requests/${requestId}/updates/new`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					'update-content': updateText
				})
			})
				.then(response => response.json())
				.then(data => {
					if (data.success) {

						// Reload the updates list
						const updatesList = document.getElementById('updates-list');
						fetch(`/api/requests/${requestId}/updates`)
							.then(response => response.json())
							.then(updates => {
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
							})
							.catch(error => {
								console.error('Error:', error);
								updatesList.innerHTML = 'No updates available.';
							});

						// Reset the update text box
						document.getElementById('update-text').value

						// scroll to bottom of modal
						document.getElementById('update-text').scrollIntoView(true);

					} else {
						showErrorModal('Error', 'Failed to add update: ' + data.message);
					}
				})
				.catch(error => {
					console.error('Error:', error);
					showErrorModal('Error', 'An error occurred while adding the update.');
				});
		}
	}
});

/*
	Handle the resolve request button on each request.
*/

document.addEventListener('click', function (event) {
	if (event.target.id == 'resolve-request-btn') {

		// get the id from the current info filled out from when the request was opened
		const requestId = document.getElementById('add-update-btn').getAttribute('data-request-id');

		fetch(`/api/requests/${requestId}/resolve`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		})
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					location.reload(); // Reload the page to see the updated request status
				} else {
					showErrorModal('Error', 'Failed to resolve request: ' + data.message);
				}
			})
			.catch(error => {
				console.error('Error:', error);
				showErrorModal('Error', 'An error occurred while resolving the request.');
			});
	}
});