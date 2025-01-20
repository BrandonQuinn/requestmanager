from flask import Flask, render_template_string, jsonify, request
from mako.template import Template
from mako.lookup import TemplateLookup
import model
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__name__), '..',)))
import init

app = Flask(__name__)

# Configure Mako template lookup
template_lookup = TemplateLookup(directories=['templates'])

# ###########
# UI ROUTES #
#############

@app.route("/")
def index():
	template = template_lookup.get_template("index.html")
	return template.render(title="Request")

# Return install html page
@app.route("/install")
def install():
	if (init.is_database_initialised()):
		return request.redirect("/404")

	template = template_lookup.get_template("install.html")
	return template.render(title="Request")

# Default 404 page
@app.route("/404")
def error_404():
	template = template_lookup.get_template("404.html")
	return template.render(title="404")

#############
# Users API #
#############

@app.route('/api/users', methods=['GET'])
def get_users():
	users = model.get_users()
	return jsonify(users)

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
# Return true if the database is set up, false if not. 
#
@app.route('/api/database/checkinstall', methods=['GET'])
def database_check_install():
	installed = init.is_database_initialised()
	return jsonify(installed)

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

	print("USERNAME USERNAME USERNAME " + new_db_username)

	# if it's already initialised, return true and don't create anything
	if not initialised:
		init.init_database(new_db_username, new_db_password)
	elif initialised:
		return 'NULL'

	initialised = init.is_database_initialised()
	return '{"success": "True"}'

'''@app.route('/api/database/checkauth', methods=['POST'])
def login():
	username = request.form.get('username')
	password = request.form.get('password')
	
	# Dummy authentication logic
	if username == 'admin' and password == 'password':
		return jsonify({'message': 'Login successful', 'status': 'success'})
	else:
		return jsonify({'message': 'Invalid credentials', 'status': 'failure'})'''

######################
# Authentication API #
######################
'''
@app.route('/api/login', methods=['POST'])
def login():
	username = request.form.get('username')
	password = request.form.get('password')
	
	# Dummy authentication logic
	if username == 'admin' and password == 'password':
		return jsonify({'message': 'Login successful', 'status': 'success'})
	else:
		return jsonify({'message': 'Invalid credentials', 'status': 'failure'})
'''

if __name__ == "__main__":
	app.run(debug=True)