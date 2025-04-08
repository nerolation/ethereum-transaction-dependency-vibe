#!/usr/bin/env python3
import requests
import sys

def check_backend():
    try:
        response = requests.get('http://localhost:5000/api/status')
        if response.status_code == 200:
            print("✅ Backend is running at http://localhost:5000/api/status")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to backend at http://localhost:5000/api/status")
        print("Backend server is not running or is not accessible.")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_backend()
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Make sure your backend server is running (python app.py in the backend directory)")
        print("2. Check if there are any error messages when starting the backend")
        print("3. Verify that port 5000 is not being used by another application")
        print("4. Ensure your Google credentials are properly set up")
        sys.exit(1)
    sys.exit(0) 