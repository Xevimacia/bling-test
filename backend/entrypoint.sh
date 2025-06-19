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
python manage.py migrate --noinput

# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME}"
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
END

# Update superuser with external_id
python manage.py update_superuser --external-id="${DJANGO_SUPERUSER_EXTERNAL_ID:-super_user_id_123}"

# Start the Django development server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000 