# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port 8000 for Django
EXPOSE 8000

# Run migrations, load data, and start the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata problems.json && gunicorn myproject.wsgi:application --bind 0.0.0.0:8000"]
