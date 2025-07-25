from argon2 import PasswordHasher
from flask import request
import database
import secrets
import datetime

#
# Takes the username and password - checks the hash
# returns a token
#
def authenticate_user(username, password):
	token = None

	try:
		# get user data from database and then hashed password 
		user_data = database.get_user_by_username(username)
		hashed_pw = user_data[3]

		# validate the password
		if validate_pw_hash(hashed_pw, password):
			# generate a token
			token = generate_user_token(username)

			# save the token to the database (will automatilly set times and deadlines)
			database.save_user_token(username, token)
			
	except Exception as error:
		raise Exception(error)

	return token

#
# Generates a random token for the user and saves it to the database
#
def generate_user_token(username):
	token = secrets.token_hex(32)
	return token

#
# Checks if the token is valid (in the database)
#
def check_token(username, token):

	# if no username or token is provided, return false
	if not username or not token:
		return False
	
	# get the full token data out of the database and check if anything is returned
	try:
		token_data = database.get_token(token)

		# Get user by username sent from client
		user_data = database.get_user_by_username(username)

		# nothing returned, no token exists
		if not token_data:
			return False

		# check if the person who created the token is the person claiming to be logged in (via cookie)
		if not token_data[4] == user_data[0]:
			return False

		# check if the deadline is less than the current time
		if token_data[3] < datetime.datetime.now():
			return False
		
	except Exception as error:
		print(f"Error while checking token: {error}. It may not exist or is invalid. Or there was a database error retrieving it.")
		return False

	return True

#
# Hash a password with argon2
#
def hash(pw):
	ph = PasswordHasher(time_cost=3, memory_cost=102400, parallelism=4)
	hashed_password = ph.hash(pw)
	return hashed_password

#
# Check paramters if they match to validate password
#
def validate_pw_hash(hashed_pw, plaintext_pw):
	ph = PasswordHasher(time_cost=3, memory_cost=102400, parallelism=4)
	try:
		return ph.verify(hashed_pw, plaintext_pw)
	except:
		return False

#
# Take the token and specified permissions and check the token has the permissions.
# Return True is that's the case.
#
def check_permission(perm_str, token):
	# TODO: Will need logic to determine if the token is a global token

	# will need a few things, the token, the user and the permission to match everything up
	try:
		perm_data = database.get_permission_by_name(perm_str)
		
		# permission not found
		if not perm_data:
			print("Error while checking permission, no permission exists: " + perm_str)
			raise Exception("Error while checking permission, no permission exists: " + perm_str)
		
		# get token data
		token_data = database.get_token(token)

		# token not found
		if not token_data:
			print("No token found while checking permissions: " + token)
			raise Exception("Error, no token found in database while checking permissions")

		# get the user using the id associated with the token
		user_data = database.get_user_by_id(token_data[4])
		
		# user not found
		if not user_data:
			print("User not found in database while checking permssions, user id: " + token[4])
			raise Exception("User not found in database while checking permssions, user id: " + token[4])
		
		# get the array of permissions from the user data
		user_permissions = user_data[5]

		# get the id of the permission we need
		permission_id = perm_data[0]

		# Does the list of user permissions contain the required permission, or is the user a global admin
		for p_id in user_permissions:
			if p_id is permission_id or p_id == 0:
				return True
			
		return False

	except Exception as error:
		print(error)
		raise Exception (error)

