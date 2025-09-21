# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Install pip tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create runtime directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chmod -R 755 /app

# Add entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Collect static at build time (safe even if none exist)
RUN python medic_query/medic_query/manage.py collectstatic --noinput || true

EXPOSE 8000

# Default command runs entrypoint which handles migrations and then starts gunicorn
CMD ["/entrypoint.sh"]
