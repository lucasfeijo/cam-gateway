#!/usr/bin/env python3
"""
Test script for CAM Gateway application
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoints"""
    print("Testing API documentation...")
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ API docs accessible")
            return True
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False

def test_stream_crud():
    """Test stream CRUD operations"""
    print("Testing stream CRUD operations...")
    
    # Test data
    test_stream = {
        "name": "Test Camera",
        "rtsp_url": "rtsp://192.168.1.100:554/test",
        "username": "test",
        "password": "test123",
        "enabled": True,
        "onvif_port": 8001
    }
    
    try:
        # Create stream
        print("  Creating test stream...")
        response = requests.post(f"{API_BASE}/streams", json=test_stream)
        if response.status_code == 201:
            stream_data = response.json()
            stream_id = stream_data["id"]
            print(f"  ✅ Stream created with ID: {stream_id}")
        else:
            print(f"  ❌ Failed to create stream: {response.status_code}")
            return False
        
        # Get stream
        print("  Getting stream...")
        response = requests.get(f"{API_BASE}/streams/{stream_id}")
        if response.status_code == 200:
            print("  ✅ Stream retrieved successfully")
        else:
            print(f"  ❌ Failed to get stream: {response.status_code}")
            return False
        
        # Update stream
        print("  Updating stream...")
        update_data = {"name": "Updated Test Camera"}
        response = requests.put(f"{API_BASE}/streams/{stream_id}", json=update_data)
        if response.status_code == 200:
            print("  ✅ Stream updated successfully")
        else:
            print(f"  ❌ Failed to update stream: {response.status_code}")
            return False
        
        # Get stream status
        print("  Getting stream status...")
        response = requests.get(f"{API_BASE}/streams/{stream_id}/status")
        if response.status_code == 200:
            print("  ✅ Stream status retrieved")
        else:
            print(f"  ❌ Failed to get stream status: {response.status_code}")
            return False
        
        # Delete stream
        print("  Deleting test stream...")
        response = requests.delete(f"{API_BASE}/streams/{stream_id}")
        if response.status_code == 204:
            print("  ✅ Stream deleted successfully")
        else:
            print(f"  ❌ Failed to delete stream: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ CRUD test error: {e}")
        return False

def test_onvif_endpoints():
    """Test ONVIF endpoints"""
    print("Testing ONVIF endpoints...")
    
    # Create a test stream first
    test_stream = {
        "name": "ONVIF Test Camera",
        "rtsp_url": "rtsp://192.168.1.100:554/test",
        "enabled": False,
        "onvif_port": 8002
    }
    
    try:
        # Create stream
        response = requests.post(f"{API_BASE}/streams", json=test_stream)
        if response.status_code != 201:
            print("  ❌ Failed to create test stream for ONVIF test")
            return False
        
        stream_id = response.json()["id"]
        
        # Test device.xml
        print("  Testing device.xml endpoint...")
        response = requests.get(f"{BASE_URL}/onvif/{stream_id}/device.xml")
        if response.status_code == 200:
            print("  ✅ Device XML endpoint working")
        else:
            print(f"  ❌ Device XML failed: {response.status_code}")
        
        # Test media.wsdl
        print("  Testing media.wsdl endpoint...")
        response = requests.get(f"{BASE_URL}/onvif/{stream_id}/media.wsdl")
        if response.status_code == 200:
            print("  ✅ Media WSDL endpoint working")
        else:
            print(f"  ❌ Media WSDL failed: {response.status_code}")
        
        # Clean up
        requests.delete(f"{API_BASE}/streams/{stream_id}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ONVIF test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting CAM Gateway tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("API Documentation", test_api_docs),
        ("Stream CRUD Operations", test_stream_crud),
        ("ONVIF Endpoints", test_onvif_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CAM Gateway is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 