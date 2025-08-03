# CAM Gateway Deployment Guide

## Overview

CAM Gateway is a Docker containerized application that converts RTSP streams to ONVIF format for integration with UniFi Protect. This guide covers deployment on various platforms including ZimaBoard with ZimaOS.

## Prerequisites

- Docker and Docker Compose installed
- Network access to RTSP cameras
- UniFi Protect NVR or Cloud Key

## Quick Start

### Option 1: From Docker Registry (Recommended)
```bash
# Pull and run directly from Docker Hub
docker run -d \
  --name cam-gateway \
  -p 8000:8000 \
  -p 554:554 \
  -p 8001-8010:8001-8010 \
  -v /path/to/data:/app/data \
  feijo/cam-gateway:latest
```

### Option 2: From Source
#### 1. Clone the Repository
```bash
git clone https://github.com/lucasfeijo/cam-gateway.git
cd cam-gateway
```

#### 2. Create Data Directory
```bash
mkdir -p data
```

#### 3. Build and Run with Docker Compose
```bash
docker-compose up -d
```

### 4. Access the Web Interface
Open your browser and navigate to:
- **Web Interface**: http://your-server-ip:8000
- **API Documentation**: http://your-server-ip:8000/api/docs

## ZimaBoard/ZimaOS Deployment

### 1. SSH into your ZimaBoard
```bash
ssh root@your-zimaboard-ip
```

### 2. Install Docker (if not already installed)
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y
```

### 3. Clone and Deploy
```bash
# Clone the repository
git clone https://github.com/lucasfeijo/cam-gateway.git
cd cam-gateway

# Create data directory
mkdir -p data

# Build and start
docker-compose up -d
```

### 4. Configure Firewall
Ensure the following ports are open:
- Port 8000: Web interface and API
- Port 554: RTSP
- Ports 8001-8010: ONVIF streams

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `/app/data/streams.db` | SQLite database path |
| `ONVIF_PORT` | `8000` | ONVIF service port |
| `RTSP_PORT` | `554` | RTSP service port |
| `LOG_LEVEL` | `INFO` | Logging level |

### Stream Configuration

Each stream requires:
- **Name**: Human-readable name for the stream
- **RTSP URL**: Full RTSP URL to the camera stream
- **Username/Password**: Optional credentials for the camera
- **ONVIF Port**: Optional custom port (auto-assigned if not specified)
- **Enabled**: Whether the stream should be active

Example stream configuration:
```json
{
  "name": "Front Door Camera",
  "rtsp_url": "rtsp://192.168.1.100:554/stream1",
  "username": "admin",
  "password": "password123",
  "enabled": true,
  "onvif_port": 8001
}
```

## UniFi Protect Integration

### 1. Add ONVIF Camera in UniFi Protect

1. Open UniFi Protect web interface
2. Go to **Settings** → **Cameras** → **Add Camera**
3. Select **ONVIF Camera**
4. Enter the camera details:
   - **Name**: Your camera name
   - **IP Address**: Your CAM Gateway server IP
   - **Port**: The ONVIF port for your stream (e.g., 8001)
   - **Username/Password**: Leave blank (handled by CAM Gateway)

### 2. ONVIF Discovery

CAM Gateway provides ONVIF endpoints for each stream:
- **Device Info**: `http://server-ip:8000/onvif/{stream_id}/device.xml`
- **Media Service**: `http://server-ip:8000/onvif/{stream_id}/media.wsdl`
- **Stream URL**: `rtsp://server-ip:{onvif_port}/stream`

### 3. Stream Health Monitoring

Monitor stream health through:
- Web interface status indicators
- API endpoint: `GET /api/streams/{id}/status`
- Logs: `docker-compose logs cam-gateway`

## Troubleshooting

### Common Issues

1. **Stream not starting**
   - Check RTSP URL is accessible
   - Verify camera credentials
   - Check firewall settings

2. **ONVIF discovery fails**
   - Ensure ONVIF port is open
   - Check stream is enabled
   - Verify server IP is correct

3. **High CPU usage**
   - Consider hardware acceleration
   - Reduce stream quality
   - Monitor system resources

### Logs and Debugging

```bash
# View application logs
docker-compose logs cam-gateway

# Follow logs in real-time
docker-compose logs -f cam-gateway

# Access container shell
docker-compose exec cam-gateway bash

# Check stream processes
docker-compose exec cam-gateway ps aux | grep ffmpeg
```

### Performance Optimization

1. **Hardware Acceleration**
   - Use GPU acceleration if available
   - Consider dedicated hardware for multiple streams

2. **Network Optimization**
   - Use wired connections for cameras
   - Ensure adequate bandwidth
   - Monitor network latency

3. **Resource Management**
   - Limit concurrent streams based on hardware
   - Monitor memory and CPU usage
   - Adjust stream quality as needed

## Security Considerations

1. **Network Security**
   - Use VLANs to isolate camera traffic
   - Implement proper firewall rules
   - Use strong passwords for cameras

2. **Access Control**
   - Restrict web interface access
   - Use HTTPS in production
   - Implement authentication if needed

3. **Data Protection**
   - Regular backups of configuration
   - Secure storage of credentials
   - Monitor for unauthorized access

## Backup and Recovery

### Backup Configuration
```bash
# Backup database
docker-compose exec cam-gateway cp /app/data/streams.db /app/data/streams.db.backup

# Backup entire data directory
tar -czf cam-gateway-backup-$(date +%Y%m%d).tar.gz data/
```

### Restore Configuration
```bash
# Restore database
docker-compose exec cam-gateway cp /app/data/streams.db.backup /app/data/streams.db

# Restart service
docker-compose restart cam-gateway
```

## Updates and Maintenance

### Updating CAM Gateway
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Regular Maintenance
- Monitor disk space usage
- Check for application updates
- Review logs for errors
- Test stream connectivity

## Support

For issues and support:
1. Check the troubleshooting section
2. Review application logs
3. Verify network connectivity
4. Test with a simple RTSP stream first

## License

This project is licensed under the MIT License. 