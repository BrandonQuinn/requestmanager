#!/bin/bash

# Written for:
# Description:    Ubuntu 22.04.4 LTS
# Release:        22.04
# Codename:       jammy

# The python version needs to be 3.11 or lower - no importlib support

# Update package lists
sudo apt-get update

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Enable and start PostgreSQL service
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Install Python 3 if not present
sudo apt-get install -y python3 python3.10-venv python3-pip

sudo apt-get install libpq-dev gcc cmake

python3 -m venv venv

source venv/bin/activate

# Install Flask
pip install Flask
pip install cryptography
pip install mako
pip install argon2-cffi
pip install psycopg2

deactivate

echo "Installation complete. Please reboot, and change the postgres user password."
echo "After reboot, run the following commands to start the server:"
echo "source venv/bin/activate"
echo "flask run --host=<ip>"