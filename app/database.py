import psycopg2
from flask import jsonify
import json
import db_util 

#
# Get all users from the database
#
def get_all_users():
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
			connection.close()

#
# Add a new user to the database
#
def add_user(username, email, password, permissions, team, level):
	credentials = db_util.read_credentials()

	# TODO: check format of the inputs will be valid for the database

	try:
		# Connect to your postgres DB
		connection = psycopg2.connect(
			dbname="requestmanager",
			user=credentials['username'],
			password=credentials['password'],
			host="localhost",
			port=5432
		)

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
			connection.close()