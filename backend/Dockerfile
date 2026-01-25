# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# build-essential is often needed for compiling some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirement.txt .

# Install Python dependencies
# We use --no-cache-dir to keep image size small
RUN pip install --no-cache-dir -r requirement.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Fix for SSL/Networking in some containers
ENV HF_HUB_DISABLE_SSL_VERIFY=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
