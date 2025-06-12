#!/usr/bin/env python3
import requests
import json

def test_chattts_api():
    print("Testing ChatTTS through API with detailed parameters...")
    
    # Test with more specific ChatTTS parameters
    test_params = {
        "text": "Hello, this is a test.",
        "model": "chat-tts",
        "spk": "female2",
        "style": "chat",
        "temperature": 0.3,
        "top_p": 0.7,
        "top_k": 20,
        "seed": 42,
        "format": "wav",
        "prompt": "[speed_5]",
        "stream": False
    }
    
    print("Testing GET /v1/tts with detailed parameters...")
    try:
        response = requests.get("http://localhost:7870/v1/tts", params=test_params, timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type:
                with open("detailed_api_test.wav", "wb") as f:
                    f.write(response.content)
                print(f"✓ Audio generated successfully! Size: {len(response.content)} bytes")
                return True
            else:
                print(f"Unexpected content type: {content_type}")
                print(f"Response content: {response.text[:500]}...")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Try with minimal parameters
    print("\nTesting with minimal parameters...")
    minimal_params = {
        "text": "Hello",
        "model": "chat-tts"
    }
    
    try:
        response = requests.get("http://localhost:7870/v1/tts", params=minimal_params, timeout=60)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        else:
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
    except Exception as e:
        print(f"Minimal request failed: {e}")
    
    return False

if __name__ == "__main__":
    test_chattts_api() 