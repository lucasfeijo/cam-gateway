# ZimaOS Troubleshooting Guide

## Common Issues and Solutions

### 1. **Container Won't Start**

**Symptoms:**
- Container shows "Exited" status
- No logs available
- Port conflicts

**Solutions:**
```bash
# Check if ports are in use
netstat -tuln | grep -E ":(8000|554|800[1-9]|8010)"

# Check container logs
docker logs cam-gateway

# Check ZimaOS logs
journalctl -u docker
```

### 2. **Permission Denied Errors**

**Symptoms:**
- "Permission denied" in logs
- Database creation fails
- File system errors

**Solutions:**
```bash
# Ensure data directory has correct permissions
chmod 755 /opt/zimaos/apps/cam-gateway/data

# Check container user
docker exec cam-gateway id
```

### 3. **FFmpeg Issues**

**Symptoms:**
- "FFmpeg is not installed" error
- Stream processing failures
- Codec errors

**Solutions:**
```bash
# Test FFmpeg in container
docker exec cam-gateway ffmpeg -version

# Check FFmpeg codecs
docker exec cam-gateway ffmpeg -codecs | grep h264
```

### 4. **Network Connectivity Issues**

**Symptoms:**
- "Connection refused" errors
- RTSP streams not accessible
- ONVIF discovery fails

**Solutions:**
```bash
# Test network connectivity from container
docker exec cam-gateway ping 192.168.1.100

# Check if RTSP ports are accessible
docker exec cam-gateway telnet 192.168.1.100 554
```

### 5. **Database Issues**

**Symptoms:**
- "Database error" in logs
- SQLite file corruption
- Permission denied on database

**Solutions:**
```bash
# Check database file
ls -la /opt/zimaos/apps/cam-gateway/data/

# Test database connectivity
docker exec cam-gateway python3 -c "
import sqlite3
conn = sqlite3.connect('/app/data/streams.db')
print('Database OK')
conn.close()
"
```

## Debugging Steps

### Step 1: Check Container Status
```bash
# Check if container is running
docker ps -a | grep cam-gateway

# Check container logs
docker logs cam-gateway
```

### Step 2: Test Container Manually
```bash
# Run container interactively for debugging
docker run -it --rm \
  -p 8000:8000 \
  -p 554:554 \
  -v /opt/zimaos/apps/cam-gateway/data:/app/data \
  feijo/cam-gateway:latest /bin/bash
```

### Step 3: Check Resource Usage
```bash
# Check memory and CPU usage
docker stats cam-gateway

# Check disk space
df -h /opt/zimaos/apps/cam-gateway/data/
```

### Step 4: Test Application Endpoints
```bash
# Test health endpoint
curl -f http://localhost:8000/health

# Test API documentation
curl -f http://localhost:8000/api/docs

# Test ONVIF endpoint
curl -f http://localhost:8000/onvif/1/device.xml
```

## ZimaOS-Specific Issues

### 1. **Port Mapping Problems**
- Ensure all required ports are mapped in ZimaOS
- Check for port conflicts with other containers
- Verify firewall settings

### 2. **Volume Mount Issues**
- Ensure `/opt/zimaos/apps/cam-gateway/data` exists
- Check volume permissions
- Verify volume is persistent

### 3. **Resource Limits**
- Increase memory limit if container crashes
- Check CPU allocation
- Monitor resource usage

### 4. **Network Configuration**
- Ensure container has network access
- Check DNS resolution
- Verify routing to camera networks

## Recovery Procedures

### Reset Container
```bash
# Stop and remove container
docker stop cam-gateway
docker rm cam-gateway

# Recreate container with proper settings
docker run -d \
  --name cam-gateway \
  --restart unless-stopped \
  -p 8000:8000 \
  -p 554:554 \
  -p 8001-8010:8001-8010 \
  -v /opt/zimaos/apps/cam-gateway/data:/app/data \
  -e DATABASE_URL=/app/data/streams.db \
  -e ONVIF_PORT=8000 \
  -e RTSP_PORT=554 \
  -e LOG_LEVEL=INFO \
  feijo/cam-gateway:latest
```

### Reset Database
```bash
# Backup current database
cp /opt/zimaos/apps/cam-gateway/data/streams.db /opt/zimaos/apps/cam-gateway/data/streams.db.backup

# Remove database to start fresh
rm /opt/zimaos/apps/cam-gateway/data/streams.db

# Restart container
docker restart cam-gateway
```

### Check ZimaOS System Logs
```bash
# Check ZimaOS container logs
journalctl -u docker -f

# Check system resources
htop
free -h
df -h
```

## Contact Information

If you continue to experience issues:

1. **Collect Debug Information:**
   ```bash
   # Save container logs
   docker logs cam-gateway > cam-gateway-logs.txt
   
   # Save system information
   docker info > docker-info.txt
   docker version > docker-version.txt
   ```

2. **Check ZimaOS Version:**
   ```bash
   cat /etc/os-release
   ```

3. **Report Issues:**
   - Include logs and system information
   - Describe exact steps to reproduce
   - Mention ZimaOS version and configuration
