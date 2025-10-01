FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV FEATURES_BUCKET=igdb-model-artifacts-dev

# Expose port
EXPOSE 8000

# Health check removed - Cloud Run handles health checks automatically

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
