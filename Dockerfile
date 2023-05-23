# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y postgresql redis-server libpq-dev gcc

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .  

# Expose the FastAPI port
EXPOSE 8000

# Set environment variables for database and Redis connection
ENV DATABASE_URL=postgresql+asyncpg://postgress:password@postgres/postgres
ENV REDIS_URL=redis://redis:6379/0

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "api.entrypoints.app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
