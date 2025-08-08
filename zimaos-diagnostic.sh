#!/bin/bash

# ZimaOS CAM Gateway Diagnostic Script
# Run this script to diagnose container launch issues

echo "=== CAM Gateway ZimaOS Diagnostic ==="
echo "Timestamp: $(date)"
echo ""

# Check if Docker is running
echo "1. Checking Docker status..."
if systemctl is-active --quiet docker; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is not running"
    echo "  Run: sudo systemctl start docker"
    exit 1
fi

# Check if container exists
echo ""
echo "2. Checking container status..."
if docker ps -a | grep -q cam-gateway; then
    echo "✓ Container exists"
    docker ps -a | grep cam-gateway
else
    echo "✗ Container does not exist"
fi

# Check container logs
echo ""
echo "3. Checking container logs..."
if docker logs cam-gateway 2>&1 | tail -20; then
    echo "✓ Container logs retrieved"
else
    echo "✗ Could not retrieve container logs"
fi

# Check port availability
echo ""
echo "4. Checking port availability..."
for port in 8000 554 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010; do
    if netstat -tuln | grep -q ":$port "; then
        echo "✗ Port $port is in use"
    else
        echo "✓ Port $port is available"
    fi
done

# Check data directory
echo ""
echo "5. Checking data directory..."
DATA_DIR="/opt/zimaos/apps/cam-gateway/data"
if [ -d "$DATA_DIR" ]; then
    echo "✓ Data directory exists: $DATA_DIR"
    if [ -w "$DATA_DIR" ]; then
        echo "✓ Data directory is writable"
    else
        echo "✗ Data directory is not writable"
        echo "  Run: sudo chmod 755 $DATA_DIR"
    fi
else
    echo "✗ Data directory does not exist: $DATA_DIR"
    echo "  Run: sudo mkdir -p $DATA_DIR && sudo chmod 755 $DATA_DIR"
fi

# Check disk space
echo ""
echo "6. Checking disk space..."
df -h /opt/zimaos/apps/cam-gateway/data 2>/dev/null || df -h /

# Check memory usage
echo ""
echo "7. Checking memory usage..."
free -h

# Test container manually
echo ""
echo "8. Testing container startup..."
echo "Attempting to start container in test mode..."
docker run --rm -it \
    -p 8000:8000 \
    -p 554:554 \
    -v "$DATA_DIR:/app/data" \
    -e DATABASE_URL=/app/data/streams.db \
    -e ONVIF_PORT=8000 \
    -e RTSP_PORT=554 \
    -e LOG_LEVEL=INFO \
    feijo/cam-gateway:latest /app/start.sh &
TEST_PID=$!

# Wait a moment and check if it started
sleep 10
if kill -0 $TEST_PID 2>/dev/null; then
    echo "✓ Test container started successfully"
    kill $TEST_PID
else
    echo "✗ Test container failed to start"
fi

echo ""
echo "=== Diagnostic Complete ==="
echo ""
echo "If issues persist, check:"
echo "1. Container logs: docker logs cam-gateway"
echo "2. System logs: journalctl -u docker"
echo "3. Resource usage: docker stats cam-gateway"
echo "4. Network connectivity: docker exec cam-gateway ping 8.8.8.8"
