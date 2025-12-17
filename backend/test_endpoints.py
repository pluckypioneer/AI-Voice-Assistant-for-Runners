import requests

print("Checking backend health...")
try:
    r = requests.get("http://localhost:8000/health")
    print(f"Health check: {r.status_code}")
except Exception as e:
    print(f"Backend not running: {e}")
    exit(1)

print("\nChecking POST /api/v1/runs/save...")
try:
    # We expect 422 because we aren't sending a body, but 404 means it doesn't exist.
    r = requests.post("http://localhost:8000/api/v1/runs/save", json={})
    print(f"Status: {r.status_code}")
    if r.status_code == 404:
        print("❌ Endpoint NOT FOUND")
    elif r.status_code == 422:
        print("✅ Endpoint EXISTS (Validation Error as expected)")
    else:
        print(f"✅ Endpoint EXISTS (Status: {r.status_code})")
except Exception as e:
    print(f"Error: {e}")
