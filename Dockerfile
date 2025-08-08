FROM python:3.11-slim

# Install system dependencies with better error handling
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libswscale-dev \
    libavdevice-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Create a non-root user for better security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 554

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=/app/data/streams.db
ENV ONVIF_PORT=8000
ENV RTSP_PORT=554
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Make startup script executable
RUN chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"] 