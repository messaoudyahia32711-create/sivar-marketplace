import os
import django

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

def verify_integration():
    print("--- Starting Programmatic Integration Check ---")
    client = APIClient()
    
    # Using the correct full path: /api/vendors/ + api/dashboard/
    API_URL = '/api/vendors/api/dashboard/'
    
    # 1. Institution Check
    inst_user = User.objects.filter(role='INSTITUTION').first()
    if inst_user:
        print(f"Checking Institution User: {inst_user.username}")
        client.force_authenticate(user=inst_user)
        try:
            response = client.get(API_URL) 
            if response.status_code == 200:
                print("SUCCESS: Institution can access dashboard API (200 OK)")
            else:
                print(f"FAILURE: Institution access denied - Status {response.status_code}")
                # print(f"DEBUG: {response.content}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    else:
        print("WARNING: No Institution user found for testing.")

    # 2. Vendor Check
    vendor_user = User.objects.filter(role='SELLER').first()
    if vendor_user:
        print(f"Checking Vendor User: {vendor_user.username}")
        client.force_authenticate(user=vendor_user)
        try:
            response = client.get(API_URL)
            if response.status_code == 200:
                print("SUCCESS: Vendor can access dashboard API (200 OK)")
            else:
                print(f"FAILURE: Vendor access denied - Status {response.status_code}")
        except Exception as e:
            print(f"ERROR: {str(e)}")

    print("\n--- Summary Check Completed ---")

if __name__ == "__main__":
    verify_integration()
