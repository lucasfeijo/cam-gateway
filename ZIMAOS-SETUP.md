# ZimaOS Setup Guide for CAM Gateway

## Quick Setup Reference

When adding the container in ZimaOS, use these settings:

### 🔧 **Basic Configuration**
- **Name**: `CAM Gateway`
- **Image**: `feijo/cam-gateway:latest`
- **Restart Policy**: `unless-stopped`

### 🌐 **Port Mappings**
```
8000:8000    # Web interface and API
554:554      # RTSP protocol
8001:8001    # ONVIF stream 1
8002:8002    # ONVIF stream 2
8003:8003    # ONVIF stream 3
8004:8004    # ONVIF stream 4
8005:8005    # ONVIF stream 5
8006:8006    # ONVIF stream 6
8007:8007    # ONVIF stream 7
8008:8008    # ONVIF stream 8
8009:8009    # ONVIF stream 9
8010:8010    # ONVIF stream 10
```

### 💾 **Volume Mappings**
```
/opt/zimaos/apps/cam-gateway/data:/app/data
```

### ⚙️ **Environment Variables**
```
DATABASE_URL=/app/data/streams.db
ONVIF_PORT=8000
RTSP_PORT=554
LOG_LEVEL=INFO
```

### 🔐 **Capabilities (Optional)**
```
SYS_ADMIN
NET_ADMIN
SYS_NICE
```

### 📊 **Resource Limits (Optional)**
- **Memory**: `1G`
- **CPU**: `2`

## Step-by-Step Setup

### 1. **Add Container in ZimaOS**
1. Go to ZimaOS Dashboard
2. Navigate to **Containers** or **Apps**
3. Click **"Add Container"** or **"Add App"**

### 2. **Enter Basic Info**
- **Container Name**: `cam-gateway`
- **Image**: `feijo/cam-gateway:latest`
- **Restart Policy**: `unless-stopped`

### 3. **Configure Port Mappings**
Add each port mapping:
- `8000:8000` (Web interface)
- `554:554` (RTSP)
- `8001:8001` through `8010:8010` (ONVIF streams)

### 4. **Configure Volume Mappings**
Add volume mapping:
- **Host Path**: `/opt/zimaos/apps/cam-gateway/data`
- **Container Path**: `/app/data`

### 5. **Add Environment Variables**
Add each environment variable:
- `DATABASE_URL=/app/data/streams.db`
- `ONVIF_PORT=8000`
- `RTSP_PORT=554`
- `LOG_LEVEL=INFO`

### 6. **Add Capabilities (Optional)**
If ZimaOS supports capabilities, add:
- `SYS_ADMIN`
- `NET_ADMIN`
- `SYS_NICE`

### 7. **Set Resource Limits (Optional)**
- **Memory Limit**: `1G`
- **CPU Limit**: `2`

### 8. **Deploy**
Click **"Deploy"** or **"Start Container"**

## Verification

### 1. **Check Container Status**
- Container should show as "Running"
- Check logs for any errors

### 2. **Access Web Interface**
- Open browser to: `http://your-zimaboard-ip:8000`
- Should see CAM Gateway interface

### 3. **Test API**
- Visit: `http://your-zimaboard-ip:8000/api/docs`
- Should see API documentation

### 4. **Add Test Stream**
- Use web interface to add a test RTSP stream
- Verify stream appears in list

## Troubleshooting

### **Container Won't Start**
- Check if ports are already in use
- Verify image name is correct: `feijo/cam-gateway:latest`
- Check ZimaOS logs for errors

### **Web Interface Not Accessible**
- Verify port 8000 is mapped correctly
- Check firewall settings
- Ensure container is running

### **FFmpeg Issues**
- Add capabilities: `SYS_ADMIN`, `NET_ADMIN`, `SYS_NICE`
- Check if FFmpeg is installed in container
- Verify RTSP URLs are accessible

## Access URLs

After deployment, access:
- **Web Interface**: `http://your-zimaboard-ip:8000`
- **API Docs**: `http://your-zimaboard-ip:8000/api/docs`
- **Health Check**: `http://your-zimaboard-ip:8000/health`
- **ONVIF Device**: `http://your-zimaboard-ip:8000/onvif/1/device.xml`

## Next Steps

1. **Add RTSP Streams** via web interface
2. **Configure UniFi Protect** to discover ONVIF devices
3. **Monitor Streams** through web interface
4. **Backup Configuration** using ZimaOS backup features 