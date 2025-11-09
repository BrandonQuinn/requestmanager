// https://computersarentforme.com/en/RequestManager/Api

/*
    API functions for fetching data related to requests and settings
*/
async function getRequestTypes() {
    let json = [];
    
    try {
        response = await fetch('/api/requests/types')
        
        if (!response.ok) {
            throw new Error('Network response was not ok while fetching request types');
        }

        json = await response.json();
    } catch (error) {
        console.error('Error fetching request types:', error);
        showErrorModal('Error', 'An error occurred while fetching request types.');
    }

    return json;
} 

/*
    Submit a request to create a new request
*/
async function submitNewRequest(title, description, departmentId, requestTypeId) {
    let json = {};

    try {
        const response = await fetch('/api/requests/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'request-title': title,
                'request-description': description,
                'request-type': requestTypeId,
                'request-department': departmentId
            }),
        });

        json = await response.json();

        // TODO: check if response is ok

    } catch (error) {
        throw new Error('Error submitting new request: ' + error.message);
    }
}

/*
    Fetches the list of departments from the API
*/
async function getDepartments() {
    let json = [];
    
    try {
        response = await fetch('/api/requests/departments')

        if (!response.ok) {
            throw new Error('Network response was not ok while fetching departments');
        }

        json = await response.json();
    } catch (error) {
        console.error('Error fetching departments:', error);
        showErrorModal('Error', 'An error occurred while fetching departments.');
    }
    
    return json;
}

/*
 *  Fetches the list of teams from the API
 */
async function getTeams() {
    let json = []; 

    try {
        response = await fetch('/api/teams');
        
        if (!response.ok) {
            throw new Error('Network response was not ok while fetching teams');
        }

        json = await response.json();
    } catch (error) {
        console.error('Error fetching teams:', error);
        showErrorModal('Error', 'An error occurred while fetching teams.');
    }
    return json;
}

/*
    Fetches the list of request types from the API
*/
async function getTypes() {
    let json = [];
    
    try {
        response = await fetch('/api/requests/types')

        if (!response.ok) {
            throw new Error('Network response was not ok while fetching types');
        }

        json = await response.json();
    } catch (error) {
        console.error('Error fetching types:', error);
        showErrorModal('Error', 'An error occurred while fetching types.');
    }
    
    return json;
}

/*
    Returns a setting by it's name
*/
async function fetchSettingByName(settingName) {
	try {
		const response = await fetch(`/api/settings/${settingName}`);
		if (!response.ok) {
			throw new Error(`Error fetching setting: ${response.statusText}`);
		}
		const data = await response.json();
		return data;
	} catch (error) {
		console.error(`Failed to fetch setting ${settingName}:`, error);
		return null;
	}
}

/*
    Get users by team ID
*/
async function getUsersInTeam(teamId) {
    let json = [];

    try {
        response = await fetch(`/api/teams/${teamId}/users`);

        if (!response.ok) {
            throw new Error('Network response was not ok while fetching users in team');
        }
        
        json = await response.json();
    } catch (error) {
        console.error('Error fetching users in team:', error);
        showErrorModal('Error', 'An error occurred while fetching users in team.');
    } 

    return json;
}
