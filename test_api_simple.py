#!/usr/bin/env python3
import requests
import json

def test_api():
    print("Testing Speech-AI-Forge API...")
    
    # Test basic connectivity
    try:
        response = requests.get("http://localhost:7870/docs", timeout=5)
        if response.status_code == 200:
            print("✓ API server is running")
        else:
            print(f"✗ API server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        return False
    
    # Test TTS endpoint with different approaches
    test_text = "Hello, this is a test."
    
    # Method 1: GET request with query parameters
    print("\n--- Testing GET /v1/tts ---")
    try:
        params = {
            "text": test_text,
            "model": "chat-tts",
            "format": "wav"
        }
        response = requests.get("http://localhost:7870/v1/tts", params=params, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and 'audio' in response.headers.get('content-type', ''):
            with open("api_test_output.wav", "wb") as f:
                f.write(response.content)
            print("✓ Audio saved to api_test_output.wav")
            return True
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"✗ GET request failed: {e}")
    
    # Method 2: POST request to /v2/tts
    print("\n--- Testing POST /v2/tts ---")
    try:
        data = {
            "text": test_text,
            "model": "chat-tts",
            "format": "wav"
        }
        response = requests.post("http://localhost:7870/v2/tts", json=data, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and 'audio' in response.headers.get('content-type', ''):
            with open("api_test_output_v2.wav", "wb") as f:
                f.write(response.content)
            print("✓ Audio saved to api_test_output_v2.wav")
            return True
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"✗ POST request failed: {e}")
    
    # Method 3: List available models
    print("\n--- Testing GET /v1/models/list ---")
    try:
        response = requests.get("http://localhost:7870/v1/models/list", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"Available models: {models}")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"✗ Models list request failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n✓ API test successful!")
    else:
        print("\n✗ API test failed!") 