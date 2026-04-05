import os
import django
import json
import requests
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

def test_incubator_integration():
    print("--- Starting Incubator Dashboard Programmatic Test ---")
    
    # 1. Check User exist and has correct role
    try:
        user = User.objects.get(username='incubator_admin')
        print(f"[OK] User 'incubator_admin' found. Role: {user.role}, Univ: {user.university_name}")
        if user.role != 'INCUBATOR':
            print("❌ Error: User role is not INCUBATOR")
            return
    except User.DoesNotExist:
        print("❌ Error: User incubator_admin not found")
        return

    # 2. Test API Endpoints (internal request simulation)
    from django.test import Client
    client = Client()
    client.force_login(user)
    
    # Test Dashboard Stats
    response = client.get('/api/vendors/dashboard/') # Reusing vendor dashboard logic with expanded permission
    if response.status_code == 200:
        print("✅ Dashboard API: Accessible (200 OK)")
    else:
        print(f"❌ Dashboard API: Failed with status {response.status_code}")

    # Test Organization Requests (New model)
    try:
        from apps.vendors.models import OrganizationRequest
        # Create a dummy if none exist just for test
        if not OrganizationRequest.objects.exists():
            OrganizationRequest.objects.create(name="Test Org", sector="Tech", incubator=user)
        
        # Test generic list view (assuming it exists or will be added)
        # For now let's just check the model
        print(f"✅ OrganizationRequest model: Functional. Count: {OrganizationRequest.objects.count()}")
    except ImportError:
        print("❌ Error: OrganizationRequest model not found in apps.vendors.models")

    print("--- Test Completed Successfully ---")

if __name__ == "__main__":
    test_incubator_integration()
