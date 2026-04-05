import os, sys, django, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'c:\Users\sedrata laptops\Desktop\New folder (5)\algerian_marketplace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Category as ProdCat, Product
from apps.services.models import ServiceCategory, Service
from apps.vendors.models import Store, OrganizationRequest
from apps.users.models import User

test_keywords = ['test', 'demo', 'sample']
test_exact = ['electronics', 'tech services', 'test category', 'test cat v3', 'test cat v4', 'aa']
test_users = ['test_vendor', 'test_customer', 'test_institution']

def is_test(name):
    if not name: return False
    nameL = name.lower().strip()
    return any(k in nameL for k in test_keywords) or nameL in test_exact or nameL in test_users

print("=" * 50)
print("PURGING TEST DATA...")
print("=" * 50)

deleted = 0

# 1. Delete Products/Services/Categories
for p in Product.objects.all():
    if is_test(p.name):
        print(f"  DEL Product: {p.name}")
        p.delete(); deleted += 1

for s in Service.objects.all():
    if is_test(s.name):
        print(f"  DEL Service: {s.name}")
        s.delete(); deleted += 1

for c in ProdCat.objects.all():
    if is_test(c.name):
        print(f"  DEL Product Category: {c.name}")
        c.delete(); deleted += 1

for sc in ServiceCategory.objects.all():
    if is_test(sc.name):
        print(f"  DEL Service Category: {sc.name}")
        sc.delete(); deleted += 1

# 2. Delete Stores/OrgRequests
for st in Store.objects.all():
    if is_test(st.name) or is_test(st.vendor.username):
        print(f"  DEL Store: {st.name} (vendor: {st.vendor.username})")
        st.delete(); deleted += 1

for o in OrganizationRequest.objects.all():
    if is_test(o.name):
        print(f"  DEL OrgRequest: {o.name}")
        o.delete(); deleted += 1

# 3. Delete Users (Non-superusers only)
for u in User.objects.filter(is_superuser=False):
    if is_test(u.username) or is_test(u.first_name) or is_test(u.email):
        print(f"  DEL User: {u.username}")
        u.delete(); deleted += 1

print(f"\nTotal objects deleted: {deleted}")
print("Cleanup Complete.")
