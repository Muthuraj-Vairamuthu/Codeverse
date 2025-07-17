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

# Ensure /tmp is writable for SQLite database
RUN mkdir -p /tmp && chmod 777 /tmp

# Expose port
EXPOSE 8000

# CMD to start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]