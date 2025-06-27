from flask import Flask, render_template, redirect, url_for, jsonify, request
from mako.template import Template
from mako.lookup import TemplateLookup
import os, sys
import health_checks, init, create_database, auth, database

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

	# redirect to dashboard if the user is logged in
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	if token and auth.check_token(username, token):
		return redirect(url_for('dashboard'), code=302)

	template = template_lookup.get_template("index.html")
	return template.render(title="Request Manager")

#
# Return organsation html page
#
@app.route("/organisation")
def organisation():
	# redirect to install page if the database is not initialised
	if not init.is_database_initialised():
		return redirect(url_for('install'), code=302)

	# redirect to dashboard if the user is logged in
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	if not token or not auth.check_token(username, token):
		return redirect(url_for('index'), code=302)

	template = template_lookup.get_template("organisation_templates\\organisation.html")
	return template.render(title="Organisation")

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
@app.errorhandler(404)
def error_404(error):
	template = template_lookup.get_template("404.html")
	return template.render(title="404")

#
# Return the dashboard, which is the homepage for the application
#
@app.route("/dashboard")
def dashboard():

	# Get the token and check it exists 
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')
	
	# no token, problem
	if not token:
		print("Token not recieved from client when accessing dashboard.")
		return redirect(url_for('index'), code=302, 
				Response=jsonify({'message': 'Token not recieved from client', 'status': 'failure'}))

	# if not a valid token, redirect to index
	if not auth.check_token(username, token):
		return redirect(url_for('index'), code=302,
				Response=jsonify({'message': 'Invalid token', 'status': 'failure'}))

	# get the user to send to the html (help use permissions to hide elements that the user doesn't have perms to)
	# if they can't use it, why offer it? "It's like showing a very tired mason a whole cathedral" - David Mitchell 
	user_data = database.get_user_by_username(username)

	# present the dashboard
	template = template_lookup.get_template("dashboard_templates\\dashboard.html")
	return template.render(title="Dashboard", user=user_data)

#############
# Users API #
#############

#
# Return all users
#
@app.route('/api/users', methods=['GET'])
def get_users():

	# TODO: Check permissions on token

	users = database.get_all_users()

	return jsonify(users)

#
# Return currently logged in user (associated with token from cookie)
#
@app.route('/api/users/self', methods=['GET'])
def get_user_self():
	token = request.cookies.get('auth_token')

	if not token:
		return jsonify({'error': 'Authentication required'}), 401
	
	user = database.get_user_by_token(token)

	return jsonify(user)

######################
# Authentication API #
######################

@app.route('/api/authenticate', methods=['POST'])
def login():
	if request.is_json:
		data = request.get_json()
		username = data.get('username')
		password = data.get('password')

		# authenticate the user 
		try:
			token = auth.authenticate_user(username, password)
		except Exception as error:
			return jsonify({'message': str(error), 'status': 'failure'})

		# sends the token back with the username to store in a cookie
		if (token):
			return jsonify({'message': 'Login successful', 'status': 'success', 'token': token, 'user': username})
		else:
			return jsonify({'message': 'Username or password incorrect', 'status': 'failure'})
		
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

	# return if the database has been initialised
	if init.is_database_initialised():
		return jsonify({'error': 'Database already initialised'}), 500

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

	# TODO: Update checks

	# Check if the tables exist
	users_exists = health_checks.check_table_exists('users')
	permissions_exists = health_checks.check_table_exists('permissions')
	requests_exists = health_checks.check_table_exists('requests')
	tokens_exists = health_checks.check_table_exists('tokens')
	settings_exists = health_checks.check_table_exists('app_settings')
	updates_exists = health_checks.check_table_exists('updates')
	departments_exists = health_checks.check_table_exists('departments')
	global_tokens_exists = health_checks.check_table_exists('global_tokens')
	request_types_exists = health_checks.check_table_exists('request_types')
	teams_exists = health_checks.check_table_exists('teams')

	# If the tables don't exist, return an error
	if not users_exists or not permissions_exists or not requests_exists or not tokens_exists or not settings_exists or not updates_exists or not departments_exists or not global_tokens_exists or not request_types_exists or not teams_exists:
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

# ##############
# REQUESTS API #
################

