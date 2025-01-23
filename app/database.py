import psycopg2
from flask import jsonify
import json
import auth
import db_util 

#
# Connect to the database
#
def connect():
	credentials = db_util.read_credentials()

	try:
		# Connect to your postgres DB
		connection = psycopg2.connect(
			dbname="requestmanager",
			user=credentials['username'],
			password=credentials['password'],
			host="localhost",
			port=5432
		)

		return connection

	except Exception as error:
		print(f"Error connecting to the database: {error}")
		return None

#
# Close the connection to the database
#
def disconnect(connection):
	if connection:
		connection.close()

#
# Get all users from the database
#
def get_all_users():
	try:
		# Connect to your postgres DB
		connection = connect()

		cursor = connection.cursor()

		# Execute a query
		cursor.execute("SELECT * FROM users")

		# Retrieve query results
		users = cursor.fetchall()

		return users

	except Exception as error:
		print(f"Error fetching users: {error}")
	finally:
		if connection:
			cursor.close()
			disconnect(connection)
#
# Add a new user to the database
#
def add_user(username, email, password, permissions, team, level):
	# TODO: check format of the inputs will be valid for the database

	try:
		# Connect to your postgres DB
		connection = connect()

		cursor = connection.cursor()

		# Execute a query to insert a new user
		insert_query = """
		INSERT INTO users (username, email, password, permissions, team, level)
		VALUES (%s, %s, %s, %s)
		"""
		cursor.execute(insert_query, (username, password, email, permissions, team, level))

		# Commit the transaction
		connection.commit()

		return jsonify({"message": "User added successfully"}), 201

	except Exception as error:
		print(f"Error adding user: {error}")
		return jsonify({"message": "Error adding user"}), 500
	finally:
		if connection:
			cursor.close()
			disconnect(connection)

#
# Check if the breakglass account has been set in the settings table. To help prevent re-creation via the API.
# Helps prevent the circumstance where if we only checked if the breakglass account exists and it didn't then the API might offer the
# option to set it. If it doesn't exists but was set ever, that's a different problem, the API will not offer the ability to fix that.
# The policy will be; no modifications to the breakglass account once it has been set without logging in with it.
#
def check_breakglass_account_is_set():
	try:
		# Connect to your postgres DB
		connection = connect()
		cursor = connection.cursor()

		# Execute a query
		cursor.execute("SELECT * FROM app_settings WHERE setting_name='breakglass_set'")

		# Check if the value column is 1
		breakglass_account = cursor.fetchone()
		if breakglass_account and breakglass_account[2] == 1:
			return True
		else:
			return False
		
	except Exception as error:
		print(f"Error fetching breakglass account: {error}")
		return False
	finally:
		if connection:
			cursor.close()
			disconnect(connection)

#
# Create the breakglass account in the database
#
def create_breakglass_account(password):
	try:
		# Connect to your postgres DB
		connection = connect()

		cursor = connection.cursor()

		# Execute a query to insert a new user
		insert_query = """
		INSERT INTO users (username, email, password, permissions, team, level)
		VALUES (%s, %s, %s, %s, %s, %s)
		"""

		# Hash the password
		hash = auth.hash(password)
		cursor.execute(insert_query, ('breakglass', 'breakglass@breakglass.com', hash, 0, 'breakglass', 0))

		connection.commit()

		# Update the settings table to set breakglass_set to 1
		update_query = """
		UPDATE app_settings
		SET value = 1
		WHERE setting_name = 'breakglass_set'
		"""
		cursor.execute(update_query)

		# Commit the transaction
		connection.commit()

	finally:
		if connection:
			cursor.close()
			disconnect(connection)