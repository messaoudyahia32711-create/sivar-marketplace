import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.vendors.models import Store

username = 'institution_admin'
password = 'admin_pass_2024'

# التحقق من وجود المستخدم
if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(
        username=username, 
        password=password, 
        role='INSTITUTION', 
        phone_number='0550123456',
        is_verified=True
    )
    # إنشاء ملف تعريف (Store/Institution Profile) ليعمل الـ Dashboard
    Store.objects.create(
        vendor=user,
        name='مؤسسة البركة للخدمات',
        description='مؤسسة رائدة في تقديم الحلول المتكاملة.'
    )
    print(f"✅ تم إنشاء الحساب بنجاح.")
    print(f"Username: {username}")
    print(f"Password: {password}")
else:
    print("⚠️ الحساب موجود مسبقاً.")
