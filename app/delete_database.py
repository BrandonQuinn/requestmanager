import psycopg2
import json
import os

username = "postgres"
password = "postgres1234!"

#
# USED FOR COMPLETELY DESTROYING THE DATABASE (for testing) - to ensure the database
# can be continually re-created without issues
#

#
# Delete all tables
#
def delete_tables(db_name, user, password, host='localhost', port='5432'):
	conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)
	
	try:
		conn.autocommit = True
		cur = conn.cursor()

		# Get all table names
		cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
		tables = cur.fetchall()

		# Drop all tables
		for table_name in tables:
			cur.execute(f"DROP TABLE IF EXISTS {table_name[0]} CASCADE;")
		
		print("All tables dropped successfully.")

	except psycopg2.Error as e:
		print(f"An error occurred: {e}")
	finally:
		if conn:
			conn.close()

#
# Delete the database
#
def delete_database(db_name, user, password, host='localhost', port='5432'):
	conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
	
	try:
		conn.autocommit = True
		cur = conn.cursor()

		# Terminate all connections to th e database
		cur.execute(f"""
			SELECT pg_terminate_backend(pg_stat_activity.pid)
			FROM pg_stat_activity
			WHERE pg_stat_activity.datname = '{db_name}'
			AND pid <> pg_backend_pid();
		""")

		# Drop the database
		cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
		
		print(f"Database {db_name} dropped successfully.")

	except psycopg2.Error as e:
		print(f"An error occurred: {e}")
	finally:
		if conn:
			conn.close()

#
# Deletes the user created for the database
#
def delete_user():
	with open('app/db_credentials.json') as f:
		credentials = json.load(f)
		user_to_delete = credentials['username']

	conn = psycopg2.connect(dbname='postgres', user=username, password=password, host='localhost', port='5432')
	
	try:
		conn.autocommit = True
		cur = conn.cursor()

		# Revoke all privileges on the public schema, need to remove these otherwise user can't be deleted
		cur.execute(f"REVOKE ALL PRIVILEGES ON SCHEMA public FROM {user_to_delete};")

		# Revoke default privileges on the public schema, need to remove these otherwise user can't be deleted
		cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM {user_to_delete};")

		# Drop the user
		cur.execute(f"DROP USER IF EXISTS {user_to_delete};")
		
		print(f"User {user_to_delete} dropped successfully.")

	except psycopg2.Error as e:
		print(f"An error occurred: {e}")
	finally:
		if conn:
			conn.close()

#
# Delete the file used to store the credentials
# 
def delete_db_credentials_file():
	try:
		os.remove('app/db_credentials.json')
		print("db_credentials.json file deleted successfully.")
	except OSError as e:
		print(f"Error: {e.strerror}")

#
# Deletes everything. Be careful with this one.
#
def delete_database_and_tables():
	delete_tables('requestmanager', username, password) 
	delete_database('requestmanager', username, password)
	delete_user()
	delete_db_credentials_file()