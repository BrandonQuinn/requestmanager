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
		user_data = database.get_user_by_username(username)
		hashed_pw = user_data[3]

		# validate the password
		if validate_pw_hash(hashed_pw, password):
			# generate a token
			token = generate_user_token()

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
