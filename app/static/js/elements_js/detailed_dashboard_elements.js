// unassigned_request_table_simple_t.html
// This file contains the HTML template for displaying unassigned requests in a simple table format.

// Function to update the table with unassigned requests
function updateUnassignedRequestsTable() {
    var unassignedRequestsTables = document.querySelectorAll('.simple-unassigned-request-table');

    unassignedRequestsTables.forEach(function(table) {
        // Clear existing rows
        table.querySelector('tbody').innerHTML = '';

        // Fetch unassigned requests from the server
        fetch('/api/requests/unassigned')
            .then(response => response.json())
            .then(data => {
                data.forEach(request => {

                    var createdDate = new Date(request[2]);
                    var priorityBadge = '';

                    switch (request[3]) { // Assuming request[3] is the priority
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

                    // Create a new row for each request
                    var row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="text-secondary">${priorityBadge}</td>
                        <td class="text-secondary">${request[5]}</td>
                        <td class="text-secondary"><a href="#" class="text-reset">${createdDate.toLocaleString()}</a></td>
                        <td>
                            <a href="">View<span class="view-id" style="display:none">${request[0]}</span></a>
                        </td>
                    `;
                    table.querySelector('tbody').appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching unassigned requests:', error));
    });
}

// Update the unassigned requests table when the page loads
document.addEventListener('DOMContentLoaded', updateUnassignedRequestsTable);