import json

#
# Read the credentials from the file
#
def read_credentials(filename='db_credentials.json'):
    with open(filename) as f:
        credentials = json.load(f)
        return credentials