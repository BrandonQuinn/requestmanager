import psycopg2
from psycopg2 import sql

user = "postgres"
password = "postgres1234!"
host = "localhost"
port = "5432"
breakglass_password = "breakglass1234!"

#
# Create a new database called requestmanager
#
def create_database(conn, cur):
	# Create database
	cur.execute(sql.SQL("CREATE DATABASE requestmanager"))

	# Commit the changes
	conn.commit()

#
# Create a new table of users
#
def create_users_table(conn, cur):
	# Create table
	cur.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(50) UNIQUE NOT NULL,
			email VARCHAR(100) UNIQUE NOT NULL,
			password VARCHAR(100) NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			permissions INTEGER[]
		)
	''')

	# Commit the changes
	conn.commit()

#
# Create a new table of permissions with ids, names, and descriptions.
# The ids are then added to the users table to have permissions
#
def create_permissions_table(conn, cur):
	# Create table
	cur.execute('''
		CREATE TABLE IF NOT EXISTS permissions (
			id SERIAL PRIMARY KEY,
			permission_name VARCHAR(50) UNIQUE NOT NULL,
			description TEXT
		)
	''')

	# Commit the changes
	conn.commit()

#
# Create the database and tables
#
def create_database_and_tables():
	# Connect to your postgres DB
	# Connect to the default database
	conn = psycopg2.connect(
		dbname="postgres",
		user=user,
		password=password,
		host=host,
		port=port
	)

	cur = conn.cursor()

	create_database(conn, cur)
	cur.close()
	conn.close()

	conn = psycopg2.connect(
		dbname="requestmanager",
		user=user,
		password=password,
		host=host,
		port=port
	)

	create_users_table(conn, cur)
	create_permissions_table(conn, cur)
	create_default_values(conn, cur)

	# Close communication with the database
	cur.close()
	conn.close()

#
# Create all the default values for the tables.
# Such as a breakglass account with a strong password
# 
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
 
	# Insert breakglass user
	cur.execute('''
		INSERT INTO users (username, email, password, permissions)
		VALUES (%s, %s, %s, %s)
	''', ('breakglass', 'breakglass@example.com', '', '{0}'))

	# Commit the changes
	conn.commit()

	# Close communication with the database
	cur.close()
	conn.close()