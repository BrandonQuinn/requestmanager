// Returns a setting by it's name
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