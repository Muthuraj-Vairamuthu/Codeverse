# Use official Python image
FROM python:3.11-slim

# Disable pyc files and buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# CMD that runs only after environment variables (like SECRET_KEY) are available
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn myproject.wsgi:application --bind 0.0.0.0:8000"]
