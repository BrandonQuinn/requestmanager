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
        const response = await fetch('/api/requests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'request-title': title,
                'request-description': description,
                'request-type': departmentId,
                'request-department': requestTypeId
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok while submitting new request');
        }

        json = await response.json();
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