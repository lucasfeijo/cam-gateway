# CAM Gateway - RTSP to ONVIF Proxy

A Docker containerized application that registers RTSP streams from your network and proxies them to ONVIF format for integration with UniFi Protect.

## Requirements

### Functional Requirements
- **CRUD Operations**: Register, view, update, delete RTSP stream configurations
- **RTSP Proxy**: Convert RTSP streams to ONVIF format
- **Multiple Streams**: Handle multiple ONVIF endpoints on the same server
- **UniFi Protect Integration**: Generate ONVIF streams compatible with UniFi Protect
- **Docker Deployment**: Containerized for ZimaBoard/ZimaOS deployment

### Technical Requirements
- Python 3.9+
- FastAPI for REST API
- FFmpeg for stream processing
- ONVIF server implementation
- SQLite for data persistence
- Docker containerization

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RTSP Camera   │───▶│  CAM Gateway    │───▶│  UniFi Protect  │
│   (Network)     │    │  (ONVIF Proxy)  │    │   (NVR)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │  (Stream Config)│
                       └─────────────────┘
```

## Features

- **Stream Management**: Add, edit, delete RTSP stream configurations
- **ONVIF Discovery**: Automatic ONVIF device discovery
- **Stream Health Monitoring**: Monitor stream status and health
- **REST API**: Full CRUD API for stream management
- **Web Interface**: Simple web UI for stream management
- **Docker Ready**: Pre-configured for ZimaBoard deployment

## API Endpoints

- `GET /api/streams` - List all registered streams
- `POST /api/streams` - Register new RTSP stream
- `GET /api/streams/{id}` - Get stream details
- `PUT /api/streams/{id}` - Update stream configuration
- `DELETE /api/streams/{id}` - Delete stream
- `GET /api/streams/{id}/status` - Get stream health status

## ONVIF Endpoints

Each registered stream will be available as an ONVIF device at:
- `http://{server_ip}:8000/onvif/{stream_id}/device.xml`
- `http://{server_ip}:8000/onvif/{stream_id}/media.wsdl`

## Deployment

### Docker Deployment

#### From Registry (Recommended)
```bash
docker run -d \
  --name cam-gateway \
  -p 8000:8000 \
  -p 554:554 \
  -p 8001-8010:8001-8010 \
  -v /path/to/config:/app/data \
  feijo/cam-gateway:latest
```

#### From Source
```bash
docker build -t cam-gateway .
docker run -d \
  --name cam-gateway \
  -p 8000:8000 \
  -p 554:554 \
  -v /path/to/config:/app/data \
  cam-gateway
```

### ZimaBoard/ZimaOS
1. Build the Docker image
2. Deploy to ZimaBoard
3. Configure UniFi Protect to discover ONVIF devices
4. Add discovered streams to UniFi Protect

## Configuration

### Environment Variables
- `DATABASE_URL`: SQLite database path (default: `/app/data/streams.db`)
- `ONVIF_PORT`: ONVIF service port (default: 8000)
- `RTSP_PORT`: RTSP service port (default: 554)
- `LOG_LEVEL`: Logging level (default: INFO)

### Stream Configuration
```json
{
  "name": "Front Door Camera",
  "rtsp_url": "rtsp://192.168.1.100:554/stream1",
  "username": "admin",
  "password": "password",
  "enabled": true,
  "onvif_port": 8001
}
```

## Development

### Prerequisites
- Python 3.9+
- FFmpeg
- Docker

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## License

MIT License 