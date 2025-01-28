from argon2 import PasswordHasher
from flask import request

def authenticate_user(username, password):
	# Get the username and password from the request
	username = request.headers.get('username')
	password = request.headers.get('password')

	# TODO: Check if the username and password are correct and create a token and return it

	# Check if the username and password are correct
	if username == "admin" and password == "password":
		return True

	return False

#
# Hash a password with argon2
#
def hash(pw):
	ph = PasswordHasher(time_cost=3, memory_cost=102400, parallelism=4)
	hashed_password = ph.hash(pw)
	return hashed_password