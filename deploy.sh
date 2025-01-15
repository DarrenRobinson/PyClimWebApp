#!/usr/bin/env bash
set -e

# Deploy the PyClim web app using nginx and Streamlit
# Usage:
# sudo bash -x deploy.sh

# Options
app_dir="/opt/pyclim"
venv_dir="$sort_dir/venv"
pip="$venv_dir/bin/pip"
python_version="python3.12"
python="$venv_dir/bin/python"

# Create Python virtual environment
apt update -qq
apt install --upgrade --yes -qq "$python_version" "$python_version-venv"
python3 -m venv "$venv_dir"

# Install dependencies
$pip install --quiet --upgrade -r requirements.txt
cp --recursive * "app_dir/"

# Install Streamlit service
cp --verbose config/streamlit.service /etc/systemd/system/streamlit.service
systemctl daemon-reload

# Install web reverse proxy server
# Install nginx
# https://nginx.org/en/docs/install.html
apt install --yes -qq nginx
nginx -version

# Configure web server
rm -f /etc/nginx/sites-enabled/default
cp config/nginx.conf /etc/nginx/sites-available/streamlit.conf
# Enable the site by creating a symbolic link
ln --symbolic --force /etc/nginx/sites-available/streamlit.conf /etc/nginx/sites-enabled/streamlit.conf
systemctl reload nginx.service
