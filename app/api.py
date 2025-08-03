from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models import Stream, StreamCreate, StreamUpdate, StreamResponse, StreamStatusResponse
from app.stream_manager import stream_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["streams"])

@router.get("/streams", response_model=List[StreamResponse])
async def get_streams(db: Session = Depends(get_db)):
    """Get all registered streams"""
    streams = db.query(Stream).all()
    return streams

@router.post("/streams", response_model=StreamResponse, status_code=status.HTTP_201_CREATED)
async def create_stream(stream_data: StreamCreate, db: Session = Depends(get_db)):
    """Create a new stream"""
    try:
        # Check if ONVIF port is already in use
        if stream_data.onvif_port:
            existing_stream = db.query(Stream).filter(Stream.onvif_port == stream_data.onvif_port).first()
            if existing_stream:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ONVIF port {stream_data.onvif_port} is already in use"
                )
        
        # Create new stream
        stream = Stream(**stream_data.dict())
        db.add(stream)
        db.commit()
        db.refresh(stream)
        
        # Start the stream if enabled
        if stream.enabled:
            success = await stream_manager.start_stream(stream)
            if not success:
                logger.warning(f"Failed to start stream {stream.id}")
        
        logger.info(f"Created stream: {stream.name} (ID: {stream.id})")
        return stream
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create stream"
        )

@router.get("/streams/{stream_id}", response_model=StreamResponse)
async def get_stream(stream_id: int, db: Session = Depends(get_db)):
    """Get a specific stream by ID"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    return stream

@router.put("/streams/{stream_id}", response_model=StreamResponse)
async def update_stream(stream_id: int, stream_data: StreamUpdate, db: Session = Depends(get_db)):
    """Update a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    try:
        # Check if ONVIF port is already in use by another stream
        if stream_data.onvif_port and stream_data.onvif_port != stream.onvif_port:
            existing_stream = db.query(Stream).filter(
                Stream.onvif_port == stream_data.onvif_port,
                Stream.id != stream_id
            ).first()
            if existing_stream:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ONVIF port {stream_data.onvif_port} is already in use"
                )
        
        # Update stream fields
        update_data = stream_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stream, field, value)
        
        db.commit()
        db.refresh(stream)
        
        # Restart stream if it was running
        if stream.enabled:
            await stream_manager.stop_stream(stream_id)
            await stream_manager.start_stream(stream)
        
        logger.info(f"Updated stream: {stream.name} (ID: {stream.id})")
        return stream
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stream {stream_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update stream"
        )

@router.delete("/streams/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stream(stream_id: int, db: Session = Depends(get_db)):
    """Delete a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    try:
        # Stop the stream if it's running
        await stream_manager.stop_stream(stream_id)
        
        # Delete the stream
        db.delete(stream)
        db.commit()
        
        logger.info(f"Deleted stream: {stream.name} (ID: {stream_id})")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting stream {stream_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete stream"
        )

@router.get("/streams/{stream_id}/status", response_model=StreamStatusResponse)
async def get_stream_status(stream_id: int, db: Session = Depends(get_db)):
    """Get the status of a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Get current status from stream manager
    status = await stream_manager.get_stream_status(stream_id)
    
    # Check stream health
    health_status = await stream_manager.check_stream_health(stream)
    
    # Update status in database
    await stream_manager.update_stream_status(db, stream_id, health_status)
    
    return StreamStatusResponse(
        stream_id=stream_id,
        status=health_status,
        last_check=stream.updated_at or stream.created_at,
        error_message=None
    )

@router.post("/streams/{stream_id}/start")
async def start_stream(stream_id: int, db: Session = Depends(get_db)):
    """Manually start a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    success = await stream_manager.start_stream(stream)
    if success:
        return {"message": f"Stream {stream_id} started successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start stream"
        )

@router.post("/streams/{stream_id}/stop")
async def stop_stream(stream_id: int, db: Session = Depends(get_db)):
    """Manually stop a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    success = await stream_manager.stop_stream(stream_id)
    if success:
        return {"message": f"Stream {stream_id} stopped successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop stream"
        )

@router.post("/streams/{stream_id}/restart")
async def restart_stream(stream_id: int, db: Session = Depends(get_db)):
    """Restart a stream"""
    stream = db.query(Stream).filter(Stream.id == stream_id).first()
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    success = await stream_manager.restart_stream(stream)
    if success:
        return {"message": f"Stream {stream_id} restarted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restart stream"
        ) 