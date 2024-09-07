# Base image
FROM python:3.10

# Working directory
WORKDIR /Mardex

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/Mardex/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Create virtual environment
RUN python -m venv $VIRTUAL_ENV

# Install Python dependencies
COPY requirements.txt /Mardex/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create and set permissions for staticfiles folder
RUN mkdir -p /Mardex/staticfiles
RUN chmod 755 /Mardex/staticfiles

# Copy project files
COPY . /Mardex/

# Collect static files
RUN python manage.py collectstatic --noinput

# Django settings
ENV DJANGO_SETTINGS_MODULE=Mardex_1.settings

# Expose port
EXPOSE 8001

# Run migrations and start Daphne server
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8001 Mardex_1.asgi:application"]
