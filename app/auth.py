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
	# get the full token data out of the database and check if anything is returned
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
	
	return True

#
# Hash a password with argon2
#
def hash(pw):
	ph = PasswordHasher(time_cost=3, memory_cost=102400, parallelism=4)
	hashed_password = ph.hash(pw)
	return hashed_password

#
# Check paramters if they match
#
def validate_pw_hash(hashed_pw, plaintext_pw):
	ph = PasswordHasher(time_cost=3, memory_cost=102400, parallelism=4)
	try:
		return ph.verify(hashed_pw, plaintext_pw)
	except:
		return False
