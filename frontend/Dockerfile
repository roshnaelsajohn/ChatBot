# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements for compatibility (or create a separate frontend one)
# Since frontend imports requests and streamlit, we need to ensure they are installed
# We can create a mini requirements.txt for frontend or just install inline
RUN pip install --no-cache-dir streamlit requests

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Set Streamlit config
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "streamlit_app.py"]
