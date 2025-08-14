import json

#
# Read the credentials from the file
#
def read_credentials(filename='db_credentials.json'):
    with open(filename, encoding='utf-8') as f:
        credentials = json.load(f)
        return credentials