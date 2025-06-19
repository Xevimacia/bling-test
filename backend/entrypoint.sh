#!/bin/sh
set -e

# Wait for the database to be ready
until python manage.py migrate --check; do
  echo "Waiting for database to be ready..."
  sleep 2
  # Try to run migrations (will do nothing if up to date)
  python manage.py migrate
  sleep 1
  # Check again
  python manage.py migrate --check && break
  sleep 2
  echo "Retrying..."
done

# Run migrations (safe to run even if already applied)
echo "Applying migrations (if needed)..."
python manage.py migrate

# Start the Django development server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000 