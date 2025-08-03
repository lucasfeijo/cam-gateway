from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

Base = declarative_base()

class Stream(Base):
    """Database model for RTSP stream configuration"""
    __tablename__ = "streams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    rtsp_url = Column(String(500), nullable=False)
    username = Column(String(100), nullable=True)
    password = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=True)
    onvif_port = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StreamStatus(Base):
    """Database model for stream health status"""
    __tablename__ = "stream_status"
    
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)  # online, offline, error
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    error_message = Column(Text, nullable=True)

# Pydantic models for API
class StreamBase(BaseModel):
    name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    enabled: bool = True
    onvif_port: Optional[int] = None

class StreamCreate(StreamBase):
    pass

class StreamUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    enabled: Optional[bool] = None
    onvif_port: Optional[int] = None

class StreamResponse(StreamBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StreamStatusResponse(BaseModel):
    stream_id: int
    status: str
    last_check: datetime
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True 