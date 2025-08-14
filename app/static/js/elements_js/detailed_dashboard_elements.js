// unassigned_request_table_simple_t.html
// This file contains the HTML template for displaying unassigned requests in a simple table format.

// Get all the unassigned request tables
var unassignedRequestsTables = document.querySelectorAll('.simple-unassigned-request-table');

// Function to update the table with unassigned requests
function updateUnassignedRequestsTable() {
    unassignedRequestsTables.forEach(function(table) {
        // Clear existing rows
        table.querySelector('tbody').innerHTML = '';

        // Fetch unassigned requests from the server
        fetch('/api/unassigned_requests')
            .then(response => response.json())
            .then(data => {
                data.forEach(request => {
                    // Create a new row for each request
                    var row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="text-secondary">${request.priority}</td>
                        <td class="text-secondary">${request.title}</td>
                        <td class="text-secondary">${request.updates}</td>
                        <td class="text-secondary"><a href="#" class="text-reset">${request.created}</a></td>
                        <td>
                            <a href="/requests/${request.id}">View</a>
                        </td>
                    `;
                    table.querySelector('tbody').appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching unassigned requests:', error));
    });
}