#
# Get a request by its ID
#
@app.route('/api/requests/<int:request_id>', methods=['GET'])
def get_request_by_id(request_id):
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401

	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# get the request from the database
	try:
		request_data = database.get_request_by_id(request_id)
	except:
		return jsonify({'error': 'No requests found with that ID.'}), 404
	
	# check if empty
	if not request_data:
		return jsonify({'error': 'Request not found'}), 404

	# TODO: Check permissions or user role to determine how much of the request they'll see

	# get type name
	type_name = ""
	if request_data[11] != None:
		type_name = database.get_request_type_by_id(request_data[11])[1]

	# get department name
	department_name = ""
	if request_data[7] != None:
		department_name = database.get_department_by_id(request_data[7])[1]
	
	# get team name
	team_name = ""
	if request_data[8] != None:
		team_name = database.get_team_by_id(request_data[8])[1]

	# get assignee name
	assignee_name = ""
	if request_data[9] != None:
		assignee_name = database.get_user_by_id(request_data[9])[1]

	request_data = (
		request_data[0],
		request_data[1],
		request_data[2],
		request_data[3],
		request_data[4],
		request_data[5],
		request_data[6],
		department_name,
		team_name,
		assignee_name,
		request_data[10],
		type_name
	)

	return jsonify(request_data), 200

@app.route('/api/requests/new', methods=['POST'])
def new_request():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401
	
	request_title = None
	request_description = None
	request_type = None
	
	# get the data sent via POST
	if request.is_json:
		data = request.get_json()
		request_title = data.get('request-title')
		request_description = data.get('request-description')
		request_type = data.get('request-type')
		request_department = data.get('request-department')

		# check if not null or empty
		if not request_title or request_title == "":
			return jsonify({'error': 'Empty title send for new request.'}), 406
		if not request_description or request_description == "":
			return jsonify({'error': 'Empty title description for new request.'}), 406
		if not request_type or request_type == "":
			return jsonify({'error': 'Empty title type for new request.'}), 406
		if not request_department or request_type == "":
			return jsonify({'error': 'Empty title department for new request.'}), 406

	# TODO: Do other input validation (limiting length of description etc.)
	
	# check if the logged in user has permission to create a new request
	create_request_permission = auth.check_permission('create_request', token)

	# the token has the perms, create the new request
	if create_request_permission:
		# TODO: Login to determine team and other fields that are not provided
		database.add_request(username, request_title, request_description, request_type, request_department)
		return jsonify({'success': 'Request created.'}), 200
	else:
		return jsonify({'error': 'Permission denied.'}), 405
#
# Get all the requests requested by the logged in user
#
@app.route('/api/requests/user/self', methods=['GET'])
def get_requests_self():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# get what requests are needed based on filters
	page = request.args.get('page', default=1, type=int)
	count = request.args.get('count', default=10, type=int)
	sort = request.args.get('sort', default=None, type=str)

	# limit the count to something reasonable
	if count > 50:
		count = 50

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401

	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# TODO: Check permissions or user role to determine how much of the request they'll see

	# TODO: Sort the return data using the sort arg if set

	requests = database.get_requests_by_requester(username)

	return jsonify(requests), 200

#
# Get a list of all types
#
@app.route('/api/requests/types', methods=['GET'])
def get_request_types():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401

	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401
	
	# Get the list of request types from the database
	request_types = database.get_request_types()

	# Return the list of request types as JSON
	return jsonify(request_types), 200

#
# Get a list of all departments
#
@app.route('/api/requests/departments', methods=['GET'])
def get_request_departments():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401

	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401
	
	# Get the list of request types from the database
	request_types = database.get_request_departments()

	# Return the list of request types as JSON
	return jsonify(request_types), 200

# ##############
# UPDATES API  #
################ 

#
# Gets updates for a request
#
@app.route('/api/requests/<int:request_id>/updates', methods=['GET'])
def get_request_updates(request_id):
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401

	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# get the request from the database
	try:
		updates_data = database.get_updates_by_request_id(request_id)
	except:
		return jsonify({'error': 'No updates or no request found while fetching updates.'}), 404
	
	# check if empty
	if not updates_data:
		return jsonify({}), 200
	
	return jsonify(updates_data), 200

