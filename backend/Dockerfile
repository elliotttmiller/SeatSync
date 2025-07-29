FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and Poetry in one layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && pip install --no-cache-dir poetry \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Start the app with Poetry and Uvicorn, using $PORT
CMD ["sh", "-c", "poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT"] 