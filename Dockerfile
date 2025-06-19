# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set environment variables for Python to avoid buffering issues in logs
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (optional, but good for common build tools)
# e.g., if you have Pillow (image processing) or other packages with C extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker's cache
# if only requirements.txt changes, it will rebuild from here
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend project into the container
COPY backend/ /app/

# Copy entrypoint script and make it executable
COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the port that Gunicorn/Django will run on
EXPOSE 8000

# Command to run the Django development server
# For production, you'd use Gunicorn or uWSGI
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