#
# Adds a new update
#
@app.route('/api/requests/<int:request_id>/updates/new', methods=['POST'])
def new_request_update(request_id):
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401
	
	update_content = None
	
	# get the data sent via POST
	if request.is_json:
		data = request.get_json()
		update_content = data.get('update-content')

		# check if not null or empty
		if not update_content or update_content == "":
			return jsonify({'error': 'Empty update content send for new update.'}), 406

	print(update_content)

	# default value for customer visible is true
	database.add_update(request_id, username, update_content, True) 
	return jsonify({'success': 'Update added.'}), 200

#
# Resolve a request by its ID
#
@app.route('/api/requests/<int:request_id>/resolve', methods=['POST'])
def resolve_request(request_id):
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	resolve_request_permission = False
	
	# check if the logged in user has permission to resolve a request
	resolve_request_permission = auth.check_permission('resolve_request', token)

	# Check if the user created the request, if so, they can resolve it
	user_data = database.get_user_by_token(token)
	request_data = database.get_request_by_id(request_id)

	if user_data[0] == request_data[1]:
		resolve_request_permission = True

	# TODO: More checks around compartmentalisation and team permissions

	# If permission to resolve, resolve the request
	if resolve_request_permission:
		try:
			database.resolve_request(request_id)
			return jsonify({'success': 'Request resolved.'}), 200
		except Exception as e:
			return jsonify({'error': str(e)}), 500
	else:
		return jsonify({'error': 'Permission denied.'}), 405

# ###################
# ORGANISATION API  #
#####################

#
# Get a list of all departments
#
@app.route('/api/departments', methods=['GET'])
def get_departments():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401
	
	# TODO: Check permissions to see which departments the user can see

	# Get the list of departments from the database
	departments = database.get_departments()
	return jsonify(departments), 200

#
# Get a list of all teams
#
@app.route('/api/teams', methods=['GET'])
def get_teams():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# TODO: Check permissions to see which departments the user can see

	# Get the list of teams from the database
	teams = database.get_teams()
	return jsonify(teams), 200

#
# Get a team by its ID
#
@app.route('/api/teams/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# TODO: Check permissions to see which teams a user can see

	# Get the list of teams from the database
	team = database.get_team_by_id(team_id)
	return jsonify(team), 200

#
# Create a new team
#
@app.route('/api/teams/new', methods=['POST'])
def new_team():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# TODO: Check permissions to see if the user can create a new team

	# get the data sent via POST
	if request.is_json:
		data = request.get_json()
		name = data.get('name')
		description = data.get('description')

		# check if not null or empty
		if not name or name == "":
			return jsonify({'error': 'Empty team name sent for new team.'}), 406
		
		if not description or name == "":
			return jsonify({'error': 'Empty team description sent for new team.'}), 406

		try:
			database.add_team(name, description)
			return jsonify({'success': 'Team added.'}), 200
		except Exception as e:
			return jsonify({'error': str(e)}), 500

	return jsonify({'error': 'Adding team failed.'}), 400

#
# Create a new department
#
@app.route('/api/departments/new', methods=['POST'])
def new_department():
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	department_name = None
	
	# TODO: Check permissions to see if the user can create a new department

	print(request.get_json())

	# get the data sent via POST
	if request.is_json:
		data = request.get_json()
		name = data.get('name')
		description = data.get('description')
		initial_team = data.get('initial_team')
		teams = data.get('teams')

		# check if not null or empty
		if not name or name == "":
			return jsonify({'error': 'Empty department name send for new department.'}), 406

		teamList = list(teams)
		database.add_department(name, description, initial_team, teamList)

		return jsonify({'success': 'Department added.'}), 200

	return jsonify({'error': 'Adding department failed.'}), 200

# ###################
# SETTINGS API      #
#####################

@app.route('/api/settings/<string:setting_name>', methods=['GET'])
def get_setting_by_name(setting_name):
	# get auth data
	token = request.cookies.get('auth_token')
	username = request.cookies.get('user')

	# check token
	if not token or not username:
		return jsonify({'error': 'Authentication required'}), 401
	if not auth.check_token(username, token):
		return jsonify({'error': 'Invalid token, required to first login'}), 401

	# Check if the user has permission to view settings

	# Get the settings from the database
	try:
		setting = database.get_setting_by_name(setting_name)
	except Exception as e:
		return jsonify({'error': str(e)}), 500
	
	return jsonify(setting), 200

#
# Start the app.
# LEAVE AT BOTTOM
#
if __name__ == "__main__":
	app.run(debug=True)