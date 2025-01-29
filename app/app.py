from flask import Flask, render_template, redirect, url_for, jsonify, request
from mako.template import Template
from mako.lookup import TemplateLookup
import database
import os, sys
import health_checks
import init
import create_database

app = Flask(__name__)

# Configure Mako template  lookup
template_lookup = TemplateLookup(directories=['templates'])

# ###########
# UI ROUTES #
#############

#
# Return the index page
#
@app.route("/")
def index():
	# redirect to install page if the database is not initialised
	if not init.is_database_initialised():
		return redirect(url_for('install'), code=302)

	template = template_lookup.get_template("index.html")
	return template.render(title="Request Manager")

#
# Return install html page
#
@app.route("/install")
def install():
	# redirect to home page if the database is already initialised
	if init.is_database_initialised():
		return redirect(url_for('index'), code=302)

	template = template_lookup.get_template("install.html")
	return template.render(title="Install")

#
# Default 404 page
#
@app.route("/404")
def error_404():
	template = template_lookup.get_template("404.html")
	return template.render(title="404")

#############
# Users API #
#############

#
# Return all users
#
@app.route('/api/users', methods=['GET'])
def get_users():
	users = database.get_all_users()
	return jsonify(users)

######################
# Authentication API #
######################

@app.route('/api/authenticate', methods=['POST'])
def login():
	if request.is_json:
		data = request.get_json()
		username = data.get('username')
		password = data.get('password')
	
		# Dummy authentication logic
		if username == 'admin' and password == 'password':
			return jsonify({'message': 'Login successful', 'status': 'success'})
		else:
			return jsonify({'message': 'Invalid credentials', 'status': 'failure'})
		
	return jsonify({'message': 'Invalid request', 'status': 'failure'})

################
# Database API #
################

#
# Return nothing
#
@app.route('/api/database/', methods=['GET'])
def database_api():
	return jsonify("database api")

#
# Used to send the root postgres username and password initially for database creation
#
@app.route('/api/database/temp_db_user', methods=['POST'])
def temp_db_user():
	if request.is_json:
		data = request.get_json()
		db_username = data.get('db_username')
		db_password = data.get('db_password')

		if not db_username or not db_password:
			return jsonify({'error': 'Username and password are required'}), 400

		# TODO: test the credentials, if it fails, return error code

		# set the password
		try:
			create_database.set_temp_db_user(db_username, db_password)
			return jsonify({'success': 'Temporary database user set successfully'}), 200
		except Exception as e:
			return jsonify({'error': str(e)}), 500
	else:
		return jsonify({'error': 'Invalid request format'}), 400

#
# Set the breakglass account
#
@app.route('/api/database/breakglass', methods=['POST'])
def set_breakglass():
	if not init.is_database_initialised():
		return jsonify({'error': 'Database not initialised'}), 400
	
	# ############################################################## WARNING ###########################################################################
	# Stops the ability to set it ever again if it has EVER been set in the past. If the entry is lost in the database, too bad. 
	# Manual intervention required via database user or reinstall. 
	# Helps prevent the unlikey but possible scenario where the breakglass account can be reset via the API which is a major security vulnerability.
	# !!! The entire security of the application depends on this check. !!!
	####################################################################################################################################################
	if database.check_breakglass_account_is_set():
		return jsonify({'error': 'Breakglass account already set'}), 400

	if request.is_json:
		data = request.get_json()
		password = data.get('breakglass-password')

		try:
			database.create_breakglass_account(password)
			return jsonify({'success': 'Breakglass account set successfully'}), 200
		except Exception as e:
			return jsonify({'error': str(e)}), 500
	else:
		return jsonify({'error': 'Invalid request format'}), 400

#
# Return true if the database is set up, false if not. 
#
@app.route('/api/database/checkinstall', methods=['GET'])
def database_check_install():
	installed = init.is_database_initialised()

	if installed:
		return jsonify({'installed': True}), 200
	
	return jsonify({'installed': False}), 500

#
# Conduct a details health check
#
@app.route('/api/database/health', methods=['GET'])
def database_health():
	# Check if the database is initialised
	initialised = init.is_database_initialised()

	# If the database is not initialised, return an error
	if not initialised:
		return jsonify({'error': 'Database not initialised'}), 500

	# Check if the tables exist
	users_exists = health_checks.check_table_exists('users')
	permissions_exists = health_checks.check_table_exists('permissions')
	requests_exists = health_checks.check_table_exists('requests')
	tokens_exists = health_checks.check_table_exists('tokens')
	settings_exists = health_checks.check_table_exists('settings')

	# If the tables don't exist, return an error
	if not users_exists or not permissions_exists or not requests_exists or not tokens_exists or not settings_exists:
		return jsonify({'error': 'One or more tables do not exist'}), 500

	# If everything is fine, return a success message
	return jsonify({'success': 'Database is healthy'}), 200

#
# Create a new user in the database
# 
@app.route('/api/database/create_user', methods=['POST'])
def create_user():
	if not init.is_database_initialised():
		return jsonify({'error': 'Database not initialised'}), 400

	if request.is_json:
		data = request.get_json()
		username = data.get('username')
		password = data.get('password')

		if not username or not password:
			return jsonify({'error': 'Username and password are required'}), 400

		try:
			database.create_user(username, password)
			return jsonify({'success': 'User created successfully'}), 201
		except Exception as e:
			return jsonify({'error': str(e)}), 500
	else:
		return jsonify({'error': 'Invalid request format'}), 400

#
# Create the database and tables
#
@app.route('/api/database/initialise', methods=['POST'])
def init_database():
	initialised = init.is_database_initialised()

	new_db_username = None
	new_db_password = None

	if request.is_json:
		data = request.get_json()
		new_db_username = data.get('new_db_username')
		new_db_password = data.get('new_db_password')

	# if it's already initialised, return true and don't create anything
	if not initialised:
		init.init_database(new_db_username, new_db_password)
	elif initialised:
		return jsonify({'error': 'Database already initialised'}), 500
	
	initialised = init.is_database_initialised()
	return jsonify({'success': 'Database created successfully'}), 201

if __name__ == "__main__":
	app.run(debug=True)