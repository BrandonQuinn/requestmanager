import psycopg2
from psycopg2 import sql
from argon2 import PasswordHasher
import json
import db_util
import os

host = "localhost"
port = "5432"

## NOTE: If you add a table here, you need to add it in the checks in init.py and the health checks api

#
# Create a new database called requestmanager
#
def create_database():
    creds = db_util.read_credentials('temp_root_creds.json')

    conn = psycopg2.connect(
        dbname="postgres",
        user=creds['username'],
        password=creds['password'],
        host=host,
        port=port
    )

    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql.SQL("CREATE DATABASE requestmanager"))
    
    cur.close()
    conn.close()

#
# Set the temporary username and password
#
def set_temp_db_user(db_username, db_password):

    # Save the credentials to a file
    save_credentials_to_file(db_username, db_password, 'temp_root_creds.json')

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
            permissions INTEGER[] DEFAULT '{}',
            level INTEGER DEFAULT 0,
            end_user BOOLEAN DEFAULT TRUE,
            firstname VARCHAR(128),
            lastname VARCHAR(128)
        )
    ''')
    conn.commit()

#
# Create a new table of departments
#
def create_department_table(conn, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR (32),
            teams INTEGER[] DEFAULT '{}',
            description VARCHAR(256),
            initial_assignment INTEGER
        )
    ''')
    conn.commit()

#
# Create a new table of teams
#
def create_team_table(conn, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR (32),
            users INTEGER[],
            description VARCHAR(256)
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
            team_category INTEGER,
            assigned_to_team INTEGER,
            assigned_to_user INTEGER,
            escalation_level INTEGER,
            type INTEGER,
            resolved BOOLEAN DEFAULT FALSE,
            resolved_at TIMESTAMP
        )
    ''')
    conn.commit()

#
# Create a table for storing text updates to requests
#
def create_updates_table(conn, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS updates (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            made_by INTEGER NOT NULL,
            request_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            customer_visible BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()

#
# Create a new table all updates
#
def create_request_udpates_table(conn, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS request_updates (
            id SERIAL PRIMARY KEY,
            update_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            made_by INTEGER NOT NULL,
            associated_request INTEGER NOT NULL
        )
    ''')
    conn.commit()

#
# Create a new table of users
#
def create_request_type_table(conn, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS request_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR (32)
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
            created_by SERIAL UNIQUE NOT NULL
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
            deadline TIMESTAMP NOT NULL,
            created_by SERIAL UNIQUE NOT NULL
        )
    ''')
    conn.commit()

#
# Create the global settings tables for the application
#
def create_settings_table(conn, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
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
    
    creds = db_util.read_credentials('temp_root_creds.json')

    # Connect to the requestmanager database to create the tables and values
    conn = psycopg2.connect(
        dbname="requestmanager",
        user=creds['username'],
        password=creds['password'],
        host=host,
        port=port
    )

    cur = conn.cursor()

    # Create a new user with permissions on the requestmanager database and start using it
    create_db_user(new_db_username, new_db_password, conn, cur)

    # close the connection via postgres user
    cur.close()
    conn.close()

    # delete the tmp creds file
    os.remove('temp_root_creds.json')

    # open a new connection with the new user
    creds = db_util.read_credentials()

    conn = psycopg2.connect(
        dbname="requestmanager",
        user=creds['username'],
        password=creds['password'],
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
    create_department_table(conn, cur)
    create_team_table(conn, cur)
    create_request_type_table(conn, cur)
    create_request_udpates_table(conn, cur)
    create_updates_table(conn, cur)
    
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
    # Insert default permissions
    cur.execute('''
        INSERT INTO permissions (id, permission_name, description)
        VALUES (%s, %s, %s)
    ''', (0, 'breakglass', 'Breakglass perm with complete unrestricted access.'))

    #
    # PERMISSIONS
    #

    # Create a permission for allowing request creation
    cur.execute('''
        INSERT INTO permissions (id, permission_name, description)
        VALUES (%s, %s, %s)
    ''', (1, 'create_request', 'Permission to allow creating a new request.'))

    # Create a permission for allowing request creation
    cur.execute('''
        INSERT INTO permissions (id, permission_name, description)
        VALUES (%s, %s, %s)
    ''', (2, 'resolve_request', 'Permission to allow resolving.'))

    # Create a permission for allowing request creation
    cur.execute('''
        INSERT INTO permissions (id, permission_name, description)
        VALUES (%s, %s, %s)
    ''', (3, 'create_user', 'Permission to allow creating a new user.'))

    # Create a permission for allowing request creation
    cur.execute('''
        INSERT INTO permissions (id, permission_name, description)
        VALUES (%s, %s, %s)
    ''', (4, 'delete_user', 'Permission to allow deleting a new user.'))

    #
    # SETTINGS
    #

    # Create a setting to tell if the breakglass account is enabled
    cur.execute('''
        INSERT INTO app_settings (id, setting_name, value, description)
        VALUES (%s, %s, %s, %s)
    ''', (0, 'breakglass_enabled', 1, '1 If the breakglass account is enabled. Enabled by default on a fresh install.'))

    # Create a setting to tell if the breakglass account has been set
    cur.execute('''
        INSERT INTO app_settings (id, setting_name, value, description)
        VALUES (%s, %s, %s, %s)
    ''', (1, 'breakglass_set', 0, '1 If the breakglass account has been set ever. The breakglass account can only ever be created once. Helps prevent it being recreated via the api if somehow removed.'))

    # Create a setting for the timeout for a user login session (how long their session token lasts)
    cur.execute('''
        INSERT INTO app_settings (id, setting_name, value, description)
        VALUES (%s, %s, %s, %s)
    ''', (2, 'user_session_timeout', 30, 'How long a user session token will last before requiring the user to login again. In Minutes.'))

    # Create a setting for the timeout for a breakglass session
    cur.execute('''
        INSERT INTO app_settings (id, setting_name, value, description)
        VALUES (%s, %s, %s, %s)
    ''', (3, 'breakglass_session_timeout', 10, 'How long a breakglass account session token lasts. In Minutes.'))

    # Create a setting for the timeout for a breakglass session
    cur.execute('''
        INSERT INTO app_settings (id, setting_name, value, description)
        VALUES (%s, %s, %s, %s)
    ''', (4, 'user_password_min_length', 16, 'Minimum length of a user password. This is used to enforce strong passwords.'))

    # Commit the changes
    conn.commit()

#
# Create the user that will have permissions on the requestmanager database.
#
def create_db_user(new_username, new_password, conn, cur):
    conn.autocommit = True
    cur = conn.cursor()

    # Create a new user
    cur.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(new_username)), [new_password])
    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE requestmanager TO {}").format(sql.Identifier(new_username)))
    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON SCHEMA public TO {}").format(sql.Identifier(new_username)))
    cur.execute(sql.SQL("ALTER DATABASE requestmanager OWNER TO {}").format(sql.Identifier(new_username)))

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