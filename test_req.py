import urllib.request, json
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/users/register/',
    data=json.dumps({'username': 'testVendorSuperEasy', 'email': 'ez@x.com', 'password': '123', 'password2': '123', 'role': 'VENDOR', 'phone_number': '0666666666', 'entity_name': 'My Inst'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    res = urllib.request.urlopen(req)
    print(res.read())
except Exception as e:
    print(e.read())
