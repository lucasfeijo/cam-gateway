import asyncio
import subprocess
import logging
import os
from typing import Dict, Optional, List
from datetime import datetime
import ffmpeg
import requests
from sqlalchemy.orm import Session
from app.models import Stream, StreamStatus

logger = logging.getLogger(__name__)

class StreamManager:
    """Manages RTSP streams and ONVIF proxy functionality"""
    
    def __init__(self):
        self.active_streams: Dict[int, subprocess.Popen] = {}
        self.stream_status: Dict[int, str] = {}
        
    async def start_stream(self, stream: Stream) -> bool:
        """Start an RTSP stream and proxy it to ONVIF"""
        try:
            # Check if stream is already running
            if stream.id in self.active_streams:
                logger.warning(f"Stream {stream.id} is already running")
                return True
                
            # Build RTSP URL with credentials if provided
            rtsp_url = stream.rtsp_url
            if not rtsp_url.startswith("rtsp://"):
                rtsp_url = f"rtsp://{rtsp_url}"
                
            if stream.username and stream.password:
                # Insert credentials into RTSP URL
                if "://" in rtsp_url:
                    protocol, rest = rtsp_url.split("://", 1)
                    # Check if credentials are already in the URL
                    if "@" not in rest:
                        rtsp_url = f"{protocol}://{stream.username}:{stream.password}@{rest}"
            
            # Create ONVIF proxy endpoint
            onvif_port = stream.onvif_port or (8001 + stream.id)
            
            # Start FFmpeg process to proxy the stream
            cmd = [
                "ffmpeg",
                "-i", rtsp_url,
                "-c:v", "copy",  # Copy video codec without re-encoding
                "-c:a", "copy",  # Copy audio codec without re-encoding
                "-f", "rtsp",
                f"rtsp://0.0.0.0:{onvif_port}/stream"
            ]
            
            logger.info(f"Starting stream {stream.id} with RTSP URL: {rtsp_url}")
            logger.info(f"Starting stream {stream.id} with command: {' '.join(cmd)}")
            
            # Start the FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            # Wait a moment to see if the process starts successfully
            await asyncio.sleep(2)
            
            if process.poll() is None:
                self.active_streams[stream.id] = process
                self.stream_status[stream.id] = "online"
                logger.info(f"Stream {stream.id} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"Failed to start stream {stream.id}: {stderr.decode()}")
                self.stream_status[stream.id] = "error"
                return False
                
        except Exception as e:
            logger.error(f"Error starting stream {stream.id}: {str(e)}")
            self.stream_status[stream.id] = "error"
            return False
    
    async def stop_stream(self, stream_id: int) -> bool:
        """Stop an RTSP stream"""
        try:
            if stream_id in self.active_streams:
                process = self.active_streams[stream_id]
                process.terminate()
                await asyncio.sleep(1)
                
                if process.poll() is None:
                    process.kill()
                
                del self.active_streams[stream_id]
                self.stream_status[stream_id] = "offline"
                logger.info(f"Stream {stream_id} stopped successfully")
                return True
            else:
                logger.warning(f"Stream {stream_id} is not running")
                return True
                
        except Exception as e:
            logger.error(f"Error stopping stream {stream_id}: {str(e)}")
            return False
    
    async def check_stream_health(self, stream: Stream) -> str:
        """Check the health of an RTSP stream"""
        try:
            # Try to connect to the RTSP stream
            rtsp_url = stream.rtsp_url
            if stream.username and stream.password:
                if "://" in rtsp_url:
                    protocol, rest = rtsp_url.split("://", 1)
                    rtsp_url = f"{protocol}://{stream.username}:{stream.password}@{rest}"
            
            # Use FFprobe to check stream health
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                rtsp_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                return "online"
            else:
                return "offline"
                
        except subprocess.TimeoutExpired:
            return "timeout"
        except Exception as e:
            logger.error(f"Error checking stream health: {str(e)}")
            return "error"
    
    async def get_stream_status(self, stream_id: int) -> Optional[str]:
        """Get the current status of a stream"""
        return self.stream_status.get(stream_id, "unknown")
    
    async def get_all_stream_status(self) -> Dict[int, str]:
        """Get status of all streams"""
        return self.stream_status.copy()
    
    async def restart_stream(self, stream: Stream) -> bool:
        """Restart a stream"""
        await self.stop_stream(stream.id)
        await asyncio.sleep(1)
        return await self.start_stream(stream)
    
    async def update_stream_status(self, db: Session, stream_id: int, status: str, error_message: str = None):
        """Update stream status in database"""
        try:
            # Check if status record exists
            status_record = db.query(StreamStatus).filter(StreamStatus.stream_id == stream_id).first()
            
            if status_record:
                status_record.status = status
                status_record.last_check = datetime.utcnow()
                status_record.error_message = error_message
            else:
                status_record = StreamStatus(
                    stream_id=stream_id,
                    status=status,
                    error_message=error_message
                )
                db.add(status_record)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating stream status: {str(e)}")
            db.rollback()

# Global stream manager instance
stream_manager = StreamManager() 