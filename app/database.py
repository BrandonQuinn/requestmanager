import psycopg2
from flask import jsonify
import json
import auth
import db_util 
from datetime import datetime, timedelta

# Used for creating the database and new user then cleared from memory
temp_db_username = None
temp_db_password = None

#
# Connect to the database
#
def connect():
	# TODO: Cache the connection. So we don't keep reading the file.
	# TODO: Remove exception handling internally, raise the exceptions
	credentials = db_util.read_credentials()

	try:
		# Connect to your postgres DB
		connection = psycopg2.connect(
			dbname="requestmanager",
			user=credentials['username'],
			password=credentials['password'],
			host="localhost",
			port="5432"
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

######################################
#	USERS
######################################

#
# Get all users from the database
#
def get_all_users():
	# TODO: Remove exception handling internally, raise the exceptions

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
# Return all fields for a user by the username
#
def get_user_by_username(username):
	# TODO: Remove exception handling internally, raise the exceptions

	try:
		# Connect to the db
		connection = connect()
		cursor = connection.cursor()

		# Execute a query to get the user by username
		query = "SELECT * FROM users WHERE username = %s"
		cursor.execute(query, (username,))

		# Retrieve query results
		user = cursor.fetchone()

		if user:
			return user
		else:
			raise Exception("No user found when getting user by username from database")
			
	except Exception as error:
		print(f"Error adding user: {error}")
		return None
	finally:
		if connection:
			cursor.close()
			disconnect(connection)

#
# Add a new user to the database
#
def add_user(username, email, password, permissions, team, level):
	# TODO: check format of the inputs will be valid for the database
	# TODO: Remove exception handling internally, raise the exceptions

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
	# TODO: Remove exception handling internally, raise the exceptions

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
	# TODO: Remove exception handling internally, raise the exceptions

	try:
		# Connect to your postgres DB
		connection = connect()
		cursor = connection.cursor()

		# Execute a query to insert a new user
		insert_query = """
		INSERT INTO users (username, email, password, permissions, team, level)
		VALUES (%s, %s, %s, %s, %s, %s)
		"""

		# Hash the password and create the entry in the database
		hash = auth.hash(password)
		cursor.execute(insert_query, ('breakglass', 'breakglass@breakglass.com', hash, '{0}', '{0}', 0))
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

	# print the error first before sending it to the calling function, which will likely be an api call to send the
	# error back to the user interface
	except Exception as error:
		print(f"Error creating breakglass account: {error}")
		raise error
	finally:
		if connection:
			cursor.close()
			disconnect(connection)


######################################
#	SETTINGS
######################################

#
# Get a setting by it's name
#
def get_setting_by_name(setting_name):
	try:
		# Connect to your postgres DB
		connection = connect()
		cursor = connection.cursor()

		# Execute a query to get the setting by name
		query = "SELECT * FROM app_settings WHERE setting_name = %s"
		cursor.execute(query, (setting_name,))

		# Retrieve query results
		setting = cursor.fetchone()

		if setting:
			return setting
		else:
			raise Exception('Failed to find setting %s in database', setting_name)

	except Exception as error:
		print(f"Error fetching setting: {error}")
		raise error
	finally:
		if connection:
			cursor.close()
			disconnect(connection)


########################################################
#			TOKENS
########################################################

#
# Return the results from a query to get the token by the token value
#
def get_token(token):
	try:
		# Connect to your postgres DB
		connection = connect()
		cursor = connection.cursor()

		# Execute a query to get the token
		query = "SELECT * FROM tokens WHERE token = %s"
		cursor.execute(query, (token,))

		# Retrieve query results
		token_data = cursor.fetchone()

		if token_data:
			return token_data
		else:
			raise Exception("Token not found in database")

	except Exception as error:
		print(f"Error fetching token: {error}")
		raise error
	finally:
		if connection:
			cursor.close()
			disconnect(connection)

#
# Takes the token created and associated with the user and saves it to the database with a new time and deadline.
# This function will refresh the token by default.
# Returns True if the user was created, false or an exception if not
#
def save_user_token(username, token):
	# TODO: Move token time deadline login to auth.authenticate function (database module should be dumb database access)

	# Connect to your postgres DB
	connection = connect()
	cursor = connection.cursor()

	# Check if the user exists
	query = "SELECT * FROM users WHERE username = %s"
	cursor.execute(query, (username,))
	user = cursor.fetchone()

	# User not found in the database, throw an error
	if not user:
		print(f"Error: User not found while saving token to user token table")
		raise Exception("User not found while saving token to user token table")

	# get the timeout setting value from the settings table
	timeout_setting = get_setting_by_name('user_session_timeout')
	breakglass_timeout_setting = get_setting_by_name('breakglass_session_timeout')

	# Generate current timestamp and deadline timestamp, breakglass will have much shorter timeout
	created_at = datetime.now()
	if username == "breakglass":
		deadline = created_at + timedelta(minutes=breakglass_timeout_setting[2])
	else:
		deadline = created_at + timedelta(minutes=timeout_setting[2])

	# Execute a query to insert or update the token for the user
	upsert_query = """
	INSERT INTO tokens (token, created_at, deadline, created_by)
	VALUES (%s, %s, %s, %s)
	ON CONFLICT (created_by)
	DO UPDATE SET token = EXCLUDED.token, created_at = EXCLUDED.created_at, deadline = EXCLUDED.deadline
	"""
	cursor.execute(upsert_query, (token, created_at, deadline, user[0]))

	# Commit the transaction
	connection.commit()
	cursor.close()
	disconnect(connection)

	return True

########################################################
#			PERMISSIONS
########################################################

