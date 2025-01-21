#
# Read the credentials from the file
#
import json

def read_credentials():
	with open('db_credentials.json') as f:
		credentials = json.load(f)
		return credentials