#!/bin/bash

# CAM Gateway Startup Script for ZimaOS
# This script provides better error handling and logging

set -e

echo "=== CAM Gateway Starting ==="
echo "Timestamp: $(date)"
echo "Environment:"
echo "  DATABASE_URL: ${DATABASE_URL:-/app/data/streams.db}"
echo "  ONVIF_PORT: ${ONVIF_PORT:-8000}"
echo "  RTSP_PORT: ${RTSP_PORT:-554}"
echo "  LOG_LEVEL: ${LOG_LEVEL:-INFO}"

# Check if data directory exists and is writable
if [ ! -d "/app/data" ]; then
    echo "Creating data directory..."
    mkdir -p /app/data
fi

if [ ! -w "/app/data" ]; then
    echo "ERROR: Data directory is not writable"
    exit 1
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: FFmpeg is not installed"
    exit 1
fi

# Check if required ports are available
echo "Checking port availability..."
if ! netstat -tuln | grep -q ":8000 "; then
    echo "ERROR: Port 8000 is already in use"
    exit 1
fi

# Test database connectivity
echo "Testing database..."
python3 -c "
import sqlite3
import os
db_path = os.getenv('DATABASE_URL', '/app/data/streams.db')
try:
    conn = sqlite3.connect(db_path)
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database error: {e}')
    exit(1)
"

# Start the application
echo "Starting CAM Gateway..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level ${LOG_LEVEL:-INFO} 