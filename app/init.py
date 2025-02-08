import psycopg2
import create_database
import delete_database

username = "postgres"
password = "postgres1234!"

# 
# Check if the database exists
#
def check_database_exists(dbname, user, password, host='localhost', port='5432'):
	try:
		# Connect to the default database
		conn = psycopg2.connect(dbname='requestmanager', user=username, password=password, host=host, port=port)
		conn.autocommit = True
		cursor = conn.cursor()

		# Check if the database exists
		cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
		exists = cursor.fetchone() is not None

		cursor.close()
		conn.close()

		return exists
	except Exception as e:
		print(f"An error occurred: {e}")
		return False

#
# Check if a table exists
#
def check_table_exists(dbname, user, password, table_name, host='localhost', port='5432'):
	try:
		# Connect to the specified database
		conn = psycopg2.connect(dbname=dbname, user=username, password=password, host=host, port=port)
		conn.autocommit = True
		cursor = conn.cursor()

		# Check if the table exists
		cursor.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name='{table_name}'")
		exists = cursor.fetchone() is not None

		cursor.close()
		conn.close()

		return exists
	except Exception as e:
		print(f"An error occurred: {e}")
		return False
	
#
# Check if all tables that are required exist, returns True if everything exists
#
def check_if_all_tables_exists(database, username, password):
	users_exists = check_table_exists('requestmanager', username, password, 'users')
	permssions_exists = check_table_exists('requestmanager', username, password, 'permissions')
	requests_exists = check_table_exists('requestmanager', username, password, 'requests')
	requests_exists = check_table_exists('requestmanager', username, password, 'tokens')
	requests_exists = check_table_exists('requestmanager', username, password, 'app_settings')
	requests_exists = check_table_exists('requestmanager', username, password, 'global_tokens')
	requests_exists = check_table_exists('requestmanager', username, password, 'requests')
	requests_exists = check_table_exists('requestmanager', username, password, 'departments')
	requests_exists = check_table_exists('requestmanager', username, password, 'teams')
	requests_exists = check_table_exists('requestmanager', username, password, 'request_types')

	return users_exists and permssions_exists and requests_exists

#
# Return true if the database and tables exists
#
def is_database_initialised():
	return check_database_exists('requestmanager', username, password) and check_if_all_tables_exists('requestmanager', username, password)

#
# Create the database and tables
#
def init_database(new_db_username, new_db_password):
	create_database.create_database_and_tables(new_db_username, new_db_password)