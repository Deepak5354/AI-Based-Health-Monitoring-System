"""
Simple test script to verify the API is working
Run this after starting the Flask server
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_conversation_flow():
    """Test complete conversation flow"""
    print("Testing conversation flow...\n")
    
    # 1. Start conversation
    print("1. Starting conversation...")
    response = requests.post(f"{BASE_URL}/api/conversation/start", json={})
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    
    data = response.json()
    conversation_id = data["conversation_id"]
    print(f"   Conversation ID: {conversation_id}\n")
    
    # 2. Set age
    print("2. Setting age...")
    response = requests.post(
        f"{BASE_URL}/api/conversation/{conversation_id}/age",
        json={"age": "18-64 years (Adult)"}
    )
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    print(f"   {response.json()['message']}\n")
    
    # 3. Set language
    print("3. Setting language...")
    response = requests.post(
        f"{BASE_URL}/api/conversation/{conversation_id}/language",
        json={"language": "english"}
    )
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    print(f"   {response.json()['message']}\n")
    
    # 4. Send chat message
    print("4. Sending chat message...")
    response = requests.post(
        f"{BASE_URL}/api/conversation/{conversation_id}/chat",
        json={"message": "I have a mild fever and headache"}
    )
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    
    result = response.json()
    print("   Response received:")
    print(f"   Summary: {result['response']['summary'][:100]}...")
    print(f"   Home Care: {result['response']['home_care'][:100]}...")
    print()
    
    # 5. Check status
    print("5. Checking conversation status...")
    response = requests.get(f"{BASE_URL}/api/conversation/{conversation_id}/status")
    if response.status_code == 200:
        print(f"   Status: {response.json()}\n")
    
    print("✅ All tests passed!")

def test_config_endpoints():
    """Test configuration endpoints"""
    print("\nTesting configuration endpoints...\n")
    
    endpoints = [
        "/api/config/age-groups",
        "/api/config/languages",
        "/api/config/llm-providers"
    ]
    
    for endpoint in endpoints:
        print(f"Testing {endpoint}...")
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            print(f"   ✅ Success")
        else:
            print(f"   ❌ Error: {response.json()}")
        print()

if __name__ == "__main__":
    try:
        test_health()
        test_config_endpoints()
        test_conversation_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("   Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

