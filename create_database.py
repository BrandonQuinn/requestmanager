import psycopg2
from psycopg2 import sql
from argon2 import PasswordHasher
import json

user = "postgres"
password = "postgres1234!"
host = "localhost"
port = "5432"
breakglass_password = "breakglass1234!"

## NOTE: If you add a table here, you need to add it in the checks in init.py

#
# Create a new database called requestmanager
#
def create_database():
	conn = psycopg2.connect(
		dbname=user,
		user=user,
		password=password,
		host=host,
		port=port
	)

	conn.autocommit = True
	cur = conn.cursor()
	cur.execute(sql.SQL("CREATE DATABASE requestmanager"))
	
	cur.close()
	conn.close()

#
# Create a new table of users
#
def create_users_table(conn, cur):
	cur.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(50) UNIQUE NOT NULL,
			email VARCHAR(100) UNIQUE NOT NULL,
			password VARCHAR(256) NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			permissions INTEGER[],
			team INTEGER[],
			level INTEGER DEFAULT 0
		)
	''')
	conn.commit()

#
# Create a new table of permissions with ids, names, and descriptions.
# The ids are then added to the users table to have permissions
#
def create_permissions_table(conn, cur):
	cur.execute('''
		CREATE TABLE IF NOT EXISTS permissions (
			id SERIAL PRIMARY KEY,
			permission_name VARCHAR(50) UNIQUE NOT NULL,
			description TEXT
		)
	''')
	conn.commit()

#
# Create a new table of requests
#
def create_requests_table(conn, cur):
	cur.execute('''
		CREATE TABLE IF NOT EXISTS requests (
			id SERIAL PRIMARY KEY,
			requester SERIAL NOT NULL,
			requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			priority INTEGER,
			outage BOOLEAN,
			title VARCHAR(256) NOT NULL,
			description TEXT,
			team_category SERIAL,
			assigned_to_team SERIAL,
			assigned_to_user SERIAL,
			escalation_level INTEGER
		)
	''')
	conn.commit()

#
# Create a new table of tokens associated with users
#
def create_user_tokens_table(conn, cur):
	cur.execute('''
		CREATE TABLE IF NOT EXISTS tokens (
			id SERIAL PRIMARY KEY,
			token VARCHAR(256) UNIQUE NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			deadline TIMESTAMP,
			created_by SERIAL NOT NULL
		)
	''')
	conn.commit()

#
# Create a table of global tokens that can be used by anyone who has the token. i.e. you don't need to authenticate
#
def create_global_tokens_table(conn, cur):
	cur.execute('''
		CREATE TABLE IF NOT EXISTS global_tokens (
			id SERIAL PRIMARY KEY,
			token VARCHAR(256) UNIQUE NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			deadline TIMESTAMP NOT NULL
		)
	''')
	conn.commit()

def create_settings_table(conn, cur):
	cur.execute('''
		CREATE TABLE IF NOT EXISTS settings (
			id SERIAL PRIMARY KEY,
			setting_name VARCHAR(50) UNIQUE NOT NULL,
			value INTEGER NOT NULL,
			description TEXT
		)
	''')
	conn.commit()

#
# Create the database and tables
#
def create_database_and_tables(new_db_username, new_db_password):
	# Create the requestmanager database
	create_database()

	# Create a new user with permissions on the requestmanager database
	create_db_user(new_db_username, new_db_password)

	# Connect to the requestmanager database to create the tables and values
	conn = psycopg2.connect(
		dbname="requestmanager",
		user=user,
		password=password,
		host=host,
		port=port
	)

	cur = conn.cursor()

	# Create the tables
	create_users_table(conn, cur)
	create_permissions_table(conn, cur)
	create_requests_table(conn, cur)
	create_user_tokens_table(conn, cur)
	create_global_tokens_table(conn, cur)
	create_settings_table(conn, cur)

	# Create default values
	create_default_values(conn, cur)

	# Close communication with the database
	cur.close()
	conn.close()

#
# Create all the default values for the tables.
# Such as a breakglass account with a strong password
#
def create_default_values(conn, cur):
	# Connect to the requestmanager database
	conn = psycopg2.connect(
		dbname="requestmanager",
		user=user,
		password=password,
		host=host,
		port=port
	)

	cur = conn.cursor()
 
	# Insert default permissions
	cur.execute('''
		INSERT INTO permissions (id, permission_name, description)
		VALUES (%s, %s, %s)
	''', (0, 'breakglass', 'Breakglass perm with complete unrestricted access.'))

	# Create a settings to tell if the breakglass account is enabled
	cur.execute('''
		INSERT INTO settings (id, setting_name, value, description)
		VALUES (%s, %s, %s, %s)
	''', (0, 'breakglass_enabled', 1, '1 If the breakglass account is enabled. Enabled by default on a fresh install.'))

	# Create a settings to tell if the breakglass account has been set
	cur.execute('''
		INSERT INTO settings (id, setting_name, value, description)
		VALUES (%s, %s, %s, %s)
	''', (0, 'breakglass_set', 0, '1 If the breakglass account has been set ever. The breakglass account can only ever be created once. Helps prevent it being recreated via the api if somehow removed.'))

	# Commit the changes
	conn.commit()

	# Close communication with the database
	cur.close()
	conn.close()
#
# Create the user that will have permissions on the requestmanager database.
#
def create_db_user(new_username, new_password):
	conn = psycopg2.connect(
		dbname=user,
		user=user,
		password=password,
		host=host,
		port=port
	)

	conn.autocommit = True
	cur = conn.cursor()

	# Create a new user
	new_user = new_username
	new_password = new_password
	cur.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(new_user)), [new_password])

	# Grant read and write permissions on the requestmanager database
	cur.execute(sql.SQL("GRANT CONNECT ON DATABASE requestmanager TO {}").format(sql.Identifier(new_user)))
	cur.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(new_user)))
	cur.execute(sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {}").format(sql.Identifier(new_user)))
	cur.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {}").format(sql.Identifier(new_user)))

	# Close communication with the database
	cur.close()
	conn.close()

	# Save the credentials to a file
	save_credentials_to_file(new_username, new_password)

#
# Save the credentials to a file.
#
def save_credentials_to_file(username, password, filename='db_credentials.json'):
	credentials = {
		"username": username,
		"password": password
	}
	with open(filename, 'w') as file:
		json.dump(credentials, file, indent=4)