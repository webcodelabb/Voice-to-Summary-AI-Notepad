#!/usr/bin/env python3
"""
Simple test script for Voice-to-Summary AI Notepad Backend 
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")

def test_summarize_endpoint():
    """Test the summarize endpoint"""
    print("\n📝 Testing summarize endpoint...")
    try:
        test_text = """
        This is a test transcript for the Voice-to-Summary AI Notepad backend. 
        The system should be able to process this text and generate a meaningful summary. 
        The summary should highlight the key points and provide a concise overview of the content.
        """
        
        payload = {
            "text": test_text,
            "max_length": 50,
            "style": "bullet_points"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/summarize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Summarize endpoint passed")
            result = response.json()
            print(f"   Summary: {result.get('summary', 'N/A')}")
            print(f"   Word count: {result.get('word_count', 'N/A')}")
        else:
            print(f"❌ Summarize endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Summarize endpoint error: {str(e)}")

def test_transcribe_status():
    """Test the transcribe status endpoint"""
    print("\n🎤 Testing transcribe status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/transcribe/status")
        if response.status_code == 200:
            print("✅ Transcribe status passed")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Transcribe status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Transcribe status error: {str(e)}")

def test_summarize_status():
    """Test the summarize status endpoint"""
    print("\n🧠 Testing summarize status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/summarize/status")
        if response.status_code == 200:
            print("✅ Summarize status passed")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Summarize status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Summarize status error: {str(e)}")

def main():
    """Run all tests"""
    print("🧪 Testing Voice-to-Summary AI Notepad Backend")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first:")
            print("   python start.py")
            return
    except:
        print("❌ Server is not running. Please start the server first:")
        print("   python start.py")
        return
    
    # Run tests
    test_health_check()
    test_root_endpoint()
    test_summarize_endpoint()
    test_transcribe_status()
    test_summarize_status()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 
