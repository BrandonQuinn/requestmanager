import json
import os
import psycopg2
import db_util

#
# Checks the credentials file exists, and that it contains a username 
# and password and they work with the database
#
def check_credentials():
    if not os.path.exists('db_credentials.json'):
        return {'status': 'failed', 'message': 'File not found'}

    with open('db_credentials.json', encoding='utf-8') as f:
        credentials = json.load(f)

    if not credentials.get('username') or not credentials.get('password'):
        return {'status': 'failed', 'message': 'Username or password not found in file'}
    
    # check if the credentials work with the database
    try:
        conn = psycopg2.connect(dbname='requestmanager', user=credentials['username'], password=credentials['password'], host='localhost', port='5432')
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.close()
        conn.close()
    except Exception as e:
        return {'status': 'failed', 'message': f'An error occurred: {e}'}

    return {'status': 'success', 'message': 'Credentials are valid'}

#
# Use the db_credentials.json file to check if a table exists
#
def check_table_exists(table_name):
    credentials = db_util.read_credentials()

    try:
        # Connect to your postgres DB
        connection = psycopg2.connect(
            dbname='requestmanager',
            user=credentials['username'],
            password=credentials['password'],
            host='localhost',
            port=5432
        )

        cursor = connection.cursor()
 
        # Check if the table exists
        cursor.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name='{table_name}'")
        exists = cursor.fetchone() is not None

        return exists

    except Exception as error:
        print(f'Error checking table: {error}')
    finally:
        if connection:
            cursor.close()
            connection.close()
