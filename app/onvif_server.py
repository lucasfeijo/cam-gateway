import os
import logging
from typing import Dict, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import XMLResponse, PlainTextResponse
from sqlalchemy.orm import Session
from app.models import Stream
from app.database import get_db

logger = logging.getLogger(__name__)

class ONVIFServer:
    """ONVIF server implementation for stream proxy"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """Setup ONVIF routes"""
        
        @self.app.get("/onvif/{stream_id}/device.xml")
        async def device_xml(stream_id: int, request: Request):
            """ONVIF device XML endpoint"""
            return await self.get_device_xml(stream_id, request)
        
        @self.app.get("/onvif/{stream_id}/media.wsdl")
        async def media_wsdl(stream_id: int, request: Request):
            """ONVIF media WSDL endpoint"""
            return await self.get_media_wsdl(stream_id, request)
        
        @self.app.post("/onvif/{stream_id}/media")
        async def media_service(stream_id: int, request: Request):
            """ONVIF media service endpoint"""
            return await self.get_media_service(stream_id, request)
        
        @self.app.get("/onvif/{stream_id}/stream")
        async def stream_endpoint(stream_id: int, request: Request):
            """RTSP stream endpoint"""
            return await self.get_stream_endpoint(stream_id, request)
    
    async def get_device_xml(self, stream_id: int, request: Request) -> XMLResponse:
        """Generate ONVIF device XML"""
        db = next(get_db())
        stream = db.query(Stream).filter(Stream.id == stream_id).first()
        
        if not stream:
            return XMLResponse(content="<error>Stream not found</error>", status_code=404)
        
        host = request.headers.get("host", "localhost")
        base_url = f"http://{host}"
        
        device_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
    <soap:Header/>
    <soap:Body>
        <tds:GetDeviceInformationResponse>
            <tds:Manufacturer>CAM Gateway</tds:Manufacturer>
            <tds:Model>{stream.name}</tds:Model>
            <tds:FirmwareVersion>1.0.0</tds:FirmwareVersion>
            <tds:SerialNumber>CAM-{stream_id:04d}</tds:SerialNumber>
            <tds:HardwareId>CAM-Gateway-{stream_id}</tds:HardwareId>
        </tds:GetDeviceInformationResponse>
    </soap:Body>
</soap:Envelope>"""
        
        return XMLResponse(content=device_xml)
    
    async def get_media_wsdl(self, stream_id: int, request: Request) -> XMLResponse:
        """Generate ONVIF media WSDL"""
        host = request.headers.get("host", "localhost")
        base_url = f"http://{host}"
        
        media_wsdl = f"""<?xml version="1.0" encoding="UTF-8"?>
<definitions name="MediaService" targetNamespace="http://www.onvif.org/ver10/media/wsdl" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://schemas.xmlsoap.org/wsdl/" xmlns:tns="http://www.onvif.org/ver10/media/wsdl" xmlns:ter="http://www.onvif.org/ver10/error" xmlns:trt="http://www.onvif.org/ver10/media/wsdl">
    <types>
        <xsd:schema targetNamespace="http://www.onvif.org/ver10/media/wsdl">
            <xsd:element name="GetStreamUri">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="StreamSetup" type="trt:StreamSetup"/>
                        <xsd:element name="ProfileToken" type="xsd:token"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="GetStreamUriResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="MediaUri" type="trt:MediaUri"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>
    <message name="GetStreamUriRequest">
        <part name="parameters" element="tns:GetStreamUri"/>
    </message>
    <message name="GetStreamUriResponse">
        <part name="parameters" element="tns:GetStreamUriResponse"/>
    </message>
    <portType name="Media">
        <operation name="GetStreamUri">
            <input message="tns:GetStreamUriRequest"/>
            <output message="tns:GetStreamUriResponse"/>
        </operation>
    </portType>
    <binding name="MediaBinding" type="tns:Media">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="GetStreamUri">
            <soap:operation soapAction="http://www.onvif.org/ver10/media/wsdl/GetStreamUri"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
    </binding>
    <service name="Media">
        <port name="MediaPort" binding="tns:MediaBinding">
            <soap:address location="{base_url}/onvif/{stream_id}/media"/>
        </port>
    </service>
</definitions>"""
        
        return XMLResponse(content=media_wsdl)
    
    async def get_media_service(self, stream_id: int, request: Request) -> XMLResponse:
        """Handle ONVIF media service requests"""
        db = next(get_db())
        stream = db.query(Stream).filter(Stream.id == stream_id).first()
        
        if not stream:
            return XMLResponse(content="<error>Stream not found</error>", status_code=404)
        
        host = request.headers.get("host", "localhost")
        onvif_port = stream.onvif_port or (8001 + stream.id)
        
        # Parse SOAP request
        body = await request.body()
        body_text = body.decode('utf-8')
        
        if "GetStreamUri" in body_text:
            # Generate stream URI response
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:trt="http://www.onvif.org/ver10/media/wsdl">
    <soap:Header/>
    <soap:Body>
        <trt:GetStreamUriResponse>
            <trt:MediaUri>
                <tt:Uri>rtsp://{host.split(':')[0]}:{onvif_port}/stream</tt:Uri>
                <tt:InvalidAfterConnect>false</tt:InvalidAfterConnect>
                <tt:InvalidAfterReboot>false</tt:InvalidAfterReboot>
                <tt:Timeout>PT60S</tt:Timeout>
            </trt:MediaUri>
        </trt:GetStreamUriResponse>
    </soap:Body>
</soap:Envelope>"""
            
            return XMLResponse(content=response_xml)
        else:
            # Generic response for other operations
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    <soap:Header/>
    <soap:Body>
        <soap:Fault>
            <soap:Code>
                <soap:Value>soap:Sender</soap:Value>
            </soap:Code>
            <soap:Reason>
                <soap:Text>Operation not supported</soap:Text>
            </soap:Reason>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>"""
            
            return XMLResponse(content=response_xml, status_code=500)
    
    async def get_stream_endpoint(self, stream_id: int, request: Request) -> Response:
        """Handle RTSP stream requests"""
        db = next(get_db())
        stream = db.query(Stream).filter(Stream.id == stream_id).first()
        
        if not stream:
            return Response(content="Stream not found", status_code=404)
        
        # Redirect to the actual RTSP stream
        return Response(
            content=f"RTSP stream for {stream.name}",
            media_type="text/plain"
        ) 