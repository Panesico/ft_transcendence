#!/bin/sh

sleep 3

# Define paths
PROJECT_DIR="/usr/src/app/transcendence"
SETTINGS_FILE="$PROJECT_DIR/settings.py"

# Check if Django project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
  # Create a new Django project with name 'transcendence'
  echo "Django project directory not found. Creating project..."
  django-admin startproject transcendence /usr/src/app
  sleep 2
else
  echo "Django project already exists."
fi

echo "Checking for STATIC_ROOT in $SETTINGS_FILE..."
if ! grep -q "STATIC_ROOT = '/usr/src/static/'" "$SETTINGS_FILE"; then
    # Append STATIC_ROOT after STATIC_URL
    echo "Adding STATIC_ROOT to settings.py..."
    sed -i "/STATIC_URL = 'static\/'/a STATIC_ROOT = '\/usr\/src\/static\/'" "$SETTINGS_FILE"
else
    echo "STATIC_ROOT is already present in $SETTINGS_FILE."
fi

# Collect static files and apply migrations
echo "Collecting static files..."
python manage.py collectstatic --noinput
# sleep 1
echo "Applying migrations..."
python manage.py migrate

# sleep 1

echo "Django initialised successfully. Executing "$@""
exec "$@" 
