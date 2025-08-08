import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from app.database import create_tables, get_db
from app.api import router as api_router
from app.onvif_server import ONVIFServer
from app.models import Stream
from app.stream_manager import stream_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CAM Gateway",
    description="RTSP to ONVIF Proxy for UniFi Protect Integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Create database tables
create_tables()

# Include API routes
app.include_router(api_router)

# Initialize ONVIF server
onvif_server = ONVIFServer(app)

# Serve static files and templates
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")
except:
    # Static files not available in development
    pass

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main page with stream management interface"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CAM Gateway</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .api-links { margin: 20px 0; }
                .api-links a { display: inline-block; margin: 5px; padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>CAM Gateway</h1>
                    <p>RTSP to ONVIF Proxy for UniFi Protect Integration</p>
                </div>
                
                <div class="api-links">
                    <h2>API Documentation</h2>
                    <a href="/api/docs">Interactive API Docs</a>
                    <a href="/api/redoc">ReDoc Documentation</a>
                </div>
                
                <div>
                    <h2>Quick Start</h2>
                    <p>Use the API endpoints to manage your RTSP streams:</p>
                    <ul>
                        <li><strong>GET /api/streams</strong> - List all streams</li>
                        <li><strong>POST /api/streams</strong> - Add new stream</li>
                        <li><strong>GET /api/streams/{id}</strong> - Get stream details</li>
                        <li><strong>PUT /api/streams/{id}</strong> - Update stream</li>
                        <li><strong>DELETE /api/streams/{id}</strong> - Delete stream</li>
                    </ul>
                </div>
                
                <div>
                    <h2>ONVIF Endpoints</h2>
                    <p>Each registered stream will be available as an ONVIF device:</p>
                    <ul>
                        <li><strong>/onvif/{stream_id}/device.xml</strong> - Device information</li>
                        <li><strong>/onvif/{stream_id}/media.wsdl</strong> - Media service WSDL</li>
                        <li><strong>/onvif/{stream_id}/media</strong> - Media service endpoint</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cam-gateway"}

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("CAM Gateway starting up...")
    
    # Start all enabled streams
    try:
        db = next(get_db())
        enabled_streams = db.query(Stream).filter(Stream.enabled == True).all()
        
        for stream in enabled_streams:
            logger.info(f"Starting enabled stream: {stream.name} (ID: {stream.id})")
            success = await stream_manager.start_stream(stream)
            if success:
                logger.info(f"Stream {stream.id} started successfully")
            else:
                logger.error(f"Failed to start stream {stream.id}")
                
    except Exception as e:
        logger.error(f"Error starting streams: {str(e)}")
    
    logger.info("CAM Gateway started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("CAM Gateway shutting down...")
    
    # Cleanup tasks here
    logger.info("CAM Gateway shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 